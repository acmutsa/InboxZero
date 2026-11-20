"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiError, createApiClient, toApiError, type ApiClient } from "./api";

// The backend verifies HS256 tokens with an `aud` claim, which Clerk's default
// session token doesn't have, so requests use a Clerk JWT template instead.
const JWT_TEMPLATE = process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || undefined;

/** API client bound to the signed-in user's Clerk session token. */
export function useApi(): ApiClient {
  const { getToken } = useAuth();
  return useMemo(() => createApiClient(() => getToken({ template: JWT_TEMPLATE })), [getToken]);
}

interface QueryResult<T> {
  /** Identifies which request (key + reload count) this result belongs to. */
  requestId: string | null;
  key: string | null;
  data: T | null;
  error: ApiError | null;
}

/**
 * Loads data from the API when `key` is set and reloads when it changes.
 * Pass `null` as the key to skip loading (e.g. until an account is selected).
 */
export function useApiQuery<T>(key: string | null, fetcher: (api: ApiClient) => Promise<T>) {
  const api = useApi();
  // getToken() returns null until Clerk has loaded, so hold requests until then.
  const { isLoaded } = useAuth();
  const [version, setVersion] = useState(0);
  const [result, setResult] = useState<QueryResult<T>>({
    requestId: null,
    key: null,
    data: null,
    error: null,
  });

  // Keep the latest fetcher without making it an effect dependency, so
  // callers can pass inline functions without triggering refetch loops.
  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const requestId = key === null || !isLoaded ? null : `${key}#${version}`;

  useEffect(() => {
    if (requestId === null) return;
    let cancelled = false;

    fetcherRef.current(api).then(
      (data) => !cancelled && setResult({ requestId, key, data, error: null }),
      (error) =>
        !cancelled && setResult({ requestId, key, data: null, error: toApiError(error) }),
    );

    return () => {
      cancelled = true;
    };
  }, [api, key, requestId]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  // On reload (same key) keep showing the previous data until the new
  // response arrives; on a key change, drop it immediately.
  const isSameKey = key !== null && result.key === key;

  return {
    data: isSameKey ? result.data : null,
    error: isSameKey ? result.error : null,
    isLoading: requestId !== null && result.requestId !== requestId,
    reload,
  };
}

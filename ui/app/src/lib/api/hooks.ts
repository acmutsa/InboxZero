"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { env } from "@/lib/env";

import { ApiError, createApiClient, toApiError, type ApiClient } from "./api";

const JWT_TEMPLATE = env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE;

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

export type ApiQuery<T> = ReturnType<typeof useApiQuery<T>>;

type RegistrationStatus = "loading" | "registered" | "unregistered" | "error";

/**
 * Loads the backend user for the signed-in Clerk user. The backend answers
 * 404 until they've registered, which shows up here as "unregistered".
 */
export function useRegistration() {
  const user = useApiQuery("user", (client) => client.getCurrentUser());
  let status: RegistrationStatus = "loading";
  if (user.data) status = "registered";
  else if (user.error?.status === 404) status = "unregistered";
  else if (user.error) status = "error";
  return { ...user, status };
}

import { z } from "zod";

import { env } from "@/lib/env";
import {
  AuthorizationUrlSchema,
  CategoryStatsResponseSchema,
  ConnectGmailRequestSchema,
  ConnectOutlookRequestSchema,
  CreateUserRequestSchema,
  DraftStatsResponseSchema,
  EmailAccountListSchema,
  EmailAccountSchema,
  ErrorResponseSchema,
  GmailCallbackRequestSchema,
  GmailCallbackResponseSchema,
  OutlookCallbackRequestSchema,
  OutlookCallbackResponseSchema,
  UpdateUserRequestSchema,
  UserSchema,
  type ConnectGmailRequest,
  type ConnectOutlookRequest,
  type CreateUserRequest,
  type GmailCallbackRequest,
  type OutlookCallbackRequest,
  type UpdateUserRequest,
} from "./types";

/** Returns the current Clerk session token, or null when signed out. */
export type GetToken = () => Promise<string | null>;

export class ApiError extends Error {
  /** HTTP status code, or 0 when the server could not be reached. */
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const parsed = ErrorResponseSchema.safeParse(await response.json());
    if (parsed.success) {
      const { detail } = parsed.data;
      return typeof detail === "string" ? detail : detail.map((item) => item.msg).join(", ");
    }
  } catch {
    // Body was empty or not JSON; fall through to the status text.
  }
  return response.statusText || `Request failed with status ${response.status}`;
}

async function request<T>(
  getToken: GetToken,
  method: HttpMethod,
  path: string,
  responseSchema: z.ZodType<T> | null,
  body?: unknown,
): Promise<T> {
  const token = await getToken();
  if (!token) throw new ApiError(401, "You are not signed in.");

  const headers: HeadersInit = { Authorization: `Bearer ${token}` };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response: Response;
  try {
    response = await fetch(`${env.NEXT_PUBLIC_API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Could not reach the server. Please try again.");
  }

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response));
  }

  if (responseSchema === null) return undefined as T;

  const parsed = responseSchema.safeParse(await response.json());
  if (!parsed.success) {
    console.error(`Unexpected response from ${method} ${path}`, parsed.error);
    throw new ApiError(response.status, "The server sent an unexpected response.");
  }
  return parsed.data;
}

/** Validates a request body, turning Zod errors into a readable ApiError. */
function validate<T>(schema: z.ZodType<T>, body: unknown): T {
  const parsed = schema.safeParse(body);
  if (!parsed.success) {
    throw new ApiError(422, parsed.error.issues.map((issue) => issue.message).join(", "));
  }
  return parsed.data;
}

export function createApiClient(getToken: GetToken) {
  const get = <T>(path: string, schema: z.ZodType<T>) =>
    request(getToken, "GET", path, schema);
  const post = <T>(path: string, schema: z.ZodType<T>, body: unknown) =>
    request(getToken, "POST", path, schema, body);
  const patch = <T>(path: string, schema: z.ZodType<T>, body: unknown) =>
    request(getToken, "PATCH", path, schema, body);
  const del = (path: string) => request<void>(getToken, "DELETE", path, null);
  const id = (value: string) => encodeURIComponent(value);

  return {
    // Users
    createUser: async (body: CreateUserRequest) =>
      post("/api/users/create", UserSchema, validate(CreateUserRequestSchema, body)),
    getCurrentUser: () => get("/api/users/find", UserSchema),
    updateUser: async (body: UpdateUserRequest) =>
      patch("/api/users/update", UserSchema, validate(UpdateUserRequestSchema, body)),
    deleteUser: () => del("/api/users/delete"),

    // Email accounts
    getEmailAccounts: () => get("/api/email-accounts/find-all", EmailAccountListSchema),
    getEmailAccount: (accountId: string) =>
      get(`/api/email-accounts/find/${id(accountId)}`, EmailAccountSchema),
    disconnectEmailAccount: (accountId: string) =>
      del(`/api/email-accounts/disconnect/${id(accountId)}`),

    // Gmail connection
    connectGmail: async (body: ConnectGmailRequest) =>
      post(
        "/auth/google/connect-gmail",
        AuthorizationUrlSchema,
        validate(ConnectGmailRequestSchema, body),
      ),
    completeGmailConnection: async (body: GmailCallbackRequest) =>
      post(
        "/auth/google/callback",
        GmailCallbackResponseSchema,
        validate(GmailCallbackRequestSchema, body),
      ),

    // Outlook connection
    connectOutlook: async (body: ConnectOutlookRequest) =>
      post(
        "/auth/outlook/connect-outlook",
        AuthorizationUrlSchema,
        validate(ConnectOutlookRequestSchema, body),
      ),
    completeOutlookConnection: async (body: OutlookCallbackRequest) =>
      post(
        "/auth/outlook/callback",
        OutlookCallbackResponseSchema,
        validate(OutlookCallbackRequestSchema, body),
      ),

    // Stats
    getCategoryStats: (accountId: string) =>
      get(
        `/api/email-accounts/${id(accountId)}/stats/categories`,
        CategoryStatsResponseSchema,
      ),
    getDraftStats: (accountId: string) =>
      get(`/api/email-accounts/${id(accountId)}/stats/drafts`, DraftStatsResponseSchema),
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  return new ApiError(0, error instanceof Error ? error.message : "Something went wrong.");
}

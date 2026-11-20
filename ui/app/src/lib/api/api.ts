import type {
  AuthorizationUrl,
  CategoryStatsResponse,
  ConnectGmailRequest,
  CreateUserRequest,
  DraftStatsResponse,
  EmailAccount,
  ErrorResponse,
  GmailCallbackRequest,
  GmailCallbackResponse,
  UpdateUserRequest,
  User,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
    const { detail } = (await response.json()) as ErrorResponse;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
  } catch {
    // Body was empty or not JSON; fall through to the status text.
  }
  return response.statusText || `Request failed with status ${response.status}`;
}

async function request<T>(
  getToken: GetToken,
  method: HttpMethod,
  path: string,
  body?: unknown,
): Promise<T> {
  const token = await getToken();
  if (!token) throw new ApiError(401, "You are not signed in.");

  const headers: HeadersInit = { Authorization: `Bearer ${token}` };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
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

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function createApiClient(getToken: GetToken) {
  const get = <T>(path: string) => request<T>(getToken, "GET", path);
  const post = <T>(path: string, body: unknown) => request<T>(getToken, "POST", path, body);
  const patch = <T>(path: string, body: unknown) => request<T>(getToken, "PATCH", path, body);
  const del = <T>(path: string) => request<T>(getToken, "DELETE", path);
  const id = (value: string) => encodeURIComponent(value);

  return {
    // Users
    createUser: (body: CreateUserRequest) => post<User>("/api/users/create", body),
    getCurrentUser: () => get<User>("/api/users/find"),
    updateUser: (body: UpdateUserRequest) => patch<User>("/api/users/update", body),
    deleteUser: () => del<void>("/api/users/delete"),

    // Email accounts
    getEmailAccounts: () => get<EmailAccount[]>("/api/email-accounts/find-all"),
    getEmailAccount: (accountId: string) =>
      get<EmailAccount>(`/api/email-accounts/find/${id(accountId)}`),
    disconnectEmailAccount: (accountId: string) =>
      del<void>(`/api/email-accounts/disconnect/${id(accountId)}`),

    // Gmail connection
    connectGmail: (body: ConnectGmailRequest) =>
      post<AuthorizationUrl>("/auth/google/connect-gmail", body),
    completeGmailConnection: (body: GmailCallbackRequest) =>
      post<GmailCallbackResponse>("/auth/google/callback", body),

    // Stats
    getCategoryStats: (accountId: string) =>
      get<CategoryStatsResponse>(`/api/email-accounts/${id(accountId)}/stats/categories`),
    getDraftStats: (accountId: string) =>
      get<DraftStatsResponse>(`/api/email-accounts/${id(accountId)}/stats/drafts`),
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  return new ApiError(0, error instanceof Error ? error.message : "Something went wrong.");
}

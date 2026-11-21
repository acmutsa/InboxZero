// Request/response bodies for the FastAPI backend.
// Keep these in sync with the Pydantic schemas in api/app/models.

// Users

/** RegisterUserRequest */
export interface CreateUserRequest {
  first_name: string | null;
  last_name: string | null;
}

/** UpdateUserRequest */
export interface UpdateUserRequest {
  first_name: string | null;
  last_name: string | null;
}

/** UserResponse */
export interface User {
  id: string; // UUID
  first_name: string | null;
  last_name: string | null;
  created_at: string; // ISO 8601
}

// Email accounts

/** EmailServiceProvider */
export type EmailProvider = "gmail" | "outlook";

/** EmailAccountResponse */
export interface EmailAccount {
  id: string; // UUID
  email_account: string;
  provider: EmailProvider;
  created_at: string; // ISO 8601
  gmail_history_id: string | null;
  gmail_watch_expires_at: string | null; // ISO 8601
}

// Gmail connection (api/app/email_service/gmail/router.py)

/** ConnectGmailRequest */
export interface ConnectGmailRequest {
  gmail: string;
}

/** AuthorizationUrl */
export interface AuthorizationUrl {
  authorization_url: string;
}

/** GmailCallbackRequest */
export interface GmailCallbackRequest {
  code: string;
  state: string;
}

export interface GmailCallbackResponse {
  email: string;
  connected: boolean;
}

// Stats
// The stats endpoints are still placeholders that return a status message,
// not real counts. Replace these once the backend defines response models.

export type CategoryStatsResponse = Record<string, string>;
export type DraftStatsResponse = Record<string, string>;

// Errors

// FastAPI returns `detail` as a string for HTTPException and as a list
// of these for request validation (422) errors.
export interface ValidationErrorItem {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  detail: string | ValidationErrorItem[];
}

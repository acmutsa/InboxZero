import { z } from "zod";

// Request/response bodies for the FastAPI backend.
// Keep these in sync with the Pydantic schemas in api/app/models.
// Requests are validated before they're sent and responses when they arrive.

// Users

/** RegisterUserRequest */
export const CreateUserRequestSchema = z.object({
  first_name: z.string().trim().min(1).max(80).nullable(),
  last_name: z.string().trim().min(1).max(80).nullable(),
});
export type CreateUserRequest = z.infer<typeof CreateUserRequestSchema>;

/** UpdateUserRequest */
export const UpdateUserRequestSchema = CreateUserRequestSchema;
export type UpdateUserRequest = z.infer<typeof UpdateUserRequestSchema>;

/** UserResponse */
export const UserSchema = z.object({
  id: z.uuid(),
  first_name: z.string().nullable(),
  last_name: z.string().nullable(),
  created_at: z.string(), // ISO 8601
});
export type User = z.infer<typeof UserSchema>;

// Email accounts

/** EmailServiceProvider */
export const EmailProviderSchema = z.enum(["gmail", "outlook"]);
export type EmailProvider = z.infer<typeof EmailProviderSchema>;

/** EmailAccountResponse */
export const EmailAccountSchema = z.object({
  id: z.uuid(),
  email_account: z.string(),
  provider: EmailProviderSchema,
  created_at: z.string(), // ISO 8601
  gmail_history_id: z.string().nullable(),
  gmail_watch_expires_at: z.string().nullable(), // ISO 8601
});
export type EmailAccount = z.infer<typeof EmailAccountSchema>;

export const EmailAccountListSchema = z.array(EmailAccountSchema);

// Gmail connection (api/app/email_service/gmail/router.py)

/** ConnectGmailRequest */
export const ConnectGmailRequestSchema = z.object({
  gmail: z.email("Enter a valid email address."),
});
export type ConnectGmailRequest = z.infer<typeof ConnectGmailRequestSchema>;

/** AuthorizationUrl */
export const AuthorizationUrlSchema = z.object({
  authorization_url: z.url(),
});
export type AuthorizationUrl = z.infer<typeof AuthorizationUrlSchema>;

/** GmailCallbackRequest */
export const GmailCallbackRequestSchema = z.object({
  code: z.string().min(1),
  state: z.string().min(1),
});
export type GmailCallbackRequest = z.infer<typeof GmailCallbackRequestSchema>;

export const GmailCallbackResponseSchema = z.object({
  email: z.string(),
  connected: z.boolean(),
});
export type GmailCallbackResponse = z.infer<typeof GmailCallbackResponseSchema>;

// Outlook connection (api/app/email_service/outlook/router.py)
export const ConnectOutlookRequestSchema = z.object({
  outlook: z.email("Enter a valid email address."),
});
export type ConnectOutlookRequest = z.infer<typeof ConnectOutlookRequestSchema>;

export const OutlookCallbackRequestSchema = z.object({
  code: z.string().min(1),
  state: z.string().min(1),
});
export type OutlookCallbackRequest = z.infer<typeof OutlookCallbackRequestSchema>;

export const OutlookCallbackResponseSchema = z.object({
  email: z.string(),
  connected: z.boolean(),
});
export type OutlookCallbackResponse = z.infer<typeof OutlookCallbackResponseSchema>;

// Stats (api/app/repositories/stats.py)

export const CategoryStatsResponseSchema = z.array(
  z.object({
    category: z.string(),
    count: z.number().int().nonnegative(),
  }),
);
export type CategoryStatsResponse = z.infer<typeof CategoryStatsResponseSchema>;

export const DraftStatsResponseSchema = z.object({
  drafts: z.number().int().nonnegative(),
});
export type DraftStatsResponse = z.infer<typeof DraftStatsResponseSchema>;

// Errors

// FastAPI returns `detail` as a string for HTTPException and as a list
// of these for request validation (422) errors.
export const ValidationErrorItemSchema = z.object({
  loc: z.array(z.union([z.string(), z.number()])),
  msg: z.string(),
  type: z.string(),
});
export type ValidationErrorItem = z.infer<typeof ValidationErrorItemSchema>;

export const ErrorResponseSchema = z.object({
  detail: z.union([z.string(), z.array(ValidationErrorItemSchema)]),
});
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

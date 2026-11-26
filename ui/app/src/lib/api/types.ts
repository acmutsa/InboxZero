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

// Inbox (api/app/models/email_response.py, draft_response.py, update_draft_request.py)

/** EmailResponse */
export const EmailSchema = z.object({
  id: z.uuid(),
  email_account_id: z.uuid(),
  from_address: z.string(),
  subject: z.string().nullable(),
  body: z.string().nullable(),
  category: z.string().nullable(),
  created_at: z.string(), // ISO 8601
});
export type Email = z.infer<typeof EmailSchema>;

export const EmailListSchema = z.array(EmailSchema);

/** DraftStatus */
export const DraftStatusSchema = z.enum(["in_review", "sent"]);
export type DraftStatus = z.infer<typeof DraftStatusSchema>;

/** DraftResponse */
export const DraftSchema = z.object({
  id: z.uuid(),
  email_account_id: z.uuid(),
  reply_to_email: z.uuid().nullable(),
  to_address: z.string(),
  subject: z.string().nullable(),
  body: z.string().nullable(),
  status: DraftStatusSchema,
  created_at: z.string(), // ISO 8601
  updated_at: z.string(), // ISO 8601
});
export type Draft = z.infer<typeof DraftSchema>;

export const DraftListSchema = z.array(DraftSchema);

/** UpdateDraftRequest */
export const UpdateDraftRequestSchema = z.object({
  body: z.string().trim().min(1, "The reply can't be empty.").optional(),
  status: DraftStatusSchema.optional(),
});
export type UpdateDraftRequest = z.infer<typeof UpdateDraftRequestSchema>;

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

import { z } from "zod";

const envSchema = z.object({
  // Paths are appended to this, so drop any trailing slash.
  NEXT_PUBLIC_API_URL: z
    .url({ protocol: /^https?$/ })
    .transform((url) => url.replace(/\/+$/, ""))
    .default("http://localhost:8000"),
  // The backend verifies HS256 tokens with an `aud` claim, which Clerk's
  // default session token doesn't have, so requests use a Clerk JWT template.
  NEXT_PUBLIC_CLERK_JWT_TEMPLATE: z.string().min(1).default("inboxzero-api"),
});

// Next.js only inlines NEXT_PUBLIC_* variables that are referenced by their
// full name, so list each one here. Empty strings fall back to the defaults.
export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || undefined,
  NEXT_PUBLIC_CLERK_JWT_TEMPLATE: process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || undefined,
});

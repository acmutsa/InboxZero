"use client";

import { SignOutButton, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toApiError } from "@/lib/api/api";
import { useApi, useApiQuery } from "@/lib/api/hooks";

export default function ProfilePage() {
  const router = useRouter();
  const api = useApi();
  const { isLoaded, user } = useUser();
  const [disconnectError, setDisconnectError] = useState("");

  const profile = useApiQuery("user", (client) => client.getCurrentUser());
  const accounts = useApiQuery(profile.data ? "email-accounts" : null, (client) =>
    client.getEmailAccounts(),
  );

  // The backend answers 404 until the Clerk user has registered.
  const notRegistered = profile.error?.status === 404;
  useEffect(() => {
    if (notRegistered) router.replace("/registration");
  }, [notRegistered, router]);

  async function disconnect(accountId: string) {
    setDisconnectError("");
    try {
      await api.disconnectEmailAccount(accountId);
    } catch (caught) {
      setDisconnectError(toApiError(caught).message);
    }
    accounts.reload();
  }

  if (!isLoaded || !profile.data) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#030711] text-white">
        {profile.error && !notRegistered ? (
          <>
            <p>{profile.error.message}</p>
            <button
              onClick={profile.reload}
              className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100"
            >
              Try again
            </button>
          </>
        ) : (
          "Loading..."
        )}
      </div>
    );
  }

  const fullName = [profile.data.first_name, profile.data.last_name]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-[#030711] px-6 text-white">
      <h1 className="text-2xl font-semibold">Profile</h1>
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-sm">
        <p>
          <span className="text-slate-400">User ID:</span> {profile.data.id}
        </p>
        <p>
          <span className="text-slate-400">Email:</span>{" "}
          {user?.primaryEmailAddress?.emailAddress ?? "—"}
        </p>
        <p>
          <span className="text-slate-400">Name:</span> {fullName || "—"}
        </p>
      </div>
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-sm">
        <h2 className="mb-3 font-semibold">Email accounts</h2>
        {accounts.error ? (
          <p>{accounts.error.message}</p>
        ) : !accounts.data ? (
          <p className="text-slate-400">Loading...</p>
        ) : accounts.data.length === 0 ? (
          <p className="text-slate-400">No email accounts connected yet.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {accounts.data.map((account) => (
              <li key={account.id} className="flex items-center justify-between gap-4">
                <span>
                  {account.email_account}{" "}
                  <span className="text-slate-400">({account.provider})</span>
                </span>
                <button
                  onClick={() => void disconnect(account.id)}
                  className="text-slate-400 transition-colors hover:text-white"
                >
                  Disconnect
                </button>
              </li>
            ))}
          </ul>
        )}
        {disconnectError && <p role="alert" className="mt-3">{disconnectError}</p>}
      </div>
      <SignOutButton>
        <button className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100">
          Sign out
        </button>
      </SignOutButton>
    </div>
  );
}

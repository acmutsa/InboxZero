"use client";

import { SignOutButton, useUser } from "@clerk/nextjs";

export default function ProfilePage() {
  const { isLoaded, user } = useUser();

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#030711] text-white">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-[#030711] px-6 text-white">
      <h1 className="text-2xl font-semibold">Profile</h1>
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6 text-sm">
        <p>
          <span className="text-slate-400">User ID:</span> {user?.id}
        </p>
        <p>
          <span className="text-slate-400">Email:</span>{" "}
          {user?.primaryEmailAddress?.emailAddress ?? "—"}
        </p>
        <p>
          <span className="text-slate-400">Name:</span> {user?.fullName ?? "—"}
        </p>
      </div>
      <SignOutButton>
        <button className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100">
          Sign out
        </button>
      </SignOutButton>
    </div>
  );
}

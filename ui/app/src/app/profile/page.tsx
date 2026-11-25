"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import ProfileDashboard from "@/components/profile/ProfileDashboard";
import { useApiQuery, useRegistration } from "@/lib/api/hooks";

export default function ProfilePage() {
  const router = useRouter();
  const registration = useRegistration();
  // Loaded alongside the user rather than after it, so the dashboard's
  // account cards and stats don't wait an extra round trip.
  const emailAccounts = useApiQuery("email-accounts", (client) => client.getEmailAccounts());

  const unregistered = registration.status === "unregistered";
  useEffect(() => {
    if (unregistered) router.replace("/registration");
  }, [unregistered, router]);

  if (registration.data) {
    return <ProfileDashboard user={registration.data} emailAccounts={emailAccounts} />;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#030711] text-white">
      {registration.status === "error" ? (
        <>
          <p>{registration.error?.message}</p>
          <button
            onClick={registration.reload}
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

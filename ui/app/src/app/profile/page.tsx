"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import ProfileDashboard from "@/components/profile/ProfileDashboard";
import { useApiQuery } from "@/lib/api/hooks";

export default function ProfilePage() {
  const router = useRouter();
  const profile = useApiQuery("user", (client) => client.getCurrentUser());

  // The backend answers 404 until the Clerk user has registered.
  const notRegistered = profile.error?.status === 404;
  useEffect(() => {
    if (notRegistered) router.replace("/registration");
  }, [notRegistered, router]);

  if (profile.data) return <ProfileDashboard />;

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

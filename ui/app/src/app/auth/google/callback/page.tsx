'use client';

import { useAuth } from '@clerk/nextjs';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef, useState } from 'react';
import { toApiError } from '@/lib/api/api';
import { useApi } from '@/lib/api/hooks';

function GmailCallback() {
  const router = useRouter();
  const params = useSearchParams();
  const api = useApi();
  const { isLoaded } = useAuth();
  const started = useRef(false);
  const [error, setError] = useState('');
  const code = params.get('code');
  const state = params.get('state');
  const googleError = params.get('error');

  let paramsError = '';
  if (googleError === 'access_denied') paramsError = 'Gmail connection was cancelled.';
  else if (googleError) paramsError = `Google returned an error: ${googleError}`;
  else if (!code || !state) paramsError = 'Missing authorization code from Google.';

  useEffect(() => {
    if (!isLoaded || paramsError || !code || !state || started.current) return;
    started.current = true;

    api.completeGmailConnection({ code, state }).then(
      () => router.replace('/profile'),
      (caught) => setError(toApiError(caught).message),
    );
  }, [api, code, isLoaded, paramsError, router, state]);

  const message = paramsError || error;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#030711] px-4 text-center text-white">
      {message ? (
        <>
          <p role="alert">{message}</p>
          <Link href="/profile" className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100">
            Back to profile
          </Link>
        </>
      ) : (
        'Connecting your Gmail account…'
      )}
    </div>
  );
}

export default function GmailCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#030711] px-4 text-center text-white">
        Loading…
      </div>
    }>
      <GmailCallback />
    </Suspense>
  );
}

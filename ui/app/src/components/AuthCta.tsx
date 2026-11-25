'use client';

import { useAuth } from '@clerk/nextjs';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

type AuthCtaProps = {
  /** Demo mode runs without Clerk, so always show the signed-out links. */
  demo: boolean;
  className?: string;
  /** When set, also show a "Sign in" link with this class to visitors. */
  signInClassName?: string;
};

type AuthLinksProps = Omit<AuthCtaProps, 'demo'> & {
  signedIn: boolean;
  /** Keeps the space reserved while Clerk loads, without showing a guess. */
  hidden?: boolean;
};

function AuthLinks({ signedIn, hidden, className, signInClassName }: AuthLinksProps) {
  const style = hidden ? { visibility: 'hidden' as const } : undefined;
  if (signedIn) {
    return (
      <Link href="/profile" className={className} style={style}>
        <span>Go to profile</span>
        <ArrowUpRight aria-hidden="true" />
      </Link>
    );
  }
  return (
    <>
      {signInClassName && (
        <Link href="/auth/sign-in" className={signInClassName} style={style}>
          Sign in
        </Link>
      )}
      <Link href="/auth/sign-up" className={className} style={style}>
        <span>Get started</span>
        <ArrowUpRight aria-hidden="true" />
      </Link>
    </>
  );
}

function ClerkAuthLinks(props: Omit<AuthCtaProps, 'demo'>) {
  const { isLoaded, isSignedIn } = useAuth();
  return <AuthLinks {...props} signedIn={!!isSignedIn} hidden={!isLoaded} />;
}

/**
 * "Get started" for visitors and "Go to profile" for signed-in users. Checking
 * sign-in in the browser keeps the landing page static.
 */
export default function AuthCta({ demo, ...props }: AuthCtaProps) {
  return demo ? <AuthLinks {...props} signedIn={false} /> : <ClerkAuthLinks {...props} />;
}

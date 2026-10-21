'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { savePreviewValue } from '@/lib/preview';

/** Visual auth prototype. Replace with Clerk when authentication is connected. */
export default function SignUpForm({ signIn = false }: { signIn?: boolean }) {
  const router = useRouter();
  const [email, setEmail] = useState('');

  function continuePreview(social = false) {
    if (!signIn)
      savePreviewValue(
        'inboxzero-signup-email',
        social ? 'maya@studio.dev' : email.trim(),
      );
    router.push(signIn ? '/profile' : '/registration');
  }

  return (
    <>
      <h1>{signIn ? 'Welcome back' : 'Create your account'}</h1>
      <p className="muted">
        {signIn
          ? 'Sign in to your Inbox Zero workspace.'
          : 'A calmer inbox starts here.'}
      </p>
      <Button
        variant="outline"
        className="auth-social"
        onClick={() => continuePreview(true)}
      >
        Continue with Google
      </Button>
      <Button
        variant="outline"
        className="auth-social"
        onClick={() => continuePreview(true)}
      >
        Continue with Microsoft
      </Button>
      <p className="eyebrow muted">OR CONTINUE WITH EMAIL</p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          continuePreview();
        }}
        className="form-stack auth-form"
      >
        <div className="form-field">
          <Label htmlFor="auth-email">Email address</Label>
          <Input
            id="auth-email"
            type="email"
            autoComplete="email"
            required
            placeholder="maya@studio.dev"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="form-field">
          <Label htmlFor="auth-password">Password</Label>
          <Input
            id="auth-password"
            type="password"
            autoComplete={signIn ? 'current-password' : 'new-password'}
            required
            minLength={8}
            placeholder="••••••••••••"
          />
        </div>
        <Button className="auth-submit" type="submit">
          {signIn ? 'Sign in' : 'Create account'} →
        </Button>
      </form>
      <p className="auth-switch">
        {signIn ? 'New to Inbox Zero? ' : 'Already have an account? '}
        <Link href={signIn ? '/auth/sign-up' : '/auth/sign-in'}>
          {signIn ? 'Create an account' : 'Sign in'}
        </Link>
      </p>
      <p className="auth-caption">
        Clerk authentication concept · Demo navigation
      </p>
    </>
  );
}

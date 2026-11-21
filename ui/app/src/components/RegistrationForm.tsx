'use client';

import { useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toApiError } from '@/lib/api/api';
import { useApi } from '@/lib/api/hooks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import authStyles from '@/components/AuthShell.module.css';

export default function RegistrationForm() {
  const router = useRouter();
  const api = useApi();
  const { user } = useUser();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const email = user?.primaryEmailAddress?.emailAddress ?? '';

  async function register() {
    setSubmitting(true);
    setError('');
    try {
      await api.createUser({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      });
    } catch (caught) {
      const apiError = toApiError(caught);
      // 409 means this Clerk user is already registered.
      if (apiError.status !== 409) {
        setError(apiError.message);
        setSubmitting(false);
        return;
      }
    }
    router.push('/profile');
  }

  return (
    <>
      <p className="eyebrow">ACCOUNT CREATED / FINAL STEP</p>
      <h1>Make it yours.</h1>
      <p className="muted">
        Tell us a little about yourself to finish setting up your profile.
      </p>
      <form
        className={authStyles['form-stack']}
        onSubmit={(e) => {
          e.preventDefault();
          void register();
        }}
      >
        <div className={authStyles['form-field']}>
          <Label htmlFor="first-name">First name *</Label>
          <Input
            id="first-name"
            autoComplete="given-name"
            required
            pattern=".*\S.*"
            maxLength={80}
            placeholder="Maya"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
        </div>
        <div className={authStyles['form-field']}>
          <Label htmlFor="last-name">Last name *</Label>
          <Input
            id="last-name"
            autoComplete="family-name"
            required
            pattern=".*\S.*"
            maxLength={80}
            placeholder="Chen"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>
        <div className={authStyles['form-field']}>
          <Label htmlFor="primary-email">Primary email *</Label>
          <Input
            id="primary-email"
            type="email"
            autoComplete="email"
            readOnly
            placeholder="maya@studio.dev"
            aria-describedby="email-hint"
            value={email}
          />
          <small id="email-hint">From the account you signed up with.</small>
        </div>
        <small>* Required fields</small>
        {error && <small role="alert">{error}</small>}
        <Button
          className={authStyles['auth-submit']}
          type="submit"
          disabled={submitting}
        >
          {submitting ? 'Saving…' : 'Continue to my profile →'}
        </Button>
      </form>
      <small>Your email accounts can be connected from your profile.</small>
    </>
  );
}

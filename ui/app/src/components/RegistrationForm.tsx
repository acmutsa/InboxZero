'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useSessionValue } from '@/hooks/useSessionValue';
import { savePreviewValue } from '@/lib/preview';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function RegistrationForm() {
  const router = useRouter();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [editedEmail, setEmail] = useState<string | null>(null);
  const savedEmail = useSessionValue('inboxzero-signup-email');
  const email = editedEmail ?? savedEmail;

  return (
    <>
      <p className="eyebrow">ACCOUNT CREATED / FINAL STEP</p>
      <h1>Make it yours.</h1>
      <p className="muted">
        Tell us a little about yourself to finish setting up your profile.
      </p>
      <form
        className="form-stack"
        onSubmit={(e) => {
          e.preventDefault();
          savePreviewValue(
            'inboxzero-profile',
            JSON.stringify({
              firstName: firstName.trim(),
              lastName: lastName.trim(),
              email: email.trim(),
            }),
          );
          router.push('/profile');
        }}
      >
        <div className="form-field">
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
        <div className="form-field">
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
        <div className="form-field">
          <Label htmlFor="primary-email">Primary email *</Label>
          <Input
            id="primary-email"
            type="email"
            autoComplete="email"
            required
            placeholder="maya@studio.dev"
            aria-describedby="email-hint"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <small id="email-hint">Pre-filled from your sign-up email.</small>
        </div>
        <small>* Required fields</small>
        <Button className="auth-submit" type="submit">
          Continue to my profile →
        </Button>
      </form>
      <small>Your email accounts can be connected from your profile.</small>
    </>
  );
}

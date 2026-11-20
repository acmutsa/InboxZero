'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useSessionValue } from '@/hooks/useSessionValue';
import { clearPreview } from '@/lib/preview';
import { toApiError } from '@/lib/api/api';
import { useApi, useApiQuery } from '@/lib/api/hooks';
import type { EmailAccount } from '@/lib/api/types';
import InboxPanel from '@/components/InboxPanel';
import FloatingNavbar from '@/components/FloatingNavbar';
import Grainient from '@/components/Grainient';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import ProviderCard from './ProviderCard';
import ActivityCharts from './ActivityCharts';
import { emailTotal, gmailTotal, outlookTotal } from '@/lib/demo-analytics';
import dialogStyles from '@/components/ui/PreviewDialog.module.css';
import profileStyles from '@/components/profile/ProfileDashboard.module.css';
import navigationStyles from '@/components/FloatingNavbar.module.css';

type Person = { firstName: string; lastName: string; email: string };
const profileTabs = ['Profile', 'Workspace', 'Activity'];
const samplePerson: Person = { firstName: 'Maya', lastName: 'Chen', email: '' };

export default function ProfileDashboard() {
  const router = useRouter();
  const raw = useSessionValue('inboxzero-profile');
  const api = useApi();
  const emailAccounts = useApiQuery('email-accounts', (client) => client.getEmailAccounts());
  const accounts = emailAccounts.data ?? [];
  const [addOpen, setAddOpen] = useState(false);
  const [gmail, setGmail] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState('');
  const [accountError, setAccountError] = useState('');
  let person = samplePerson;
  try {
    const p = raw ? JSON.parse(raw) : null;
    if (
      p &&
      typeof p.firstName === 'string' &&
      typeof p.lastName === 'string' &&
      typeof p.email === 'string'
    )
      person = p;
  } catch {
    /* Use the sample identity for invalid preview data. */
  }

  async function connectGmail() {
    setConnecting(true);
    setConnectError('');
    try {
      const { authorization_url } = await api.connectGmail({ gmail: gmail.trim() });
      window.location.assign(authorization_url);
    } catch (caught) {
      setConnectError(toApiError(caught).message);
      setConnecting(false);
    }
  }

  async function disconnect(account: EmailAccount) {
    if (!window.confirm(`Disconnect ${account.email_account}?`)) return;
    setAccountError('');
    try {
      await api.disconnectEmailAccount(account.id);
      emailAccounts.reload();
    } catch (caught) {
      setAccountError(toApiError(caught).message);
    }
  }

  return (
    <main className={`gradient-page ${profileStyles['profile-page']}`}>
      <FloatingNavbar
        tabs={profileTabs}
        label="Profile page sections"
        action={
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                className={navigationStyles['nav-account']}
                aria-label={`Open account menu for ${person.firstName}`}
                title="Account menu"
              >
                <span aria-hidden="true">
                  {person.firstName.slice(0, 1).toUpperCase()}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem disabled>
                {person.firstName} {person.lastName}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  clearPreview();
                  router.push('/auth/sign-in');
                }}
              >
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        }
      />
      <section id="profile" className={profileStyles['profile-section']} aria-labelledby="profile-title">
        <div className={profileStyles['profile-summary']}>
          <div className={profileStyles['profile-gradient']} aria-hidden="true">
            <Grainient
              timeSpeed={1.5}
              grainAmount={0.015}
              contrast={1.1}
              zoom={0.9}
            />
          </div>
          <div className={profileStyles['profile-header']}>
            <div className={profileStyles['profile-copy']}>
              <span className="eyebrow">Your profile</span>
              <h1 id="profile-title">Hello, {person.firstName}!</h1>
            </div>
            <Button className={profileStyles['add-email']} onClick={() => setAddOpen(true)}>
              Add email
            </Button>
          </div>
          <section id="accounts" className={profileStyles['page-section']} aria-labelledby="accounts-title">
            <h2 id="accounts-title" className="sr-only">Linked email accounts</h2>
            <div className={profileStyles['provider-grid']}>
              {accounts.map((account) => (
                <ProviderCard
                  key={account.id}
                  provider={account.provider === 'gmail' ? 'Gmail' : 'Outlook'}
                  email={account.email_account}
                  connected
                  onConnectedChange={() => void disconnect(account)}
                />
              ))}
            </div>
            {emailAccounts.isLoading && !emailAccounts.data && <p>Loading email accounts…</p>}
            {emailAccounts.data && accounts.length === 0 && (
              <p>No email accounts connected yet. Use “Add email” to connect Gmail.</p>
            )}
            {emailAccounts.error && <p role="alert">{emailAccounts.error.message}</p>}
            {accountError && <p role="alert">{accountError}</p>}
          </section>
        </div>
      </section>
      <section id="workspace" aria-label="Email workspace">
        <InboxPanel name={person.firstName} />
      </section>
      <section id="activity" className={profileStyles['page-section']} aria-labelledby="activity-title">
        <Card className={`${profileStyles['activity-panel']} glass-surface`}>
          <h2 id="activity-title" className={profileStyles['activity-heading']}>Activity</h2>
          <div className={profileStyles['metrics']}>
            {[
              [emailTotal, 'Total emails'],
              [gmailTotal, 'Gmail'],
              [outlookTotal, 'Outlook'],
            ].map(([n, label]) => (
              <div key={label}>
                <strong>{n}</strong>
                <p>{label}</p>
              </div>
            ))}
          </div>
          <ActivityCharts />
        </Card>
      </section>
      <Dialog
        open={addOpen}
        onOpenChange={(open) => {
          setAddOpen(open);
          if (!open) setConnectError('');
        }}
      >
        <DialogContent className={dialogStyles['preview-dialog']}>
          <DialogTitle>Add an email account</DialogTitle>
          <DialogDescription>
            Enter the Gmail address to connect. You&apos;ll sign in to that account on Google.
          </DialogDescription>
          <form
            id="connect-gmail-form"
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              void connectGmail();
            }}
          >
            <Label htmlFor="gmail-address">Gmail address</Label>
            <Input
              id="gmail-address"
              type="email"
              autoComplete="email"
              required
              placeholder="you@gmail.com"
              value={gmail}
              onChange={(e) => setGmail(e.target.value)}
            />
          </form>
          {connectError && <small role="alert">{connectError}</small>}
          <Button type="submit" form="connect-gmail-form" disabled={connecting}>
            {connecting ? 'Redirecting to Google…' : 'Continue with Google'}
          </Button>
          <Button variant="outline" disabled>
            Continue with Microsoft (coming soon)
          </Button>
          <Button variant="outline" onClick={() => setAddOpen(false)}>
            Cancel
          </Button>
        </DialogContent>
      </Dialog>
    </main>
  );
}

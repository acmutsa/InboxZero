'use client';

import { useClerk } from '@clerk/nextjs';
import { useState } from 'react';
import { toApiError } from '@/lib/api/api';
import { useApi, useApiQuery, type ApiQuery } from '@/lib/api/hooks';
import type { EmailAccount, EmailProvider, User } from '@/lib/api/types';
import { loadAccountStats, summarizeStats } from '@/lib/email-stats';
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
import dialogStyles from '@/components/ui/PreviewDialog.module.css';
import profileStyles from '@/components/profile/ProfileDashboard.module.css';
import navigationStyles from '@/components/FloatingNavbar.module.css';

const profileTabs = ['Profile', 'Workspace', 'Activity'];

export default function ProfileDashboard({
  user,
  emailAccounts,
}: {
  user: User;
  emailAccounts: ApiQuery<EmailAccount[]>;
}) {
  const { signOut } = useClerk();
  const api = useApi();
  const accounts = emailAccounts.data ?? [];
  const accountIds = accounts.map((account) => account.id).join(',');
  const accountStats = useApiQuery(accountIds ? `stats:${accountIds}` : null, (client) =>
    loadAccountStats(client, accounts),
  );
  // Null while loading, so the panel doesn't show zeros that look like real data.
  const statsLoading = (!emailAccounts.data && !emailAccounts.error) || accountStats.isLoading;
  const stats = statsLoading ? null : summarizeStats(accountStats.data?.stats ?? []);
  const failedStats = accountStats.data?.failed ?? [];
  const firstName = user.first_name ?? '';
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');
  const [addOpen, setAddOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [connecting, setConnecting] = useState<EmailProvider | null>(null);
  const [connectError, setConnectError] = useState('');
  const [accountError, setAccountError] = useState('');

  async function connect(provider: EmailProvider) {
    setConnecting(provider);
    setConnectError('');
    try {
      const { authorization_url } =
        provider === 'gmail'
          ? await api.connectGmail({ gmail: email.trim() })
          : await api.connectOutlook({ outlook: email.trim() });
      window.location.assign(authorization_url);
    } catch (caught) {
      setConnectError(toApiError(caught).message);
      setConnecting(null);
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
                aria-label={`Open account menu for ${fullName || 'your account'}`}
                title="Account menu"
              >
                <span aria-hidden="true">
                  {(firstName.slice(0, 1) || '?').toUpperCase()}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem disabled>{fullName}</DropdownMenuItem>
              <DropdownMenuItem onClick={() => void signOut({ redirectUrl: '/' })}>
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
              <h1 id="profile-title">{firstName ? `Hello, ${firstName}!` : 'Hello!'}</h1>
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
              <p>No email accounts connected yet. Use “Add email” to connect Gmail or Outlook.</p>
            )}
            {emailAccounts.error && <p role="alert">{emailAccounts.error.message}</p>}
            {accountError && <p role="alert">{accountError}</p>}
          </section>
        </div>
      </section>
      <section id="workspace" aria-label="Email workspace">
        <InboxPanel accounts={accounts} onApprove={accountStats.reload} />
      </section>
      <section id="activity" className={profileStyles['page-section']} aria-labelledby="activity-title">
        <Card className={`${profileStyles['activity-panel']} glass-surface`}>
          <h2 id="activity-title" className={profileStyles['activity-heading']}>Activity</h2>
          <div className={profileStyles['metrics']}>
            {[
              [stats?.emailTotal, 'Total emails'],
              [stats?.gmailTotal, 'Gmail'],
              [stats?.outlookTotal, 'Outlook'],
            ].map(([n, label]) => (
              <div key={label}>
                <strong>{n ?? '—'}</strong>
                <p>{label}</p>
              </div>
            ))}
          </div>
          {accountStats.error && <p role="alert">{accountStats.error.message}</p>}
          {failedStats.length > 0 && (
            <p role="alert">Couldn&apos;t load stats for {failedStats.join(', ')}.</p>
          )}
          <ActivityCharts stats={stats} />
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
            Enter the address to connect. You&apos;ll sign in to that account on Google or Microsoft.
          </DialogDescription>
          <form
            id="connect-email-form"
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              const { submitter } = e.nativeEvent as SubmitEvent;
              const isOutlook = submitter instanceof HTMLButtonElement && submitter.value === 'outlook';
              void connect(isOutlook ? 'outlook' : 'gmail');
            }}
          >
            <Label htmlFor="email-address">Email address</Label>
            <Input
              id="email-address"
              type="email"
              autoComplete="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </form>
          {connectError && <small role="alert">{connectError}</small>}
          <Button type="submit" form="connect-email-form" value="gmail" disabled={connecting !== null}>
            {connecting === 'gmail' ? 'Redirecting to Google…' : 'Continue with Google'}
          </Button>
          <Button type="submit" form="connect-email-form" value="outlook" variant="outline" disabled={connecting !== null}>
            {connecting === 'outlook' ? 'Redirecting to Microsoft…' : 'Continue with Microsoft'}
          </Button>
          <Button variant="outline" onClick={() => setAddOpen(false)}>
            Cancel
          </Button>
        </DialogContent>
      </Dialog>
    </main>
  );
}

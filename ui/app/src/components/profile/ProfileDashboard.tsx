'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useSessionValue } from '@/hooks/useSessionValue';
import { clearPreview } from '@/lib/preview';
import InboxPanel from '@/components/InboxPanel';
import FloatingNavLinks from '@/components/FloatingNavLinks';
import SiteFooter from '@/components/SiteFooter';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
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
import { CategoryChart, DraftChart } from './EmailCharts';
import { sampleAccounts, type PreviewAccount } from '@/lib/preview-accounts';
import { emailTotal, gmailTotal, outlookTotal } from '@/lib/demo-analytics';

type Person = { firstName: string; lastName: string; email: string };
const profileTabs = ['Profile', 'Accounts', 'Analytics'];
const samplePerson: Person = { firstName: 'Maya', lastName: 'Chen', email: '' };

export default function ProfileDashboard() {
  const router = useRouter();
  const raw = useSessionValue('inboxzero-profile');
  const [addOpen, setAddOpen] = useState(false);
  const [accounts, setAccounts] = useState<PreviewAccount[]>(sampleAccounts);
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

  function addProvider(provider: string) {
    const email =
      provider === 'Gmail' ? 'maya.work@studio.dev' : 'maya.work@outlook.com';
    setAccounts((previous) =>
      previous.some((account) => account.email === email)
        ? previous.map((account) =>
            account.email === email ? { ...account, connected: true } : account,
          )
        : [...previous, { provider, email, connected: true }],
    );
    setAddOpen(false);
  }

  return (
    <main className="gradient-page profile-page">
      <header className="floating-nav profile-header">
        <Link className="brand" href="/">
          Inbox Zero
        </Link>
        <nav aria-label="Profile navigation">
          <FloatingNavLinks tabs={profileTabs} />
        </nav>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              className="user-menu"
              aria-label={`Open account menu for ${person.firstName}`}
            >
              <Avatar className="profile-avatar" aria-hidden="true">
                <AvatarFallback>
                  {person.firstName.slice(0, 1).toUpperCase()}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <a href="#profile">
                {person.firstName} {person.lastName}
              </a>
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
      </header>
      <section
        id="profile"
        className="profile-main"
        aria-labelledby="profile-title"
      >
        <h1 id="profile-title">Your profile</h1>
        <Card className="identity glass-surface">
          <Avatar className="profile-avatar" aria-hidden="true">
            <AvatarFallback>
              {person.firstName.slice(0, 1).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div>
            <h2>Hello, {person.firstName}!</h2>
            <p>{person.email || 'Personal workspace · Sample profile'}</p>
          </div>
        </Card>
        <section
          id="accounts"
          className="accounts"
          aria-labelledby="accounts-title"
        >
          <div className="section-heading">
            <h2 id="accounts-title">Link accounts</h2>
            <Button className="add-email" onClick={() => setAddOpen(true)}>
              Add email
            </Button>
          </div>
          <p className="muted">
            Connect an email account or manage your existing connections.
          </p>
          <div className="provider-grid">
            {accounts.map((account) => (
              <ProviderCard
                key={account.email}
                {...account}
                onConnectedChange={(connected) =>
                  setAccounts((previous) =>
                    previous.map((item) =>
                      item.email === account.email
                        ? { ...item, connected }
                        : item,
                    ),
                  )
                }
              />
            ))}
          </div>
        </section>
        <InboxPanel name={person.firstName} accounts={accounts} />
      </section>
      <section
        id="analytics"
        className="analytics"
        aria-labelledby="analytics-title"
      >
        <div className="section-heading">
          <div>
            <h2 id="analytics-title">Email activity</h2>
            <p>
              Email volume, categories, and draft needs across your connected
              accounts.
            </p>
          </div>
          <small>Last 30 days · Sample data</small>
        </div>
        <div className="metrics">
          {[
            [emailTotal, 'Total emails'],
            [gmailTotal, 'Gmail'],
            [outlookTotal, 'Outlook'],
          ].map(([n, label]) => (
            <Card className="glass-surface" key={label}>
              <strong>{n}</strong>
              <p>{label}</p>
            </Card>
          ))}
        </div>
        <div className="charts">
          <CategoryChart />
          <DraftChart />
        </div>
      </section>
      <SiteFooter profile />
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="preview-dialog">
          <DialogTitle>Add an email account</DialogTitle>
          <DialogDescription>
            Choose a provider to connect another inbox.
          </DialogDescription>
          <Button onClick={() => addProvider('Gmail')}>
            Continue with Google
          </Button>
          <Button variant="outline" onClick={() => addProvider('Outlook')}>
            Continue with Microsoft
          </Button>
          <Button variant="outline" onClick={() => setAddOpen(false)}>
            Cancel
          </Button>
          <small>Preview connection only.</small>
        </DialogContent>
      </Dialog>
    </main>
  );
}

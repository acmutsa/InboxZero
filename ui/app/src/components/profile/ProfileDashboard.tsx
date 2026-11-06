'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useSessionValue } from '@/hooks/useSessionValue';
import { clearPreview } from '@/lib/preview';
import InboxPanel from '@/components/InboxPanel';
import FloatingNavbar from '@/components/FloatingNavbar';
import Grainient from '@/components/Grainient';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
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
import { sampleAccounts, type PreviewAccount } from '@/lib/preview-accounts';
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
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className={dialogStyles['preview-dialog']}>
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

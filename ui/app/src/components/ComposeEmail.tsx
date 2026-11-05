'use client';

import { useState } from 'react';
import {
  Maximize2,
  Minimize2,
  Minus,
  Pencil,
  Send,
  Trash2,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { PreviewAccount } from '@/lib/preview-accounts';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
  DialogPortal,
} from '@/components/ui/dialog';

export type ComposedEmail = {
  to: string;
  subject: string;
  body: string;
  from: string;
  provider: string;
};

export default function ComposeEmail({
  onSend,
  accounts,
  container,
}: {
  onSend: (email: ComposedEmail) => void;
  accounts: PreviewAccount[];
  container: HTMLDivElement | null;
}) {
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [email, setEmail] = useState<
    Pick<ComposedEmail, 'to' | 'subject' | 'body'>
  >({ to: '', subject: '', body: '' });
  const [from, setFrom] = useState('');
  const connectedAccounts = accounts.filter((account) => account.connected);
  const sendingAccount =
    connectedAccounts.find((account) => account.email === from) ??
    connectedAccounts[0];
  const update = (key: 'to' | 'subject' | 'body', value: string) =>
    setEmail((previous) => ({ ...previous, [key]: value }));
  const reset = () => {
    setEmail({ to: '', subject: '', body: '' });
    setOpen(false);
    setMinimized(false);
    setExpanded(false);
  };

  return (
    <>
      <Dialog
        modal={false}
        open={open && !minimized}
        onOpenChange={(value) => {
          setOpen(value);
          setMinimized(false);
        }}
      >
        <DialogTrigger asChild>
          <Button
            className="compose-trigger"
            onClick={() => {
              setOpen(true);
              setMinimized(false);
            }}
          >
            <Pencil aria-hidden="true" />
            Compose
          </Button>
        </DialogTrigger>
        <DialogContent
          position="custom"
          container={container}
          className="compose-window"
          data-expanded={expanded}
          showCloseButton={false}
          onInteractOutside={(event) => event.preventDefault()}
        >
          <header className="compose-header">
            <DialogTitle>New message</DialogTitle>
            <div>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="Minimize message"
                onClick={() => setMinimized(true)}
              >
                <Minus />
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={
                  expanded ? 'Restore message size' : 'Expand message'
                }
                onClick={() => setExpanded((value) => !value)}
              >
                {expanded ? <Minimize2 /> : <Maximize2 />}
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="Close message"
                onClick={() => setOpen(false)}
              >
                <X />
              </Button>
            </div>
          </header>
          <form
            className="compose-form"
            onSubmit={(event) => {
              event.preventDefault();
              if (!sendingAccount) return;
              onSend({
                from: sendingAccount.email,
                provider: sendingAccount.provider,
                to: email.to.trim(),
                subject: email.subject.trim(),
                body: email.body.trim(),
              });
              reset();
            }}
          >
            <div className="compose-field">
              <Label htmlFor="compose-from">From</Label>
              <Select
                value={sendingAccount?.email ?? ''}
                onValueChange={setFrom}
                disabled={!connectedAccounts.length}
              >
                <SelectTrigger id="compose-from">
                  <SelectValue placeholder="No connected accounts" />
                </SelectTrigger>
                <SelectContent>
                  {connectedAccounts.map((account) => (
                    <SelectItem key={account.email} value={account.email}>
                      {account.email} · {account.provider}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {!sendingAccount && (
              <p className="compose-account-notice" role="status">
                Connect an email account above to send a preview.
              </p>
            )}
            <div className="compose-field">
              <Label htmlFor="compose-to">To</Label>
              <Input
                id="compose-to"
                type="email"
                required
                autoComplete="email"
                placeholder="recipient@example.com"
                value={email.to}
                onChange={(event) => update('to', event.target.value)}
              />
            </div>
            <div className="compose-field">
              <Label htmlFor="compose-subject">Subject</Label>
              <Input
                id="compose-subject"
                required
                pattern=".*\S.*"
                placeholder="Add a subject"
                value={email.subject}
                onChange={(event) => update('subject', event.target.value)}
              />
            </div>
            <Label htmlFor="compose-body" className="sr-only">
              Message
            </Label>
            <Textarea
              id="compose-body"
              className="compose-body"
              required
              placeholder="Write your message…"
              value={email.body}
              onChange={(event) => update('body', event.target.value)}
            />
            <DialogDescription className="compose-caption">
              Preview only · Messages stay in this page until you refresh.
            </DialogDescription>
            <footer className="compose-footer">
              <Button
                type="submit"
                disabled={!email.body.trim() || !sendingAccount}
              >
                <Send aria-hidden="true" />
                Send preview
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Discard message"
                onClick={reset}
              >
                <Trash2 />
              </Button>
            </footer>
          </form>
        </DialogContent>
        {open && minimized && (
          <DialogPortal container={container} forceMount>
            <Button
              className="compose-minimized"
              variant="outline"
              onClick={() => setMinimized(false)}
            >
              <Pencil aria-hidden="true" />
              <span>{email.subject || 'New message'}</span>
              <Maximize2 aria-hidden="true" />
              <span className="sr-only">Restore message</span>
            </Button>
          </DialogPortal>
        )}
      </Dialog>
    </>
  );
}

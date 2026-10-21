'use client';

import { useCallback, useRef, useState } from 'react';
import {
  Archive,
  ArrowLeft,
  CalendarDays,
  FilePenLine,
  Inbox,
  Mail,
  MailOpen,
  Send,
  X,
} from 'lucide-react';
import dynamic from 'next/dynamic';
import { sampleAccounts, type PreviewAccount } from '@/lib/preview-accounts';
import ComposeEmail, { type ComposedEmail } from '@/components/ComposeEmail';
import CalendarSkeleton from '@/components/profile/CalendarSkeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
const WorkspaceCalendar = dynamic(
  () => import('@/components/profile/WorkspaceCalendar'),
  {
    loading: () => <CalendarSkeleton />,
  },
);

const messages = [
  {
    id: 'alex',
    sender: 'Alex Morgan',
    email: 'alex@studio.dev',
    subject: 'Project update',
    body: 'Could you share the latest update before our check-in?',
    reply: 'Hi Alex, I’ll share the latest update before our check-in.',
    provider: 'Gmail',
    status: 'Draft ready · 9:42 AM',
  },
  {
    id: 'studio',
    sender: 'Studio team',
    email: 'team@studio.dev',
    subject: 'Friday catch-up',
    body: 'Are you free for a quick catch-up on Friday at 10 AM?',
    reply: 'Friday at 10 AM works for me. Looking forward to it.',
    provider: 'Gmail',
    status: 'Calendar checked · 9:15 AM',
  },
  {
    id: 'digest',
    sender: 'Weekly digest',
    email: 'digest@studio.dev',
    subject: 'This week’s highlights',
    body: 'A curated collection of product news and design ideas.',
    reply: '',
    provider: 'Outlook',
    status: 'Newsletter · Yesterday',
  },
  {
    id: 'jamie',
    sender: 'Jamie Park',
    email: 'jamie@studio.dev',
    subject: 'Design feedback',
    body: 'I’ve added my comments to the latest designs.',
    reply: 'Thanks, Jamie. I’ll review your comments and follow up.',
    provider: 'Outlook',
    status: 'Needs review · Yesterday',
  },
  {
    id: 'taylor',
    sender: 'Taylor Reed',
    email: 'taylor@studio.dev',
    subject: 'Next steps',
    body: 'Here is the summary from our meeting. Could you send the next steps?',
    reply: 'Thanks for the summary. I’ll send the next steps today.',
    provider: 'Outlook',
    status: 'Needs review · Yesterday',
  },
];
type Message = (typeof messages)[number] & { from?: string };

export default function InboxPanel({
  name = 'Maya',
  accounts = sampleAccounts,
}: {
  name?: string;
  accounts?: PreviewAccount[];
}) {
  const [workspaceNode, setWorkspaceNode] = useState<HTMLDivElement | null>(
    null,
  );
  const focusReaderTitle = useCallback((node: HTMLHeadingElement | null) => {
    node?.focus({ preventScroll: true });
  }, []);
  const messageTrigger = useRef<HTMLButtonElement | null>(null);
  const [tab, setTab] = useState('inbox');
  const [calendarOpened, setCalendarOpened] = useState(false);
  const [query, setQuery] = useState('');
  const [provider, setProvider] = useState('all');
  const [selected, setSelected] = useState<Message | null>(null);
  const [editing, setEditing] = useState(false);
  const [reply, setReply] = useState('');
  const [savedReplies, setSavedReplies] = useState<Record<string, string>>({});
  const [approved, setApproved] = useState<string[]>([]);
  const [notice, setNotice] = useState('');
  const [unreadIds, setUnreadIds] = useState(['alex', 'studio', 'jamie']);
  const [checkedIds, setCheckedIds] = useState<string[]>([]);
  const [archivedIds, setArchivedIds] = useState<string[]>([]);
  const [lastArchived, setLastArchived] = useState<string[]>([]);
  const [sentMessages, setSentMessages] = useState<Message[]>([]);
  const inboxCount = 12 - archivedIds.length;
  const unreadCount = unreadIds.filter(
    (id) => !archivedIds.includes(id),
  ).length;
  const draftCount = 4 - approved.length;
  const isDraft = tab === 'drafts';
  const visible = messages.filter(
    (message) =>
      (isDraft
        ? message.reply && !approved.includes(message.id)
        : message.id !== 'taylor' && !archivedIds.includes(message.id)) &&
      (provider === 'all' || message.provider === provider) &&
      `${message.sender} ${message.subject} ${message.body}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );

  const checkedVisible = visible.filter((message) =>
    checkedIds.includes(message.id),
  );
  const allChecked =
    visible.length > 0 && checkedVisible.length === visible.length;

  function bulkRead(unread: boolean) {
    const ids = checkedVisible.map((message) => message.id);
    setUnreadIds((previous) =>
      unread
        ? [...new Set([...previous, ...ids])]
        : previous.filter((id) => !ids.includes(id)),
    );
    setNotice(
      `${ids.length} message${ids.length === 1 ? '' : 's'} marked ${unread ? 'unread' : 'read'}.`,
    );
    setCheckedIds([]);
  }

  function sendPreview(email: ComposedEmail) {
    setSentMessages((previous) => [
      {
        id: `sent-${Date.now()}`,
        sender: email.to,
        email: email.to,
        subject: email.subject,
        body: email.body,
        reply: '',
        from: email.from,
        provider: email.provider,
        status: `${email.provider} · Sent preview`,
      },
      ...previous,
    ]);
    setNotice('Message added to Sent in this preview. No email was sent.');
    setSelected(null);
    setTab('sent');
    setQuery('');
    setProvider('all');
    setCheckedIds([]);
  }

  function openMessage(message: Message) {
    if (tab === 'inbox')
      setUnreadIds((previous) => previous.filter((id) => id !== message.id));
    setSelected(message);
    setReply(savedReplies[message.id] ?? `${message.reply}\n\nBest,\n${name}`);
    setEditing(false);
  }

  function closeMessage() {
    setSelected(null);
    const trigger = messageTrigger.current;
    requestAnimationFrame(() => {
      const target = trigger?.isConnected
        ? trigger
        : workspaceNode?.querySelector<HTMLElement>(
            '[data-slot="tabs-content"][data-state="active"]',
          );
      target?.focus({ preventScroll: true });
    });
  }

  const reader = selected && (
    <section
      key={selected.id}
      className="message-reader"
      aria-labelledby="message-reader-title"
      onKeyDown={(event) => {
        if (event.key === 'Escape') {
          event.stopPropagation();
          closeMessage();
        }
      }}
    >
      <div className="message-reader-toolbar">
        <Button variant="ghost" size="sm" onClick={closeMessage}>
          <ArrowLeft aria-hidden="true" />
          Back to {tab}
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Close message"
          onClick={closeMessage}
        >
          <X />
        </Button>
      </div>
      <header className="message-reader-header">
        <h3 id="message-reader-title" tabIndex={-1} ref={focusReaderTitle}>
          {selected.reply ? 'Re: ' : ''}
          {selected.subject}
        </h3>
        <p className="muted">
          {selected.id.startsWith('sent-') || selected.reply ? 'To' : 'From'}{' '}
          {selected.sender} · {selected.email}
        </p>
      </header>
      {selected.from && (
        <p className="muted sent-from">From: {selected.from}</p>
      )}
      <div className="message-reader-body">
        <strong className="muted">
          {selected.id.startsWith('sent-')
            ? 'Message · Preview only'
            : 'Original message'}
        </strong>
        <p className="original-message">
          {selected.id.startsWith('sent-') ? (
            selected.body
          ) : (
            <>
              Hi {name},<br />
              <br />
              {selected.body}
              <br />
              <br />
              {selected.sender}
            </>
          )}
        </p>
      </div>
      {selected.reply && (
        <div className="message-reader-reply">
          <Label htmlFor="reply-preview">Suggested reply</Label>
          {editing ? (
            <Textarea
              id="reply-preview"
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              rows={6}
              autoFocus
            />
          ) : (
            <p className="reply-preview">{reply}</p>
          )}
          {editing ? (
            <Button
              disabled={!reply.trim()}
              onClick={() => {
                setSavedReplies((previous) => ({
                  ...previous,
                  [selected.id]: reply,
                }));
                setEditing(false);
              }}
            >
              Save changes
            </Button>
          ) : (
            <>
              <Button
                onClick={() => {
                  setApproved((previous) =>
                    previous.includes(selected.id)
                      ? previous
                      : [...previous, selected.id],
                  );
                  setNotice(
                    'Reply approved in this preview. No email was sent.',
                  );
                  closeMessage();
                }}
              >
                Approve and send
              </Button>
              <Button variant="outline" onClick={() => setEditing(true)}>
                Edit reply
              </Button>
            </>
          )}
        </div>
      )}
      {tab === 'inbox' && (
        <Button
          variant="outline"
          onClick={() => {
            setUnreadIds((previous) =>
              previous.includes(selected.id)
                ? previous
                : [...previous, selected.id],
            );
            closeMessage();
          }}
        >
          Mark as unread
        </Button>
      )}
    </section>
  );

  return (
    <Tabs
      ref={setWorkspaceNode}
      value={tab}
      onValueChange={(value) => {
        if (value === 'calendar') setCalendarOpened(true);
        setTab(value);
        setSelected(null);
        setQuery('');
        setProvider('all');
        setCheckedIds([]);
      }}
      className="workspace"
    >
      <div className="workspace-topbar">
        <TabsList className="workspace-tabs" aria-label="Workspace views">
          <TabsTrigger value="inbox">
            <Inbox aria-hidden="true" />
            <span>Inbox</span>
            <span className="workspace-tab-count">{inboxCount}</span>
          </TabsTrigger>
          <TabsTrigger value="drafts">
            <FilePenLine aria-hidden="true" />
            <span>Drafts</span>
            <span className="workspace-tab-count">{draftCount}</span>
          </TabsTrigger>
          <TabsTrigger value="sent">
            <Send aria-hidden="true" />
            <span>Sent</span>
            <span className="workspace-tab-count">{sentMessages.length}</span>
          </TabsTrigger>
          <TabsTrigger value="calendar">
            <CalendarDays aria-hidden="true" />
            <span>Calendar</span>
          </TabsTrigger>
        </TabsList>
        <ComposeEmail
          onSend={sendPreview}
          accounts={accounts}
          container={workspaceNode}
        />
      </div>
      {notice && (
        <p className="preview-notice workspace-notice" role="status">
          {notice}
          {lastArchived.length > 0 && (
            <Button
              variant="ghost"
              onClick={() => {
                setArchivedIds((previous) =>
                  previous.filter((id) => !lastArchived.includes(id)),
                );
                setLastArchived([]);
                setNotice('Archive undone.');
              }}
            >
              Undo archive
            </Button>
          )}
        </p>
      )}
      {['inbox', 'drafts'].map((view) => (
        <TabsContent key={view} value={view} className="workspace-content">
          <div className="workspace-heading">
            <div>
              <h2>{view === 'inbox' ? `${name}’s Inbox` : 'Your drafts'}</h2>
              <p>
                {view === 'inbox'
                  ? 'Your latest messages, organized and ready for review.'
                  : 'Review suggested replies before you send them.'}
              </p>
            </div>
            <strong aria-live="polite">
              {view === 'inbox'
                ? `${inboxCount} messages · ${unreadCount} unread`
                : `${draftCount} drafts to review`}
            </strong>
          </div>
          <div className="workspace-search">
            <Input
              aria-label={`Search ${view}`}
              placeholder={`Search ${view}…`}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelected(null);
                setCheckedIds([]);
              }}
            />
            <Select
              value={provider}
              onValueChange={(value) => {
                setProvider(value);
                setSelected(null);
                setCheckedIds([]);
              }}
            >
              <SelectTrigger aria-label="Filter by provider">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  {view === 'inbox' ? 'All messages' : 'All accounts'}
                </SelectItem>
                <SelectItem value="Gmail">Gmail</SelectItem>
                <SelectItem value="Outlook">Outlook</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {view === 'inbox' && (
            <div
              className="message-bulk-actions"
              role="group"
              aria-label="Email selection actions"
            >
              <Label className="select-all">
                <Checkbox
                  aria-label="Select all visible emails"
                  disabled={!visible.length}
                  checked={
                    allChecked
                      ? true
                      : checkedVisible.length > 0
                        ? 'indeterminate'
                        : false
                  }
                  onCheckedChange={(checked) =>
                    setCheckedIds(
                      checked ? visible.map((message) => message.id) : [],
                    )
                  }
                />
                <span>
                  {checkedVisible.length
                    ? `${checkedVisible.length} selected`
                    : 'Select all'}
                </span>
              </Label>
              {checkedVisible.length > 0 && (
                <>
                  <Button variant="ghost" onClick={() => bulkRead(false)}>
                    <MailOpen aria-hidden="true" />
                    Mark read
                  </Button>
                  <Button variant="ghost" onClick={() => bulkRead(true)}>
                    <Mail aria-hidden="true" />
                    Mark unread
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      const ids = checkedVisible.map((message) => message.id);
                      setArchivedIds((previous) => [
                        ...new Set([...previous, ...ids]),
                      ]);
                      setLastArchived(ids);
                      if (selected && ids.includes(selected.id))
                        setSelected(null);
                      setCheckedIds([]);
                      setNotice(
                        `${ids.length} message${ids.length === 1 ? '' : 's'} archived in this preview.`,
                      );
                    }}
                  >
                    <Archive aria-hidden="true" />
                    Archive
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Clear selection"
                    onClick={() => setCheckedIds([])}
                  >
                    <X />
                  </Button>
                </>
              )}
            </div>
          )}
          <div className="mail-layout" data-reading={selected !== null}>
            <div className="mail-list-pane">
              <div className="message-list">
                {visible.map((message) => (
                  <div
                    className={`message-row${isDraft ? ' draft-row' : ''}`}
                    data-open={selected?.id === message.id}
                    data-selected={checkedIds.includes(message.id)}
                    data-read-state={
                      view === 'inbox'
                        ? unreadIds.includes(message.id)
                          ? 'unread'
                          : 'read'
                        : undefined
                    }
                    key={message.id}
                  >
                    {view === 'inbox' && (
                      <Checkbox
                        aria-label={`Select ${message.subject}`}
                        checked={checkedIds.includes(message.id)}
                        onCheckedChange={(checked) =>
                          setCheckedIds((previous) =>
                            checked
                              ? [...new Set([...previous, message.id])]
                              : previous.filter((id) => id !== message.id),
                          )
                        }
                      />
                    )}
                    <button
                      className="message-open"
                      aria-pressed={selected?.id === message.id}
                      onClick={(event) => {
                        messageTrigger.current = event.currentTarget;
                        openMessage(message);
                      }}
                    >
                      <span className="message-sender">
                        <strong>{message.sender}</strong>
                        <small>
                          {isDraft ? (
                            'Suggested reply'
                          ) : (
                            <>
                              <span
                                className="message-read-indicator"
                                aria-hidden="true"
                              />
                              {unreadIds.includes(message.id)
                                ? 'Unread'
                                : 'Read'}
                              <span aria-hidden="true"> · </span>To {name}
                            </>
                          )}
                        </small>
                      </span>
                      <span className="message-copy">
                        <strong>
                          {isDraft ? 'Re: ' : ''}
                          {message.subject}
                        </strong>
                        <span>
                          {isDraft
                            ? (savedReplies[message.id] ?? message.reply)
                            : message.body}
                        </span>
                      </span>
                      <span className="message-status">
                        <small>
                          {isDraft
                            ? `${message.provider} · Ready to review`
                            : approved.includes(message.id)
                              ? 'Approved · Preview'
                              : message.status}
                        </small>
                        {isDraft && <strong>Review draft →</strong>}
                      </span>
                    </button>
                  </div>
                ))}
                {visible.length === 0 && (
                  <p className="empty-state">
                    {query || provider !== 'all'
                      ? 'No messages match your search.'
                      : view === 'inbox'
                        ? 'Your inbox is clear.'
                        : 'All done. No drafts left to review.'}
                  </p>
                )}
              </div>
              <small>
                {isDraft
                  ? 'Every draft needs your approval before sending.'
                  : `Showing ${visible.length} of ${inboxCount} messages · Sample workspace`}
              </small>
            </div>
            {tab === view && reader}
          </div>
        </TabsContent>
      ))}
      <TabsContent value="sent" className="workspace-content">
        <div className="workspace-heading">
          <div>
            <h2>Sent messages</h2>
            <p>Messages composed in this preview.</p>
          </div>
          <strong>{sentMessages.length} sent</strong>
        </div>
        <div className="mail-layout" data-reading={selected !== null}>
          <div className="mail-list-pane">
            <div className="message-list">
              {sentMessages.map((message) => (
                <div
                  className="message-row sent-row"
                  data-open={selected?.id === message.id}
                  key={message.id}
                >
                  <button
                    className="message-open"
                    aria-pressed={selected?.id === message.id}
                    onClick={(event) => {
                      messageTrigger.current = event.currentTarget;
                      openMessage(message);
                    }}
                  >
                    <span className="message-sender">
                      <strong title={message.email}>To: {message.email}</strong>
                      <small title={message.from}>From: {message.from}</small>
                    </span>
                    <span className="message-copy">
                      <strong>{message.subject}</strong>
                      <span>{message.body}</span>
                    </span>
                    <span className="message-status">
                      <small>{message.status}</small>
                      <strong>View message →</strong>
                    </span>
                  </button>
                </div>
              ))}
              {!sentMessages.length && (
                <p className="empty-state">
                  No sent messages yet. Choose Compose to write one.
                </p>
              )}
            </div>
          </div>
          {reader}
        </div>
      </TabsContent>
      {calendarOpened && (
        <TabsContent
          value="calendar"
          forceMount
          hidden={tab !== 'calendar'}
          className="calendar-content"
        >
          <WorkspaceCalendar />
        </TabsContent>
      )}
    </Tabs>
  );
}

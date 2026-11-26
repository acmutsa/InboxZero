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
import { toApiError } from '@/lib/api/api';
import { useApi, useApiQuery } from '@/lib/api/hooks';
import type { Draft, Email, EmailAccount, EmailProvider } from '@/lib/api/types';
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
import calendarStyles from '@/components/profile/WorkspaceCalendar.module.css';
import inboxStyles from '@/components/InboxPanel.module.css';
type Message = {
  id: string;
  sender: string;
  email: string;
  subject: string;
  body: string;
  reply: string;
  provider: EmailProvider | '';
  status: string;
  from?: string;
};

const providerLabel = { gmail: 'Gmail', outlook: 'Outlook' };

/** "9:42 AM" today, "Yesterday", otherwise a short date. */
function formatTime(iso: string) {
  const date = new Date(iso);
  const days = Math.round(
    (new Date().setHours(0, 0, 0, 0) - new Date(iso).setHours(0, 0, 0, 0)) / 86_400_000,
  );
  if (days === 0) return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  if (days === 1) return 'Yesterday';
  return date.toLocaleDateString();
}

const WorkspaceCalendar = dynamic(
  () => import('@/components/profile/WorkspaceCalendar'),
  {
    loading: () => <CalendarSkeleton />,
  },
);

export default function InboxPanel({
  accounts,
}: {
  accounts: EmailAccount[];
}) {
  const api = useApi();
  const emails = useApiQuery('emails', (client) => client.getEmails());
  const drafts = useApiQuery('drafts:in_review', (client) => client.getDrafts('in_review'));
  const sent = useApiQuery('drafts:sent', (client) => client.getDrafts('sent'));
  const [saving, setSaving] = useState(false);
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
  const [notice, setNotice] = useState('');
  // shortcut: read/unread and archive live only in this tab (no DB columns yet); persist them when the schema has them.
  const [unreadIds, setUnreadIds] = useState<string[]>([]);
  const [checkedIds, setCheckedIds] = useState<string[]>([]);
  const [archivedIds, setArchivedIds] = useState<string[]>([]);
  const [lastArchived, setLastArchived] = useState<string[]>([]);
  const accountOf = (accountId: string) =>
    accounts.find((account) => account.id === accountId);
  const emailById = new Map((emails.data ?? []).map((email) => [email.id, email]));
  const draftedEmailIds = new Set((drafts.data ?? []).map((draft) => draft.reply_to_email));
  const toInboxMessage = (email: Email): Message => ({
    id: email.id,
    sender: email.from_address,
    email: email.from_address,
    subject: email.subject ?? '(no subject)',
    body: email.body ?? '',
    reply: '',
    provider: accountOf(email.email_account_id)?.provider ?? '',
    status: `${draftedEmailIds.has(email.id) ? 'Draft ready' : (email.category ?? 'Uncategorized')} · ${formatTime(email.created_at)}`,
  });
  const toDraftMessage = (draft: Draft): Message => {
    const original = draft.reply_to_email ? emailById.get(draft.reply_to_email) : undefined;
    const provider = accountOf(draft.email_account_id)?.provider ?? '';
    return {
      id: draft.id,
      sender: draft.to_address,
      email: draft.to_address,
      subject: original?.subject ?? draft.subject ?? '(no subject)',
      body: original?.body ?? '',
      reply: draft.body ?? '',
      provider,
      status: `${provider ? providerLabel[provider] : ''} · ${formatTime(draft.updated_at)}`,
    };
  };
  const toSentMessage = (draft: Draft): Message => ({
    ...toDraftMessage(draft),
    subject: draft.subject ?? '(no subject)',
    body: draft.body ?? '',
    reply: '',
    from: accountOf(draft.email_account_id)?.email_account,
  });
  const inboxMessages = (emails.data ?? [])
    .filter((email) => !archivedIds.includes(email.id))
    .map(toInboxMessage);
  const draftMessages = (drafts.data ?? []).map(toDraftMessage);
  const sentMessages = (sent.data ?? []).map(toSentMessage);
  const inboxCount = inboxMessages.length;
  const draftCount = draftMessages.length;
  const isDraft = tab === 'drafts';
  const activeQuery = isDraft ? drafts : emails;
  const visible = (isDraft ? draftMessages : inboxMessages).filter(
    (message) =>
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

  async function saveDraft(message: Message, approve: boolean) {
    setSaving(true);
    try {
      await api.updateDraft(message.id, approve ? { body: reply, status: 'sent' } : { body: reply });
      drafts.reload();
      if (approve) {
        sent.reload();
        setNotice('Reply approved.');
        closeMessage();
      } else {
        setEditing(false);
      }
    } catch (error) {
      setNotice(toApiError(error).message);
    } finally {
      setSaving(false);
    }
  }

  function openMessage(message: Message) {
    if (tab === 'inbox')
      setUnreadIds((previous) => previous.filter((id) => id !== message.id));
    setSelected(message);
    setReply(message.reply);
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
      className={inboxStyles['message-reader']}
      aria-labelledby="message-reader-title"
      onKeyDown={(event) => {
        if (event.key === 'Escape') {
          event.stopPropagation();
          closeMessage();
        }
      }}
    >
      <div className={inboxStyles['message-reader-toolbar']}>
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
      <header className={inboxStyles['message-reader-header']}>
        <h3 id="message-reader-title" tabIndex={-1} ref={focusReaderTitle}>
          {selected.reply ? 'Re: ' : ''}
          {selected.subject}
        </h3>
        <p className="muted">
          {selected.reply || tab === 'sent' ? 'To' : 'From'} {selected.email}
        </p>
      </header>
      <div className={inboxStyles['message-reader-body']}>
        <strong className="muted">
          {tab === 'sent' ? 'Your reply' : 'Original message'}
        </strong>
        <p className={inboxStyles['original-message']}>{selected.body}</p>
      </div>
      {selected.reply && (
        <div className={inboxStyles['message-reader-reply']}>
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
            <p className={inboxStyles['reply-preview']}>{reply}</p>
          )}
          {editing ? (
            <Button
              disabled={!reply.trim() || saving}
              onClick={() => saveDraft(selected, false)}
            >
              Save changes
            </Button>
          ) : (
            <>
              <Button disabled={saving} onClick={() => saveDraft(selected, true)}>
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
      orientation="vertical"
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
      className={inboxStyles['workspace']}
    >
      <aside className={inboxStyles['workspace-sidebar']} aria-label="Workspace navigation">
        <div className={inboxStyles['sidebar-heading']}>Workspace</div>
        <TabsList className={inboxStyles['workspace-tabs']} aria-label="Workspace views">
          <TabsTrigger value="inbox" title="Inbox">
            <Inbox aria-hidden="true" />
            <span>Inbox</span>
            <span className={inboxStyles['workspace-tab-count']}>{inboxCount}</span>
          </TabsTrigger>
          <TabsTrigger value="drafts" title="Drafts">
            <FilePenLine aria-hidden="true" />
            <span>Drafts</span>
            <span className={inboxStyles['workspace-tab-count']}>{draftCount}</span>
          </TabsTrigger>
          <TabsTrigger value="sent" title="Sent">
            <Send aria-hidden="true" />
            <span>Sent</span>
            <span className={inboxStyles['workspace-tab-count']}>{sentMessages.length}</span>
          </TabsTrigger>
          <TabsTrigger value="calendar" title="Calendar">
            <CalendarDays aria-hidden="true" />
            <span>Calendar</span>
          </TabsTrigger>
        </TabsList>
      </aside>
      <div className={inboxStyles['workspace-main']}>
      {notice && (
        <p className={`${inboxStyles['preview-notice']} ${inboxStyles['workspace-notice']}`} role="status">
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
        <TabsContent key={view} value={view} className={inboxStyles['workspace-content']}>
          {view === 'drafts' && <div className={inboxStyles['workspace-heading']}>
            <div>
              <h2>Your drafts</h2>
              <p>Review suggested replies before you send them.</p>
            </div>
            <strong aria-live="polite">
              {draftCount} drafts to review
            </strong>
          </div>}
          <div className={inboxStyles['workspace-search']}>
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
                <SelectItem value="gmail">Gmail</SelectItem>
                <SelectItem value="outlook">Outlook</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {view === 'inbox' && (
            <div
              className={inboxStyles['message-bulk-actions']}
              role="group"
              aria-label="Email selection actions"
            >
              <Label className={inboxStyles['select-all']}>
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
          <div className={inboxStyles['mail-layout']} data-reading={selected !== null}>
            <div className={inboxStyles['mail-list-pane']}>
              <div className={inboxStyles['message-list']}>
                {visible.map((message) => (
                  <div
                    className={`${inboxStyles['message-row']}${isDraft ? ` ${inboxStyles['draft-row']}` : ""}`}
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
                      className={inboxStyles['message-open']}
                      aria-pressed={selected?.id === message.id}
                      onClick={(event) => {
                        messageTrigger.current = event.currentTarget;
                        openMessage(message);
                      }}
                    >
                      <span className={inboxStyles['message-sender']}>
                        <strong>{message.sender}</strong>
                        <small>
                          {isDraft ? (
                            'Suggested reply'
                          ) : (
                            <>
                              <span
                                className={inboxStyles['message-read-indicator']}
                                aria-hidden="true"
                              />
                              {unreadIds.includes(message.id)
                                ? 'Unread'
                                : 'Read'}
                            </>
                          )}
                        </small>
                      </span>
                      <span className={inboxStyles['message-copy']}>
                        <strong>
                          {isDraft ? 'Re: ' : ''}
                          {message.subject}
                        </strong>
                        <span>
                          {isDraft
                            ? message.reply
                            : message.body}
                        </span>
                      </span>
                      <span className={inboxStyles['message-status']}>
                        <span
                          className={inboxStyles['message-status-label']}
                          data-kind={isDraft || message.status.startsWith('Draft ready') ? 'action' : 'muted'}
                        >
                          {isDraft ? 'Draft ready' : message.status.split(' · ')[0]}
                        </span>
                        <small>
                          {message.status.split(' · ')[1]}
                        </small>
                        {isDraft && <strong>Review draft →</strong>}
                      </span>
                    </button>
                  </div>
                ))}
                {visible.length === 0 && (
                  <p
                    className={inboxStyles['empty-state']}
                    role={activeQuery.error ? 'alert' : undefined}
                  >
                    {activeQuery.error
                      ? activeQuery.error.message
                      : activeQuery.isLoading && !activeQuery.data
                        ? 'Loading…'
                        : query || provider !== 'all'
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
                  : `Showing ${visible.length} of ${inboxCount} messages`}
              </small>
            </div>
            {tab === view && reader}
          </div>
        </TabsContent>
      ))}
      <TabsContent value="sent" className={inboxStyles['workspace-content']}>
        <div className={inboxStyles['workspace-heading']}>
          <div>
            <h2>Sent messages</h2>
            <p>Replies you approved.</p>
          </div>
          <strong>{sentMessages.length} sent</strong>
        </div>
        <div className={inboxStyles['mail-layout']} data-reading={selected !== null}>
          <div className={inboxStyles['mail-list-pane']}>
            <div className={inboxStyles['message-list']}>
              {sentMessages.map((message) => (
                <div
                  className={inboxStyles['message-row']}
                  data-open={selected?.id === message.id}
                  key={message.id}
                >
                  <button
                    className={inboxStyles['message-open']}
                    aria-pressed={selected?.id === message.id}
                    onClick={(event) => {
                      messageTrigger.current = event.currentTarget;
                      openMessage(message);
                    }}
                  >
                    <span className={inboxStyles['message-sender']}>
                      <strong title={message.email}>To: {message.email}</strong>
                      <small title={message.from}>From: {message.from}</small>
                    </span>
                    <span className={inboxStyles['message-copy']}>
                      <strong>{message.subject}</strong>
                      <span>{message.body}</span>
                    </span>
                    <span className={inboxStyles['message-status']}>
                      <small>{message.status}</small>
                      <strong>View message →</strong>
                    </span>
                  </button>
                </div>
              ))}
              {!sentMessages.length && (
                <p
                  className={inboxStyles['empty-state']}
                  role={sent.error ? 'alert' : undefined}
                >
                  {sent.error
                    ? sent.error.message
                    : sent.isLoading && !sent.data
                      ? 'Loading…'
                      : 'No sent messages yet. Approve a draft to see it here.'}
                </p>
              )}
            </div>
          </div>
          {tab === 'sent' && reader}
        </div>
      </TabsContent>
      {calendarOpened && (
        <TabsContent
          value="calendar"
          forceMount
          hidden={tab !== 'calendar'}
          className={calendarStyles['calendar-content']}
        >
          <WorkspaceCalendar />
        </TabsContent>
      )}
      </div>
    </Tabs>
  );
}

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
import { previewInbox, previewDrafts, previewUnreadIds, type PreviewMessage } from '@/lib/preview-messages';

type Message = PreviewMessage & { from?: string };

const WorkspaceCalendar = dynamic(
  () => import('@/components/profile/WorkspaceCalendar'),
  {
    loading: () => <CalendarSkeleton />,
  },
);

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
  const [sentMessages, setSentMessages] = useState<Message[]>([]);
  const [notice, setNotice] = useState('');
  const [unreadIds, setUnreadIds] = useState(previewUnreadIds);
  const [checkedIds, setCheckedIds] = useState<string[]>([]);
  const [archivedIds, setArchivedIds] = useState<string[]>([]);
  const [lastArchived, setLastArchived] = useState<string[]>([]);
  const inboxCount = previewInbox.filter(
    (message) => !archivedIds.includes(message.id),
  ).length;
  const draftCount = previewDrafts.filter((message) => !approved.includes(message.id)).length;
  const isDraft = tab === 'drafts';
  const visible = (isDraft ? previewDrafts : previewInbox).filter(
    (message) =>
      (isDraft
        ? !approved.includes(message.id)
        : !archivedIds.includes(message.id)) &&
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

  function approveReply(message: Message) {
    if (!approved.includes(message.id)) {
      setApproved((previous) => [...previous, message.id]);
      setSentMessages((previous) => [
        {
          ...message,
          id: `sent-${message.id}`,
          subject: `Re: ${message.subject}`,
          body: reply,
          reply: '',
          from:
            accounts.find(
              (account) =>
                account.connected && account.provider === message.provider,
            )?.email ?? message.provider,
          status: `${message.provider} · Approved preview`,
        },
        ...previous,
      ]);
    }
    setNotice('Reply approved in this preview. No email was sent.');
    closeMessage();
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
          {selected.reply ? 'To' : 'From'}{' '}
          {selected.sender} · {selected.email}
        </p>
      </header>
      <div className={inboxStyles['message-reader-body']}>
        <strong className="muted">
          Original message
        </strong>
        <p className={inboxStyles['original-message']}>
          Hi {name},<br />
          <br />
          {selected.body}
          <br />
          <br />
          {selected.sender}
        </p>
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
              <Button onClick={() => approveReply(selected)}>
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
            <span className={inboxStyles['workspace-tab-count']}>0</span>
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
                <SelectItem value="Gmail">Gmail</SelectItem>
                <SelectItem value="Outlook">Outlook</SelectItem>
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
                            ? (savedReplies[message.id] ?? message.reply)
                            : message.body}
                        </span>
                      </span>
                      <span className={inboxStyles['message-status']}>
                        <span
                          className={inboxStyles['message-status-label']}
                          data-kind={approved.includes(message.id) ? 'approved' : message.reply ? 'action' : 'muted'}
                        >
                          {isDraft ? 'Draft ready' : approved.includes(message.id)
                            ? 'Approved' : message.status.split(' · ')[0]}
                        </span>
                        <small>
                          {isDraft ? message.provider : message.status.split(' · ')[1]}
                        </small>
                        {isDraft && <strong>Review draft →</strong>}
                      </span>
                    </button>
                  </div>
                ))}
                {visible.length === 0 && (
                  <p className={inboxStyles['empty-state']}>
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
            <p>Replies you approved in this preview.</p>
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
                <p className={inboxStyles['empty-state']}>
                  No sent messages yet. Approve a draft to see it here.
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

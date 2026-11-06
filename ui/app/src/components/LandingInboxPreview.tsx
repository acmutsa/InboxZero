import { CalendarDays, ChevronDown, FilePenLine, Inbox, Send } from 'lucide-react';
import { previewInbox as inbox, previewDrafts, previewUnreadIds } from '@/lib/preview-messages';
import styles from '@/components/InboxPanel.module.css';

const unreadIds = new Set(previewUnreadIds);
const navigation = [
  { label: 'Inbox', icon: Inbox, count: inbox.length },
  { label: 'Drafts', icon: FilePenLine, count: previewDrafts.length },
  { label: 'Sent', icon: Send, count: 0 },
  { label: 'Calendar', icon: CalendarDays },
];

/** Static server-rendered markup; only content and CSS are shared with profile. */
export default function LandingInboxPreview() {
  return (
    <div
      className={styles.workspace}
      data-compact
      role="img"
      aria-label="Workspace preview: an inbox with email navigation, search, and four organized messages."
    >
      <div className={styles['workspace-sidebar']} aria-hidden="true">
        <div className={styles['sidebar-heading']}>Workspace</div>
        <div className={styles['workspace-tabs']} data-slot="tabs-list">
          {navigation.map(({ label, icon: Icon, count }) => (
            <div key={label} data-slot="tabs-trigger" data-state={label === 'Inbox' ? 'active' : 'inactive'}>
              <Icon />
              <span>{label}</span>
              {count !== undefined && <span className={styles['workspace-tab-count']}>{count}</span>}
            </div>
          ))}
        </div>
      </div>
      <div className={styles['workspace-main']} aria-hidden="true">
        <div className={styles['workspace-content']} data-slot="tabs-content" data-state="active">
          <div className={styles['workspace-search']}>
            <div data-slot="input">Search inbox…</div>
            <div data-slot="select-trigger" className={styles['static-filter']}>All messages <ChevronDown /></div>
          </div>
          <div className={styles['message-bulk-actions']}>
            <div className={styles['select-all']}>
              <span data-slot="checkbox" />
              <span>Select all</span>
            </div>
          </div>
          <div className={styles['mail-layout']}>
            <div className={styles['mail-list-pane']}>
              <div className={styles['message-list']}>
                {inbox.map((message) => (
                  <div className={styles['message-row']} key={message.id} data-read-state={unreadIds.has(message.id) ? 'unread' : 'read'}>
                    <span data-slot="checkbox" />
                    <div className={styles['message-open']}>
                      <span className={styles['message-sender']}>
                        <strong>{message.sender}</strong>
                        <small><span className={styles['message-read-indicator']} />{unreadIds.has(message.id) ? 'Unread' : 'Read'}</small>
                      </span>
                      <span className={styles['message-copy']}>
                        <strong>{message.subject}</strong>
                        <span>{message.body}</span>
                      </span>
                      <span className={styles['message-status']}>
                        <span className={styles['message-status-label']} data-kind={message.reply ? 'action' : 'muted'}>{message.status.split(' · ')[0]}</span>
                        <small>{message.status.split(' · ')[1]}</small>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <small>Showing {inbox.length} of {inbox.length} messages</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

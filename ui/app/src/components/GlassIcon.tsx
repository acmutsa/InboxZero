import { CalendarDays, Inbox, Send } from 'lucide-react';
import iconStyles from '@/components/GlassIcon.module.css';

const icons = {
  inbox: Inbox,
  send: Send,
  calendar: CalendarDays,
};

/** Decorative layered icon; its surrounding heading supplies the accessible label. */
export default function GlassIcon({
  name,
  tone = 'blue',
}: {
  name: keyof typeof icons;
  tone?: 'blue' | 'violet' | 'mint';
}) {
  const Icon = icons[name];
  return (
    <span className={iconStyles['glass-icon']} data-tone={tone} aria-hidden="true">
      <span className={iconStyles['glass-icon-back']} />
      <span className={iconStyles['glass-icon-front']}>
        <Icon strokeWidth={1.6} />
      </span>
    </span>
  );
}

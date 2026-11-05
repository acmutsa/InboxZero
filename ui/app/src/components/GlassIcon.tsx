import { CalendarDays, Inbox, Mail, Send, Sparkles } from 'lucide-react';

const icons = {
  inbox: Inbox,
  mail: Mail,
  send: Send,
  calendar: CalendarDays,
  sparkles: Sparkles,
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
    <span className="glass-icon" data-tone={tone} aria-hidden="true">
      <span className="glass-icon-back" />
      <span className="glass-icon-front">
        <Icon strokeWidth={1.6} />
      </span>
    </span>
  );
}

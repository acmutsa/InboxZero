import { Skeleton } from '@/components/ui/skeleton';
import calendarStyles from '@/components/profile/WorkspaceCalendar.module.css';

export default function CalendarSkeleton() {
  return (
    <div role="status" aria-label="Loading calendar" aria-busy="true">
      <span className="sr-only">Loading calendar…</span>
      <div aria-hidden="true">
        <div className={calendarStyles['calendar-skeleton-header']}>
          <div>
            <Skeleton className={calendarStyles['calendar-skeleton-title']} />
            <Skeleton className={calendarStyles['calendar-skeleton-description']} />
          </div>
        </div>
        <div className={calendarStyles['calendar-layout']}>
          <div className={calendarStyles['calendar-skeleton-sidebar']}>
            <Skeleton className={calendarStyles['calendar-skeleton-month']} />
            <Skeleton className={calendarStyles['calendar-skeleton-list']} />
            <Skeleton className={calendarStyles['calendar-skeleton-list']} />
          </div>
          <Skeleton className={calendarStyles['calendar-skeleton-grid']} />
        </div>
      </div>
    </div>
  );
}

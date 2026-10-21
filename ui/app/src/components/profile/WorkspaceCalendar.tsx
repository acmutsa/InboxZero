'use client';

import { useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, Plus, CalendarDays } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Calendar } from '@/components/ui/calendar';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type CalendarEvent = {
  id: number;
  title: string;
  date: string;
  time: string;
  calendar: string;
  duration: number;
};
const sampleEvents: CalendarEvent[] = [
  {
    id: 1,
    title: 'Project review',
    date: '2026-10-12',
    time: '10:00',
    calendar: 'Work · Studio',
    duration: 60,
  },
  {
    id: 2,
    title: 'Focus time',
    date: '2026-10-13',
    time: '13:00',
    calendar: 'Personal',
    duration: 60,
  },
  {
    id: 3,
    title: 'Design sync',
    date: '2026-10-14',
    time: '14:00',
    calendar: 'Work · Studio',
    duration: 60,
  },
  {
    id: 4,
    title: 'Studio catch-up',
    date: '2026-10-16',
    time: '10:00',
    calendar: 'Work · Studio',
    duration: 30,
  },
];
// Stable fixture date keeps the UI aligned with the Figma sample workspace.
const previewToday = new Date(2026, 9, 16, 12);
const dateKey = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
const addDays = (date: Date, amount: number) =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate() + amount, 12);
const monthLabel = (date: Date) =>
  date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
const hourLabel = (hour: number) =>
  hour === 12 ? 'Noon' : `${hour % 12 || 12} ${hour >= 12 ? 'PM' : 'AM'}`;

export default function WorkspaceCalendar() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [date, setDate] = useState(previewToday);
  const [view, setView] = useState('Week');
  const [events, setEvents] = useState(sampleEvents);
  const [hidden, setHidden] = useState<string[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [selected, setSelected] = useState<CalendarEvent | null>(null);
  const [calendar, setCalendar] = useState('Personal');
  const weekStart = addDays(date, -date.getDay());
  const days =
    view === 'Day'
      ? [date]
      : Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const monthStart = new Date(date.getFullYear(), date.getMonth(), 1, 12);
  const monthDays = Array.from(
    {
      length:
        35 +
        (new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate() +
          monthStart.getDay() >
        35
          ? 7
          : 0),
    },
    (_, i) => addDays(monthStart, i - monthStart.getDay()),
  );
  const visibleEvents = events.filter(
    (event) => !hidden.includes(event.calendar),
  );
  const title =
    view === 'Month'
      ? monthLabel(date)
      : view === 'Day'
        ? date.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric',
            year: 'numeric',
          })
        : new Intl.DateTimeFormat('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
          }).formatRange(weekStart, addDays(weekStart, 6));

  useEffect(() => {
    const scroller = scrollRef.current;
    if (scroller) scroller.scrollTop = view === 'Month' ? 0 : 8 * 84;
  }, [view]);

  function navigate(direction: number) {
    setDate(
      view === 'Month'
        ? new Date(date.getFullYear(), date.getMonth() + direction, 1, 12)
        : addDays(date, direction * (view === 'Week' ? 7 : 1)),
    );
  }
  function eventButton(event: CalendarEvent, timed = false) {
    const [hour, minute] = event.time.split(':').map(Number);
    const end = hour * 60 + minute + event.duration;
    const formatTime = (minutes: number) =>
      `${Math.floor(minutes / 60) % 12 || 12}:${String(minutes % 60).padStart(2, '0')}`;
    const timeRange = `${formatTime(hour * 60 + minute)}–${formatTime(end)} ${end % 1440 >= 720 ? 'PM' : 'AM'}`;
    return (
      <button
        className={`calendar-event${timed ? ' calendar-event-timed' : ''}${timed && event.duration <= 30 ? ' calendar-event-compact' : ''}`}
        data-calendar={event.calendar}
        style={
          timed
            ? {
                top: `${(minute / 60) * 100}%`,
                height: `${(event.duration / 60) * 84 - 4}px`,
              }
            : undefined
        }
        key={event.id}
        onClick={() => setSelected(event)}
        aria-label={`${event.title}, ${event.time}, ${event.duration} minutes, ${event.calendar}`}
      >
        <span>{timeRange}</span>
        <strong>{event.title}</strong>
      </button>
    );
  }

  return (
    <>
      <div className="workspace-heading calendar-heading">
        <div>
          <h2>My Calendar</h2>
          <p>A little space for everything on your schedule.</p>
        </div>
        <Button onClick={() => setAddOpen(true)}>
          <Plus aria-hidden="true" />
          Add event
        </Button>
      </div>
      <div className="calendar-layout">
        <aside className="calendar-sidebar">
          <Card className="mini-calendar">
            <Calendar
              mode="single"
              required
              selected={date}
              onSelect={setDate}
              month={date}
              onMonthChange={setDate}
              today={previewToday}
              showOutsideDays={false}
              className="workspace-date-picker"
            />
          </Card>
          {[
            ['My calendars', 'Personal', 'Work · Studio'],
            ['Other calendars', 'Team availability', 'Holidays'],
          ].map(([heading, ...items]) => (
            <Card className="calendar-list" key={heading}>
              <h3>{heading}</h3>
              {items.map((item) => (
                <Label key={item}>
                  <Checkbox
                    checked={!hidden.includes(item)}
                    onCheckedChange={(checked) =>
                      setHidden((previous) =>
                        checked
                          ? previous.filter((value) => value !== item)
                          : [...previous, item],
                      )
                    }
                  />
                  {item}
                </Label>
              ))}
            </Card>
          ))}
        </aside>
        <div className="calendar-main">
          <div className="calendar-range">
            <div className="calendar-period">
              <h3>{monthLabel(date)}</h3>
              <div className="calendar-period-controls">
                <Button
                  variant="outline"
                  size="icon-sm"
                  aria-label="Previous period"
                  onClick={() => navigate(-1)}
                >
                  <ChevronLeft />
                </Button>
                <Button variant="outline" onClick={() => setDate(previewToday)}>
                  Today
                </Button>
                <Button
                  variant="outline"
                  size="icon-sm"
                  aria-label="Next period"
                  onClick={() => navigate(1)}
                >
                  <ChevronRight />
                </Button>
              </div>
            </div>
            <div className="calendar-actions">
              <ToggleGroup
                type="single"
                value={view}
                onValueChange={(value) => {
                  if (value) setView(value);
                }}
                variant="outline"
                className="calendar-view-toggle"
                aria-label="Calendar view"
              >
                {['Day', 'Week', 'Month'].map((label) => (
                  <ToggleGroupItem
                    key={label}
                    value={label}
                    aria-label={`${label} view`}
                  >
                    {label}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
            </div>
          </div>
          <div className="calendar-caption">
            <span>
              <CalendarDays aria-hidden="true" />
              {title}
            </span>
            <span>Local time</span>
          </div>
          <div
            ref={scrollRef}
            className={`calendar-scroll${view !== 'Month' ? ' calendar-time-scroll' : ''}`}
            tabIndex={0}
            role="region"
            aria-label={`${view} calendar, local time`}
          >
            {view === 'Month' ? (
              <div className="month-grid">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(
                  (day) => (
                    <strong key={day}>{day}</strong>
                  ),
                )}
                {monthDays.map((day) => (
                  <div
                    className={
                      day.getMonth() !== date.getMonth() ? 'outside-month' : ''
                    }
                    key={dateKey(day)}
                  >
                    <button
                      onClick={() => {
                        setDate(day);
                        setView('Day');
                      }}
                    >
                      {day.getDate()}
                    </button>
                    {visibleEvents
                      .filter((event) => event.date === dateKey(day))
                      .map((event) => eventButton(event))}
                  </div>
                ))}
              </div>
            ) : (
              <div
                className={`week-grid ${view === 'Day' ? 'day-grid' : ''}`}
                style={{
                  gridTemplateColumns: `60px repeat(${days.length}, minmax(0, 1fr))`,
                }}
              >
                <div className="calendar-day-label">Time</div>
                {days.map((day) => (
                  <div
                    className="calendar-day-label"
                    key={dateKey(day)}
                    data-today={dateKey(day) === dateKey(previewToday)}
                  >
                    <span>
                      {day.toLocaleDateString('en-US', { weekday: 'short' })}
                    </span>
                    <strong>{day.getDate()}</strong>
                  </div>
                ))}
                {Array.from({ length: 24 }, (_, i) => i).map((hour) => (
                  <div className="time-row" key={hour}>
                    <div className="hour-label">{hourLabel(hour)}</div>
                    {days.map((day) => (
                      <div
                        className="time-cell"
                        data-weekend={day.getDay() === 0 || day.getDay() === 6}
                        key={dateKey(day)}
                      >
                        {visibleEvents
                          .filter(
                            (event) =>
                              event.date === dateKey(day) &&
                              Number(event.time.split(':')[0]) === hour,
                          )
                          .map((event) => eventButton(event, true))}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="preview-dialog">
          <DialogTitle>Add an event</DialogTitle>
          <DialogDescription>
            Create an event in your preview calendar.
          </DialogDescription>
          <form
            className="form-stack"
            onSubmit={(e) => {
              e.preventDefault();
              const values = new FormData(e.currentTarget);
              setEvents((previous) => [
                ...previous,
                {
                  id: Date.now(),
                  title: String(values.get('title')).trim(),
                  date: String(values.get('date')),
                  time: String(values.get('time')),
                  calendar,
                  duration: 30,
                },
              ]);
              setDate(new Date(`${values.get('date')}T12:00:00`));
              setAddOpen(false);
            }}
          >
            <div className="form-field">
              <Label htmlFor="event-title">Title</Label>
              <Input
                id="event-title"
                name="title"
                required
                pattern=".*\S.*"
                placeholder="Project planning"
              />
            </div>
            <div className="form-field">
              <Label htmlFor="event-date">Date</Label>
              <Input
                id="event-date"
                type="date"
                name="date"
                required
                defaultValue={dateKey(date)}
              />
            </div>
            <div className="form-field">
              <Label htmlFor="event-time">Time</Label>
              <Input
                id="event-time"
                type="time"
                name="time"
                required
                defaultValue="16:00"
              />
            </div>
            <div className="form-field">
              <Label htmlFor="event-calendar">Calendar</Label>
              <Select value={calendar} onValueChange={setCalendar}>
                <SelectTrigger id="event-calendar">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Personal">Personal · Gmail</SelectItem>
                  <SelectItem value="Work · Studio">Work · Studio</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit">Save event</Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setAddOpen(false)}
            >
              Cancel
            </Button>
          </form>
        </DialogContent>
      </Dialog>
      <Dialog
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
        }}
      >
        <DialogContent className="preview-dialog">
          <DialogTitle>{selected?.title}</DialogTitle>
          <DialogDescription>
            {selected?.date} · {selected?.time} · {selected?.duration} minutes
          </DialogDescription>
          <p>{selected?.calendar}</p>
          <Button onClick={() => setSelected(null)}>Done</Button>
        </DialogContent>
      </Dialog>
    </>
  );
}

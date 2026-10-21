import Link from 'next/link';
import GlassIcon from '@/components/GlassIcon';
import { ArrowUpRight } from 'lucide-react';
import Grainient from '@/components/Grainient';
import FloatingNavbar from '@/components/FloatingNavbar';
import SiteFooter from '@/components/SiteFooter';
import { Section } from '@/components/ui/Section';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const steps = [
  ['Connect your inbox', 'Bring incoming messages into one clear workflow.'],
  [
    'Let AI do the groundwork',
    'Emails are sorted and replies are drafted for review.',
  ],
  ['You make the final call', 'Approve, edit, or reject. You stay in control.'],
];
const services = [
  [
    'ORGANIZE',
    'Smart sorting',
    'Keep priorities visible. Your assistant reads incoming email and organizes it into a clear, manageable inbox.',
  ],
  [
    'RESPOND',
    'Replies, ready to review',
    'Skip the blank page. Get a drafted response you can approve, edit, or reject before anything is sent.',
  ],
  [
    'SCHEDULE',
    'Calendar-aware help',
    'When scheduling comes up, your assistant checks your calendar to help prepare a practical reply.',
  ],
];

export default function Home() {
  return (
    <main className="landing">
      <FloatingNavbar />
      <section id="home" className="hero" aria-labelledby="hero-title">
        <div className="hero-background" aria-hidden="true">
          <Grainient
            color1="#6ea1cb"
            color2="#12246e"
            color3="#020f2b"
            timeSpeed={1.5}
            grainAmount={0.06}
            contrast={1.4}
            zoom={0.9}
          />
        </div>
        <div className="hero-copy">
          <span className="glass-badge">AI email assistant</span>
          <h1 id="hero-title">
            Reach inbox zero without
            <br className="desktop-break" /> writing a single reply.
          </h1>
          <p>
            Your AI assistant sorts email, drafts responses, and checks your
            calendar.
          </p>
          <Button variant="secondary" asChild className="explore">
            <a href="#about">Explore how it works ↓</a>
          </Button>
          <small>
            Review every reply. Nothing sends without your approval.
          </small>
        </div>
      </section>
      <Section
        id="about"
        eyebrow="01 / ABOUT"
        title="What is Inbox Zero?"
        description="Email should move your day forward, not take it over. Inbox Zero turns a constant stream of messages into a simple flow: sorted, drafted, and ready for your decision."
        className="landing-section"
      >
        <Card className="steps glass-surface">
          {steps.map(([title, copy]) => (
            <article key={title}>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </Card>
      </Section>
      <Section
        id="services"
        eyebrow="02 / SERVICES"
        title="What Inbox Zero does."
        description="From the first incoming message to the final reply."
        className="landing-section services"
      >
        <div className="service-grid">
          {services.map(([label, title, copy]) => (
            <Card
              className="service-card glass-surface"
              data-tone={
                label === 'RESPOND'
                  ? 'violet'
                  : label === 'SCHEDULE'
                    ? 'mint'
                    : 'blue'
              }
              key={label}
            >
              <GlassIcon
                name={
                  label === 'ORGANIZE'
                    ? 'inbox'
                    : label === 'RESPOND'
                      ? 'send'
                      : 'calendar'
                }
                tone={
                  label === 'RESPOND'
                    ? 'violet'
                    : label === 'SCHEDULE'
                      ? 'mint'
                      : 'blue'
                }
              />
              <p className="eyebrow">{label}</p>
              <h3>{title}</h3>
              <p>{copy}</p>
            </Card>
          ))}
        </div>
        <Card className="closing glass-surface">
          <h3>Make space for a better day.</h3>
          <p>Your inbox can wait less. You can do more.</p>
          <Button asChild className="light gap-2">
            <Link href="/auth/sign-up">
              <span>Get started</span>
              <ArrowUpRight aria-hidden="true" />
            </Link>
          </Button>
        </Card>
      </Section>
      <SiteFooter />
    </main>
  );
}

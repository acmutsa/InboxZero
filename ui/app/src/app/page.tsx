import Link from 'next/link';
import GlassIcon from '@/components/GlassIcon';
import { ArrowDown, ArrowUpRight, Check, FilePenLine, Link2, ShieldCheck } from 'lucide-react';
import LandingInboxPreview from '@/components/LandingInboxPreview';
import Grainient from '@/components/Grainient';
import FloatingNavbar from '@/components/FloatingNavbar';
import SiteFooter from '@/components/SiteFooter';
import { Section } from '@/components/ui/Section';
import { Card } from '@/components/ui/card';
import landingStyles from '@/app/page.module.css';

const steps = [
  { title: 'Connect', copy: 'Bring your Gmail and Outlook accounts into one workspace.', icon: Link2 },
  { title: 'Review', copy: 'Find sorted messages and suggested replies ready for a look.', icon: FilePenLine },
  { title: 'Approve', copy: 'Make an edit or give the final okay. Every reply is your call.', icon: Check },
];
const services = [
  ['ORGANIZE', 'Find what matters.', 'Keep important messages in view and everyday noise in its place.'],
  ['RESPOND', 'Start with a draft.', 'Review a suggested reply instead of starting from a blank page.'],
  ['SCHEDULE', 'Make room to meet.', 'Calendar context helps you review scheduling replies with confidence.'],
];

export default function Home() {
  return (
    <main className="landing">
      <FloatingNavbar />
      <section id="home" className={landingStyles['hero']} aria-labelledby="hero-title">
        <div className={landingStyles['hero-background']} aria-hidden="true">
          <Grainient
            timeSpeed={1.5}
            grainAmount={0.06}
            contrast={1.4}
            zoom={0.9}
          />
        </div>
        <div className={landingStyles['hero-copy']}>
          <h1 id="hero-title" className="motion-safe:animate-in motion-safe:fade-in-0 motion-safe:duration-[1200ms] motion-safe:ease-out">Your inbox, handled.</h1>
          <p>
            Email sorted. Replies drafted. Calendar checked.
            <br />You make the final call.
          </p>
          <div className={landingStyles['hero-actions']}>
            <Link href="/auth/sign-up" className={landingStyles['light']}>
              Get started <ArrowUpRight aria-hidden="true" />
            </Link>
            <a href="#about" className={landingStyles['secondary-link']}>
              See how it works <ArrowDown aria-hidden="true" />
            </a>
          </div>
          <small className={landingStyles['approval-note']}>
            <ShieldCheck aria-hidden="true" /> Nothing sends without your approval.
          </small>
        </div>
        <div className={landingStyles['product-preview']}>
          <h2 className="sr-only">Inbox workspace preview</h2>
          <LandingInboxPreview />
        </div>
      </section>
      <Section
        id="about"
        title="Three steps to a clearer inbox."
        description="Less time managing email. More space for the rest of your day."
        className={landingStyles['landing-section']}
      >
        <Card className={`${landingStyles['steps']} glass-surface`}>
          {steps.map(({ title, copy, icon: Icon }, index) => (
            <article key={title}>
              <div className={landingStyles['step-heading']}><span>0{index + 1}</span><Icon aria-hidden="true" /></div>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </Card>
      </Section>
      <Section
        id="services"
        title="A head start on every message."
        description="A little help with the work behind your inbox."
        className={`${landingStyles['landing-section']} ${landingStyles['services']}`}
      >
        <div className={landingStyles['service-grid']}>
          {services.map(([label, title, copy]) => (
            <Card
              className={`${landingStyles['service-card']} glass-surface`}
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
              <div className={landingStyles['feature-example']}>
                {label === 'ORGANIZE' ? (
                  <><span>Project update <small>Important</small></span><span>Weekly digest <small>Newsletter</small></span><span>Order confirmation <small>Receipt</small></span></>
                ) : label === 'RESPOND' ? (
                  <><span className={landingStyles['example-label']}>Suggested reply</span><p>“Thanks, Alex. I’ll share an update before our check-in.”</p><span className={landingStyles['example-footer']}><Check aria-hidden="true" /> Ready for your review</span></>
                ) : (
                  <><span className={landingStyles['example-label']}>Friday catch-up</span><strong>10:00–10:30 AM</strong><span className={landingStyles['example-footer']}><Check aria-hidden="true" /> Calendar checked</span></>
                )}
              </div>
            </Card>
          ))}
        </div>
        <Card className={`${landingStyles['closing']} glass-surface`}>
          <h3>Make space for a better day.</h3>
          <p>Your inbox can wait less. You can do more.</p>
          <Link href="/auth/sign-up" className={landingStyles['light']}>
              <span>Get started</span>
              <ArrowUpRight aria-hidden="true" />
          </Link>
        </Card>
      </Section>
      <SiteFooter />
    </main>
  );
}

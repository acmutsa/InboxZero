import { SignInButton, SignUpButton, Show, UserButton } from "@clerk/nextjs";
import Grainient from "@/components/Grainient";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col bg-[#030711] text-white">
      {/* Nav */}
      <header className="fixed inset-x-0 top-0 z-20 border-b border-white/10 bg-[#030711]/60 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <span className="text-sm font-semibold tracking-tight text-white">
            Inbox Zero
          </span>
          <div className="flex items-center gap-3">
            <Show when="signed-out">
              <SignInButton>
                <button className="rounded-full px-4 py-2 text-sm font-medium text-white/90 transition-colors hover:text-white">
                  Sign in
                </button>
              </SignInButton>
              <SignUpButton>
                <button className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100">
                  Get started
                </button>
              </SignUpButton>
            </Show>
            <Show when="signed-in">
              <a
                href="/profile"
                className="rounded-full px-4 py-2 text-sm font-medium text-white/90 transition-colors hover:text-white"
              >
                Profile
              </a>
              <UserButton />
            </Show>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
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

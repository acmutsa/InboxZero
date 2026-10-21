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

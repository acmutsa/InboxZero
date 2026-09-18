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
          <a
            href="#"
            className="rounded-full bg-white px-4 py-2 text-sm font-medium text-[#030711] transition-colors hover:bg-sky-100"
          >
            Get started
          </a>
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

        <div className="relative z-10 mx-auto flex max-w-3xl flex-col items-center px-6 py-32 text-center">
          <span className="mb-6 rounded-full border border-white/20 bg-white/5 px-4 py-1.5 text-xs font-medium tracking-wide text-sky-200">
            AI email assistant
          </span>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-6xl">
            Reach inbox zero without writing a single reply.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-200/90">
            Inbox Zero reads every email as it arrives, sorts it, and drafts the reply for
            you — checking your calendar when scheduling is involved. You just approve,
            edit, or reject. Nothing ever sends without your click.
          </p>
        </div>
      </section>
    </div>
  );
}
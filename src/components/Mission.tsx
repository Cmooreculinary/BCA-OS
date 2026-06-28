import { Reveal } from './Reveal';

/** Mission — Adeshina's House. Heartfelt, faith-rooted, understated. */
export function Mission() {
  return (
    <section
      id="mission"
      className="relative overflow-hidden border-t border-bone/10 bg-bone py-24 text-obsidian sm:py-32"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-fire/10 blur-[120px]"
      />
      <div className="relative mx-auto max-w-4xl px-5 sm:px-8">
        <Reveal>
          <div className="flex items-center gap-3">
            <span className="h-px w-8 bg-fire" aria-hidden="true" />
            <span className="font-mono text-xs uppercase tracking-[0.25em] text-fire">
              The Mission · Adeshina's House
            </span>
          </div>
        </Reveal>

        <Reveal>
          <h2 className="mt-6 max-w-3xl text-4xl text-obsidian sm:text-5xl md:text-6xl">
            Ten percent goes <span className="text-fire">home.</span>
          </h2>
        </Reveal>

        <Reveal>
          <div className="mt-8 max-w-2xl space-y-5 text-lg leading-relaxed text-obsidian/75">
            <p>
              Ten percent of everything Blue Collar Apps Co. earns supports{' '}
              <strong className="font-medium text-obsidian">Adeshina's House</strong> — homes for
              orphans and survivors of violence in Jos, Nigeria. A safe bed, a warm plate, and
              someone in your corner.
            </p>
            <p>
              This isn't a marketing line bolted on at the end. It's the reason the work exists.
              Hospitality means making room for people. We build software so that table can keep
              getting bigger — and so a kid in Jos has a place to call home.
            </p>
            <p className="font-mono text-sm uppercase tracking-[0.15em] text-obsidian/55">
              Build well. Feed people. Make room.
            </p>
          </div>
        </Reveal>

        <Reveal>
          <div className="mt-12 grid gap-px overflow-hidden border border-obsidian/10 sm:grid-cols-3">
            {[
              { figure: '10%', label: 'Of proceeds, pledged' },
              { figure: 'Jos', label: 'Plateau State, Nigeria' },
              { figure: '∞', label: 'Room at the table' },
            ].map((stat) => (
              <div key={stat.label} className="bg-bone p-8">
                <p className="font-display text-5xl text-fire">{stat.figure}</p>
                <p className="mt-2 font-mono text-xs uppercase tracking-[0.2em] text-obsidian/55">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

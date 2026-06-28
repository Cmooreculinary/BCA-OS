import { PILLARS } from '../data/catalog';
import { Reveal } from './Reveal';
import { SectionHeading } from './SectionHeading';

/** "The Trench Edge" — the value pillars that define the BCA difference. */
export function TrenchEdge() {
  return (
    <section id="edge" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal>
          <SectionHeading
            kicker="The Trench Edge"
            title={
              <>
                Why it <span className="text-fire">cuts</span> different.
              </>
            }
            lead="Every product in the ecosystem shares the same edge. This is what 40+ years at the pass builds into software."
          />
        </Reveal>

        <ul className="mt-16 grid gap-px overflow-hidden border border-bone/10 sm:grid-cols-2">
          {PILLARS.map((pillar, i) => (
            <Reveal as="li" key={pillar.id} delay={i * 90}>
              <article className="group h-full bg-obsidian-800/40 p-8 transition-colors duration-300 hover:bg-obsidian-700/60 sm:p-10">
                <div className="flex items-baseline justify-between">
                  <span className="font-mono text-sm text-fire">{pillar.index}</span>
                  <span className="h-px w-12 bg-bone/15 transition-all duration-300 group-hover:w-20 group-hover:bg-fire" />
                </div>
                <h3 className="mt-6 text-3xl sm:text-4xl">{pillar.title}</h3>
                <p className="mt-4 text-base leading-relaxed text-bone/60">{pillar.body}</p>
              </article>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}

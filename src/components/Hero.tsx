import { PRODUCTS } from '../data/catalog';

/** Top-of-page hero: wordmark statement, tagline, positioning, dual CTAs. */
export function Hero() {
  const liveCount = PRODUCTS.filter((p) => p.status === 'LIVE').length;
  const buildCount = PRODUCTS.filter((p) => p.status === 'IN BUILD').length;

  return (
    <section
      id="home"
      className="relative flex min-h-screen items-center overflow-hidden pt-24"
    >
      {/* Background flourishes */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute -left-40 top-1/4 h-96 w-96 rounded-full bg-fire/10 blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-fire/5 blur-[120px]" />
        {/* faint blueprint grid */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              'linear-gradient(#F5F2EC 1px, transparent 1px), linear-gradient(90deg, #F5F2EC 1px, transparent 1px)',
            backgroundSize: '64px 64px',
          }}
        />
      </div>

      <div className="relative mx-auto w-full max-w-7xl px-5 sm:px-8">
        <div className="max-w-4xl">
          <div className="flex items-center gap-3 animate-fade-up">
            <span className="h-px w-10 bg-fire" aria-hidden="true" />
            <span className="mono-label text-fire">
              Hospitality &amp; Foodservice Software Ecosystem
            </span>
          </div>

          <h1
            className="mt-6 text-[clamp(3.5rem,11vw,9rem)] leading-[0.88] animate-fade-up"
            style={{ animationDelay: '80ms' }}
          >
            Software, built
            <br />
            in the <span className="text-fire">trenches.</span>
          </h1>

          <p
            className="mt-8 max-w-2xl text-lg leading-relaxed text-bone/70 animate-fade-up sm:text-xl"
            style={{ animationDelay: '160ms' }}
          >
            Blue Collar Apps Co. is a connected suite of tools for the people who run
            hospitality — engineered from 40+ years on the line by a CIA-trained chef. Not
            generic SaaS bent toward food. Built from the operator's reality, agent-ready from
            day one.
          </p>

          <div
            className="mt-10 flex flex-col gap-4 animate-fade-up sm:flex-row"
            style={{ animationDelay: '240ms' }}
          >
            <a href="#catalog" className="btn-primary">
              Explore the Ecosystem
              <span aria-hidden="true">→</span>
            </a>
            <a href="#notify" className="btn-ghost">
              Get Notified
            </a>
          </div>

          {/* Live status strip */}
          <dl
            className="mt-16 flex flex-wrap gap-x-12 gap-y-6 border-t border-bone/10 pt-8 animate-fade-up"
            style={{ animationDelay: '320ms' }}
          >
            <div>
              <dt className="mono-label">Shipping now</dt>
              <dd className="mt-1 font-display text-4xl text-fire">
                {liveCount.toString().padStart(2, '0')}
              </dd>
            </div>
            <div>
              <dt className="mono-label">In build</dt>
              <dd className="mt-1 font-display text-4xl text-bone">
                {buildCount.toString().padStart(2, '0')}
              </dd>
            </div>
            <div>
              <dt className="mono-label">In the ecosystem</dt>
              <dd className="mt-1 font-display text-4xl text-bone">
                {PRODUCTS.length.toString().padStart(2, '0')}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Scroll cue */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-center">
        <span className="mono-label block animate-pulse-dot">scroll</span>
      </div>
    </section>
  );
}

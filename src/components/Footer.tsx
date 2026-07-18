import { NAV_LINKS } from '../data/nav';
import { Wordmark } from './Wordmark';

/** Footer: nav, brand, and an understated faith-rooted close. */
export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-bone/10 bg-obsidian-800/50">
      <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8">
        <div className="flex flex-col justify-between gap-12 md:flex-row">
          <div className="max-w-sm">
            <a href="#home" aria-label="Blue Collar Apps Co. — home">
              <Wordmark />
            </a>
            <p className="mt-5 text-sm leading-relaxed text-bone/50">
              A hospitality &amp; foodservice software ecosystem, engineered from the operator's
              reality. Built in the trenches — for the people who run the room.
            </p>
          </div>

          <nav aria-label="Footer">
            <span className="mono-label">Navigate</span>
            <ul className="mt-4 grid grid-cols-2 gap-x-12 gap-y-3">
              {NAV_LINKS.map((link) => (
                <li key={link.id}>
                  <a
                    href={`#${link.id}`}
                    className="font-mono text-xs uppercase tracking-[0.15em] text-bone/55 transition-colors hover:text-fire"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        <div className="mt-12 trench-rule" />

        <div className="mt-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-bone/40">
            © {year} Blue Collar Apps Co. · All rights reserved.
          </p>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-bone/40">
            10% to Adeshina's House · Built well, to feed people.
          </p>
        </div>
      </div>
    </footer>
  );
}

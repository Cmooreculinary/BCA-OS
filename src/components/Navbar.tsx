import { useEffect, useState } from 'react';
import { NAV_LINKS } from '../data/nav';
import { Wordmark } from './Wordmark';

interface NavbarProps {
  activeId: string;
}

/** Sticky top nav with active-section highlight and a mobile drawer. */
export function Navbar({ activeId }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close the mobile drawer whenever the active section changes (i.e. after a jump).
  useEffect(() => {
    setMenuOpen(false);
  }, [activeId]);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-40 transition-colors duration-300 ${
        scrolled || menuOpen
          ? 'border-b border-bone/10 bg-obsidian/90 backdrop-blur'
          : 'border-b border-transparent bg-transparent'
      }`}
    >
      <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
        <a href="#home" aria-label="Blue Collar Apps Co. — home" className="group">
          <Wordmark />
        </a>

        {/* Desktop links */}
        <ul className="hidden items-center gap-8 lg:flex">
          {NAV_LINKS.slice(1).map((link) => {
            const isActive = activeId === link.id;
            return (
              <li key={link.id}>
                <a
                  href={`#${link.id}`}
                  aria-current={isActive ? 'location' : undefined}
                  className={`relative font-mono text-xs uppercase tracking-[0.18em] transition-colors ${
                    isActive ? 'text-fire' : 'text-bone/60 hover:text-bone'
                  }`}
                >
                  {link.label}
                  <span
                    className={`absolute -bottom-2 left-0 h-px bg-fire transition-all duration-300 ${
                      isActive ? 'w-full' : 'w-0'
                    }`}
                  />
                </a>
              </li>
            );
          })}
        </ul>

        <a href="#notify" className="hidden btn-primary px-5 py-2.5 text-xs lg:inline-flex">
          Get Notified
        </a>

        {/* Mobile toggle */}
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center lg:hidden"
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span className="relative block h-4 w-6">
            <span
              className={`absolute left-0 block h-0.5 w-6 bg-fire transition-transform duration-300 ${
                menuOpen ? 'top-2 rotate-45' : 'top-0'
              }`}
            />
            <span
              className={`absolute left-0 top-2 block h-0.5 w-6 bg-bone transition-opacity duration-200 ${
                menuOpen ? 'opacity-0' : 'opacity-100'
              }`}
            />
            <span
              className={`absolute left-0 block h-0.5 w-6 bg-fire transition-transform duration-300 ${
                menuOpen ? 'top-2 -rotate-45' : 'top-4'
              }`}
            />
          </span>
        </button>
      </nav>

      {/* Mobile drawer */}
      <div
        id="mobile-menu"
        aria-hidden={!menuOpen}
        inert={!menuOpen}
        className={`overflow-hidden border-t border-bone/10 bg-obsidian/95 backdrop-blur lg:hidden ${
          menuOpen ? 'max-h-96' : 'max-h-0'
        } transition-[max-height] duration-300 ease-in-out`}
      >
        <ul className="flex flex-col px-5 py-2">
          {NAV_LINKS.slice(1).map((link) => (
            <li key={link.id} className="border-b border-bone/5 last:border-0">
              <a
                href={`#${link.id}`}
                className={`block py-4 font-mono text-sm uppercase tracking-[0.18em] ${
                  activeId === link.id ? 'text-fire' : 'text-bone/70'
                }`}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </header>
  );
}

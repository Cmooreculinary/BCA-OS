import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { TrenchEdge } from './components/TrenchEdge';
import { Catalog } from './components/Catalog';
import { ToolFinder } from './components/ToolFinder';
import { Mission } from './components/Mission';
import { GetNotified } from './components/GetNotified';
import { Footer } from './components/Footer';
import { NAV_LINKS } from './data/nav';
import { useActiveSection } from './hooks/useActiveSection';

/**
 * Single-page app shell. Sections are rendered in order; the sticky nav tracks
 * the active section via IntersectionObserver, and in-page anchor links + CSS
 * `scroll-smooth` handle the "section routing."
 */
export default function App() {
  const activeId = useActiveSection(NAV_LINKS.map((l) => l.id));

  return (
    <div className="grain relative min-h-screen bg-obsidian">
      <a
        href="#catalog"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:bg-fire focus:px-4 focus:py-2 focus:font-mono focus:text-xs focus:uppercase focus:text-obsidian"
      >
        Skip to content
      </a>

      <Navbar activeId={activeId} />

      <main>
        <Hero />
        <TrenchEdge />
        <Catalog />
        <ToolFinder />
        <Mission />
        <GetNotified />
      </main>

      <Footer />
    </div>
  );
}

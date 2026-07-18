import { useEffect, useState } from 'react';

/**
 * Tracks which section is currently in view so the nav can highlight it.
 * Uses an IntersectionObserver tuned so a section counts as "active" once it
 * occupies the upper-middle band of the viewport.
 */
export function useActiveSection(sectionIds: string[]): string {
  const [active, setActive] = useState<string>(sectionIds[0] ?? '');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Pick the most-visible intersecting section.
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) {
          setActive(visible[0].target.id);
        }
      },
      {
        // Bias the "active" band toward the top third of the viewport.
        rootMargin: '-45% 0px -45% 0px',
        threshold: [0, 0.25, 0.5, 1],
      },
    );

    const nodes = sectionIds
      .map((id) => document.getElementById(id))
      .filter((n): n is HTMLElement => n !== null);

    nodes.forEach((n) => observer.observe(n));
    return () => observer.disconnect();
  }, [sectionIds]);

  return active;
}

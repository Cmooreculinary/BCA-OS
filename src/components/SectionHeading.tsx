import type { ReactNode } from 'react';

interface SectionHeadingProps {
  /** Mono kicker label above the title. */
  kicker: string;
  title: ReactNode;
  /** Optional supporting copy under the title. */
  lead?: ReactNode;
  align?: 'left' | 'center';
}

/** Shared section header: mono kicker + Bebas title + optional lead. */
export function SectionHeading({ kicker, title, lead, align = 'left' }: SectionHeadingProps) {
  return (
    <div className={align === 'center' ? 'mx-auto max-w-2xl text-center' : 'max-w-2xl'}>
      <div
        className={`flex items-center gap-3 ${align === 'center' ? 'justify-center' : ''}`}
      >
        <span className="h-px w-8 bg-fire" aria-hidden="true" />
        <span className="mono-label text-fire">{kicker}</span>
      </div>
      <h2 className="mt-4 text-4xl sm:text-5xl md:text-6xl">{title}</h2>
      {lead && <p className="mt-5 text-base leading-relaxed text-bone/60 sm:text-lg">{lead}</p>}
    </div>
  );
}

import type { ProductStatus } from '../types';

interface StatusBadgeProps {
  status: ProductStatus;
}

/**
 * Status badge with the brand's status language:
 *  LIVE     → solid Fire Orange
 *  IN BUILD → amber outline
 *  CONCEPT  → muted gray
 */
export function StatusBadge({ status }: StatusBadgeProps) {
  const styles: Record<ProductStatus, string> = {
    LIVE: 'bg-fire text-obsidian border-fire',
    'IN BUILD': 'bg-transparent text-amber-edge border-amber-edge',
    CONCEPT: 'bg-transparent text-bone/40 border-bone/25',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 border px-2 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] ${styles[status]}`}
    >
      <span
        aria-hidden="true"
        className={`h-1.5 w-1.5 rounded-full ${
          status === 'LIVE'
            ? 'animate-pulse-dot bg-obsidian'
            : status === 'IN BUILD'
              ? 'bg-amber-edge'
              : 'bg-bone/40'
        }`}
      />
      {status}
    </span>
  );
}

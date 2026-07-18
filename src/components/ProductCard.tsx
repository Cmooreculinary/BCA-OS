import type { Product } from '../types';
import { StatusBadge } from './StatusBadge';

interface ProductCardProps {
  product: Product;
}

/** A single catalog card: name + abbr, category tag, pitch, status badge. */
export function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="trench-card flex h-full flex-col p-6">
      <div className="flex items-start justify-between gap-4">
        <span className="mono-label">{product.category}</span>
        <StatusBadge status={product.status} />
      </div>

      <h3 className="mt-6 text-2xl sm:text-3xl">
        {product.name}
        {product.abbr && (
          <span className="ml-2 align-middle font-mono text-xs tracking-[0.2em] text-fire">
            {product.abbr}
          </span>
        )}
      </h3>

      <p className="mt-3 flex-1 text-sm leading-relaxed text-bone/60">{product.pitch}</p>

      <div className="mt-6 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-bone/35">
        <span className="h-1 w-1 bg-fire" aria-hidden="true" />
        BCA Ecosystem
      </div>
    </article>
  );
}

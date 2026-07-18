import { useMemo, useState } from 'react';
import { CATEGORIES, PRODUCTS, STATUSES } from '../data/catalog';
import type { Category, ProductStatus } from '../types';
import { ProductCard } from './ProductCard';
import { Reveal } from './Reveal';
import { SectionHeading } from './SectionHeading';

type CategoryFilter = Category | 'All';
type StatusFilter = ProductStatus | 'All';

/** Reusable filter chip. */
function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`border px-4 py-2 font-mono text-[11px] uppercase tracking-[0.15em] transition-colors duration-200 ${
        active
          ? 'border-fire bg-fire text-obsidian'
          : 'border-bone/15 text-bone/55 hover:border-bone/40 hover:text-bone'
      }`}
    >
      {children}
    </button>
  );
}

/** Filterable product grid. Filters update the grid instantly. */
export function Catalog() {
  const [category, setCategory] = useState<CategoryFilter>('All');
  const [status, setStatus] = useState<StatusFilter>('All');

  const filtered = useMemo(
    () =>
      PRODUCTS.filter(
        (p) =>
          (category === 'All' || p.category === category) &&
          (status === 'All' || p.status === status),
      ),
    [category, status],
  );

  const resetFilters = () => {
    setCategory('All');
    setStatus('All');
  };

  return (
    <section id="catalog" className="relative border-t border-bone/10 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <Reveal>
          <SectionHeading
            kicker="Product Catalog"
            title={
              <>
                The <span className="text-fire">ecosystem.</span>
              </>
            }
            lead="One connected stack for the whole operation. Filter by where it fits and how far along it is."
          />
        </Reveal>

        {/* Filters */}
        <Reveal>
          <div className="mt-12 space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="mono-label mr-2 w-full sm:w-auto">Category</span>
              <Chip active={category === 'All'} onClick={() => setCategory('All')}>
                All
              </Chip>
              {CATEGORIES.map((c) => (
                <Chip key={c} active={category === c} onClick={() => setCategory(c)}>
                  {c}
                </Chip>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="mono-label mr-2 w-full sm:w-auto">Status</span>
              <Chip active={status === 'All'} onClick={() => setStatus('All')}>
                All
              </Chip>
              {STATUSES.map((s) => (
                <Chip key={s} active={status === s} onClick={() => setStatus(s)}>
                  {s}
                </Chip>
              ))}
            </div>
          </div>
        </Reveal>

        {/* Result count */}
        <p className="mt-8 font-mono text-xs uppercase tracking-[0.2em] text-bone/40">
          {filtered.length} / {PRODUCTS.length} products
        </p>

        {/* Grid or empty state */}
        {filtered.length > 0 ? (
          <ul className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((product, i) => (
              <Reveal as="li" key={product.id} delay={(i % 3) * 80}>
                <ProductCard product={product} />
              </Reveal>
            ))}
          </ul>
        ) : (
          <div className="mt-6 border border-dashed border-bone/15 p-12 text-center">
            <p className="font-display text-3xl text-bone">Nothing on the pass.</p>
            <p className="mx-auto mt-3 max-w-md text-sm text-bone/55">
              No products match that combination yet. Clear the filters to see the full
              ecosystem.
            </p>
            <button type="button" onClick={resetFilters} className="btn-ghost mt-6">
              Clear filters
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

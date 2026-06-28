// Shared domain types for the BCA marketing site.

export type ProductStatus = 'LIVE' | 'IN BUILD' | 'CONCEPT';

export type Category =
  | 'Professional Suite'
  | 'Life Management'
  | 'Consumer / DUSK Hub'
  | 'Emerging';

export interface Product {
  /** Short internal id, used as React key + filter value. */
  id: string;
  name: string;
  /** Optional shorthand / ticker shown after the name (e.g. "FTA"). */
  abbr?: string;
  /** One-line pitch. */
  pitch: string;
  category: Category;
  status: ProductStatus;
}

export interface Pillar {
  id: string;
  /** Mono index label, e.g. "01". */
  index: string;
  title: string;
  body: string;
}

export interface NavLink {
  id: string;
  label: string;
}

/** A single turn in the Tool Finder transcript. */
export interface ChatTurn {
  role: 'user' | 'bca';
  text: string;
}

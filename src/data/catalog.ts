import type { Category, Pillar, Product, ProductStatus } from '../types';

/**
 * The BCA product catalog. This array is the single source of truth for both
 * the Product Catalog grid AND the Tool Finder's grounding context — so the
 * AI can only ever recommend products that actually exist here.
 *
 * Hospitality-only. (TorqueVision / BrainForge intentionally excluded.)
 */
export const PRODUCTS: Product[] = [
  {
    id: 'footruck-apollo',
    name: 'Footruck Apollo',
    abbr: 'FTA',
    pitch: 'The Food Truck Launch Pad — startup toolkit + custom-shop builder.',
    category: 'Professional Suite',
    status: 'LIVE',
  },
  {
    id: 'venue-iq',
    name: 'Venue IQ',
    pitch: 'Event and venue operations dashboard for the people running the floor.',
    category: 'Professional Suite',
    status: 'IN BUILD',
  },
  {
    id: 'capkids',
    name: 'Captain Culinary Kids',
    abbr: 'CapKids',
    pitch: 'AI culinary learning for kids, ages 7–17 — skills before screens.',
    category: 'Emerging',
    status: 'IN BUILD',
  },
  {
    id: 'restaurateur-pro',
    name: 'Restaurateur Pro',
    pitch: 'Full-service restaurant operations suite, front to back of house.',
    category: 'Professional Suite',
    status: 'CONCEPT',
  },
  {
    id: 'hotel-resort-developer',
    name: 'Hotel / Resort Developer',
    pitch: 'Property operations and guest-experience platform for lodging.',
    category: 'Professional Suite',
    status: 'CONCEPT',
  },
  {
    id: 'maestro-vaultspace',
    name: 'Maestro + VaultSpace',
    pitch: 'Personal and life management with a persistent memory layer.',
    category: 'Life Management',
    status: 'CONCEPT',
  },
  {
    id: 'vine-barrel-foxhounds',
    name: 'Vine & Barrel / Foxhounds',
    pitch: 'Wine & beer pairing with the Som n Chef AI debate engine.',
    category: 'Consumer / DUSK Hub',
    status: 'IN BUILD',
  },
  {
    id: 'round-table',
    name: 'Round Table',
    pitch: "Digital members' club — dues, not subscriptions. Host-centric by design.",
    category: 'Consumer / DUSK Hub',
    status: 'CONCEPT',
  },
  {
    id: 'dusk',
    name: 'DUSK',
    pitch: 'The consumer hospitality hub — where guests meet the ecosystem.',
    category: 'Consumer / DUSK Hub',
    status: 'CONCEPT',
  },
  {
    id: 'fusebox',
    name: 'FUSEBOX',
    pitch: 'The utility layer powering the DUSK consumer hub.',
    category: 'Consumer / DUSK Hub',
    status: 'CONCEPT',
  },
  {
    id: 'valet-captain',
    name: 'Valet Captain',
    pitch: 'Valet and arrival operations — the first 90 seconds of the guest.',
    category: 'Professional Suite',
    status: 'CONCEPT',
  },
  {
    id: 'pubhub',
    name: 'PUBHUB',
    pitch: 'Bar and pub operations built for volume nights and tight teams.',
    category: 'Professional Suite',
    status: 'CONCEPT',
  },
  {
    id: 'plate-me',
    name: 'PLATE ME',
    pitch: 'Consumer dining feature — discover, decide, and dig in.',
    category: 'Consumer / DUSK Hub',
    status: 'CONCEPT',
  },
];

export const CATEGORIES: Category[] = [
  'Professional Suite',
  'Life Management',
  'Consumer / DUSK Hub',
  'Emerging',
];

export const STATUSES: ProductStatus[] = ['LIVE', 'IN BUILD', 'CONCEPT'];

export const PILLARS: Pillar[] = [
  {
    id: 'operator-built',
    index: '01',
    title: 'Operator-Built',
    body: 'Forty-plus years on the line and at the pass. Every product starts from a real operator problem, not a pitch deck. CIA-trained, trench-tested.',
  },
  {
    id: 'agent-ready',
    index: '02',
    title: 'Agent-Ready',
    body: 'Each tool is engineered for an AI agent fleet from day one — routing, memory, and policy baked into the OS so the software works while you sleep.',
  },
  {
    id: 'hospitality-native',
    index: '03',
    title: 'Hospitality-Native',
    body: 'Not generic SaaS bent toward food. Built in the language of covers, tickets, turns, and the guest — because hospitality is the whole point.',
  },
  {
    id: 'distribution-first',
    index: '04',
    title: 'Distribution-First',
    body: 'A connected ecosystem, not a pile of apps. One operator login reaches the whole stack — and the whole stack reaches the guest.',
  },
];

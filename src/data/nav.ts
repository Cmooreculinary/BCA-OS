import type { NavLink } from '../types';

/** Section anchors, in document order. Drives the nav + active-section logic. */
export const NAV_LINKS: NavLink[] = [
  { id: 'home', label: 'Home' },
  { id: 'edge', label: 'The Edge' },
  { id: 'catalog', label: 'Catalog' },
  { id: 'finder', label: 'Tool Finder' },
  { id: 'mission', label: 'Mission' },
  { id: 'notify', label: 'Get Notified' },
];

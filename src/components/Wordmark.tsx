interface WordmarkProps {
  /** Pixel size of the square mark. */
  size?: number;
  withText?: boolean;
}

/**
 * BCA wordmark: a sharp "trench" notch mark in Fire Orange + the lettering.
 * Pure SVG/markup so it stays crisp at any size.
 */
export function Wordmark({ size = 34, withText = true }: WordmarkProps) {
  return (
    <span className="inline-flex items-center gap-3">
      <svg
        width={size}
        height={size}
        viewBox="0 0 40 40"
        fill="none"
        aria-hidden="true"
        className="shrink-0"
      >
        <rect x="1" y="1" width="38" height="38" stroke="#EC5B13" strokeWidth="2" />
        {/* the trench cut */}
        <path d="M12 28 L20 12 L28 28" stroke="#EC5B13" strokeWidth="2.5" fill="none" />
        <path d="M16 28 L20 20 L24 28" stroke="#F5F2EC" strokeWidth="2" fill="none" />
      </svg>
      {withText && (
        <span className="flex flex-col leading-none">
          <span className="font-display text-xl tracking-display text-bone">Blue Collar Apps</span>
          <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-fire">
            Built in the Trenches
          </span>
        </span>
      )}
    </span>
  );
}

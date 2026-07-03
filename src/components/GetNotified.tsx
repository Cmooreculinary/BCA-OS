import { useState } from 'react';
import { Reveal } from './Reveal';
import { SectionHeading } from './SectionHeading';

type FormState = 'idle' | 'success';

/** Basic email shape check — good enough for a front-end stub. */
function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

/**
 * Get Notified — email capture (front-end stub).
 *
 * Currently stores the captured email in local component state only and shows
 * a success state. There is NO backend yet.
 *
 * TODO(backend): wire this to a real waitlist when the backend exists, e.g.
 *   POST /api/waitlist { email }            // store + dedupe
 *   or Stripe: create a Customer / Checkout waitlist hold.
 * Replace the body of `handleSubmit` below with the network call and keep the
 * same success/error UI states.
 */
export function GetNotified() {
  const [email, setEmail] = useState('');
  const [state, setState] = useState<FormState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [captured, setCaptured] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidEmail(email)) {
      setError('That email looks off. Mind checking it?');
      return;
    }
    setError(null);

    // --- front-end stub: store locally, no network. ---
    setCaptured((prev) => (prev.includes(email.trim()) ? prev : [...prev, email.trim()]));
    setState('success');
    // --- end stub ---
  };

  const reset = () => {
    setEmail('');
    setState('idle');
  };

  return (
    <section id="notify" className="relative border-t border-bone/10 py-24 sm:py-32">
      <div className="mx-auto max-w-3xl px-5 text-center sm:px-8">
        <Reveal>
          <SectionHeading
            align="center"
            kicker="Get Notified"
            title={
              <>
                Be first on the <span className="text-fire">pass.</span>
              </>
            }
            lead="Drop your email and we'll let you know as products go live. No spam, no daily blast — just the word when a tool is ready for service."
          />
        </Reveal>

        <Reveal>
          {state === 'success' ? (
            <div
              role="status"
              className="mx-auto mt-12 max-w-md border border-fire/40 bg-fire/5 p-8"
            >
              <p className="font-display text-4xl text-fire">You're on the list.</p>
              <p className="mt-3 text-sm text-bone/70">
                Order in. We'll call your ticket the moment there's something to serve.
              </p>
              <button type="button" onClick={reset} className="btn-ghost mt-6 text-xs">
                Add another email
              </button>
            </div>
          ) : (
            <form
              onSubmit={handleSubmit}
              noValidate
              className="mx-auto mt-12 flex max-w-lg flex-col gap-3 sm:flex-row"
            >
              <label htmlFor="notify-email" className="sr-only">
                Email address
              </label>
              <input
                id="notify-email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="you@youroperation.com"
                autoComplete="email"
                aria-invalid={error ? 'true' : undefined}
                aria-describedby={error ? 'notify-error' : undefined}
                className="flex-1 border border-bone/15 bg-obsidian px-4 py-3.5 font-body text-sm text-bone placeholder:text-bone/35 focus:border-fire"
              />
              <button type="submit" className="btn-primary">
                Notify Me
              </button>
            </form>
          )}
        </Reveal>

        {error && (
          <p id="notify-error" role="alert" className="mt-3 font-mono text-xs text-fire">
            {error}
          </p>
        )}

        {/* Dev-only signal that the stub captured the address. */}
        {import.meta.env.DEV && captured.length > 0 && state !== 'success' && (
          <p className="mt-4 font-mono text-[11px] uppercase tracking-[0.15em] text-bone/30">
            {captured.length} captured locally (stub)
          </p>
        )}
      </div>
    </section>
  );
}

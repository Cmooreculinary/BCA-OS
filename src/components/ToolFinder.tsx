import { useEffect, useRef, useState } from 'react';
import { recommendTools, ToolFinderError } from '../services/geminiService';
import type { ChatTurn } from '../types';
import { Reveal } from './Reveal';
import { SectionHeading } from './SectionHeading';

const EXAMPLES = [
  'I run a 12-truck food truck fleet',
  'Boutique hotel, 40 rooms',
  'Busy neighborhood pub on game nights',
  'Teaching my kids to cook',
];

/** Renders one transcript turn. */
function Turn({ turn }: { turn: ChatTurn }) {
  const isUser = turn.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] border px-4 py-3 ${
          isUser
            ? 'border-fire/40 bg-fire/10 text-bone'
            : 'border-bone/10 bg-obsidian-700/60 text-bone/85'
        }`}
      >
        <span className="mono-label mb-1.5 block text-[10px]">
          {isUser ? 'You' : 'BCA Tool Finder'}
        </span>
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{turn.text}</p>
      </div>
    </div>
  );
}

/**
 * Tool Finder — the Gemini-powered interactive feature.
 * The user describes their operation; BCA recommends grounded products + why.
 */
export function ToolFinder() {
  const [input, setInput] = useState('');
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const transcriptRef = useRef<HTMLDivElement>(null);

  // Keep the transcript pinned to the latest turn.
  useEffect(() => {
    transcriptRef.current?.scrollTo({
      top: transcriptRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [turns, loading]);

  const submit = async (raw: string) => {
    const operation = raw.trim();
    if (!operation || loading) return;

    setError(null);
    setInput('');
    setTurns((prev) => [...prev, { role: 'user', text: operation }]);
    setLoading(true);

    try {
      const answer = await recommendTools(operation);
      setTurns((prev) => [...prev, { role: 'bca', text: answer }]);
    } catch (err) {
      const message =
        err instanceof ToolFinderError
          ? err.message
          : 'Something went sideways. Try again in a moment.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void submit(input);
  };

  const hasStarted = turns.length > 0 || loading;

  return (
    <section id="finder" className="relative border-t border-bone/10 py-24 sm:py-32">
      {/* warm glow behind the panel */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full bg-fire/10 blur-[140px]"
      />

      <div className="relative mx-auto max-w-4xl px-5 sm:px-8">
        <Reveal>
          <SectionHeading
            align="center"
            kicker="Tool Finder · AI"
            title={
              <>
                Tell us how you <span className="text-fire">run.</span>
              </>
            }
            lead="Describe your operation in plain language. We'll point you to the BCA tools that fit — and tell you straight which are live and which are still in build."
          />
        </Reveal>

        <Reveal>
          <div className="mt-12 border border-bone/10 bg-obsidian-800/70 shadow-2xl shadow-black/40">
            {/* Panel header strip */}
            <div className="flex items-center gap-2 border-b border-bone/10 px-4 py-3">
              <span className="h-2.5 w-2.5 rounded-full bg-fire" aria-hidden="true" />
              <span className="h-2.5 w-2.5 rounded-full bg-bone/20" aria-hidden="true" />
              <span className="h-2.5 w-2.5 rounded-full bg-bone/20" aria-hidden="true" />
              <span className="mono-label ml-2">bca://tool-finder</span>
            </div>

            {/* Transcript */}
            <div
              ref={transcriptRef}
              className="thin-scroll max-h-[26rem] min-h-[14rem] space-y-4 overflow-y-auto p-5"
              aria-live="polite"
              aria-busy={loading}
            >
              {!hasStarted && (
                <div className="flex h-full flex-col items-center justify-center py-10 text-center">
                  <p className="font-mono text-sm text-bone/45">
                    {'>'} Awaiting your operation
                    <span className="ml-0.5 inline-block w-2 animate-blink text-fire">▋</span>
                  </p>
                  <p className="mt-3 max-w-sm text-sm text-bone/40">
                    Grounded only in the BCA catalog. No hype, no invented features.
                  </p>
                </div>
              )}

              {turns.map((turn, i) => (
                <Turn key={i} turn={turn} />
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="border border-bone/10 bg-obsidian-700/60 px-4 py-3">
                    <span className="mono-label mb-1.5 block text-[10px]">BCA Tool Finder</span>
                    <span className="flex items-center gap-1.5 text-sm text-fire">
                      <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-fire" />
                      <span
                        className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-fire"
                        style={{ animationDelay: '200ms' }}
                      />
                      <span
                        className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-fire"
                        style={{ animationDelay: '400ms' }}
                      />
                      <span className="ml-2 font-mono text-xs text-bone/50">
                        working the line…
                      </span>
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Error */}
            {error && (
              <div
                role="alert"
                className="border-t border-fire/30 bg-fire/5 px-5 py-3 text-sm text-fire"
              >
                {error}
              </div>
            )}

            {/* Input */}
            <form onSubmit={onSubmit} className="border-t border-bone/10 p-4">
              <div className="flex flex-col gap-3 sm:flex-row">
                <label htmlFor="finder-input" className="sr-only">
                  Describe your operation
                </label>
                <input
                  id="finder-input"
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="e.g. I run a 12-truck food truck fleet…"
                  autoComplete="off"
                  disabled={loading}
                  className="flex-1 border border-bone/15 bg-obsidian px-4 py-3 font-body text-sm text-bone placeholder:text-bone/35 focus:border-fire"
                />
                <button type="submit" className="btn-primary" disabled={loading || !input.trim()}>
                  {loading ? 'Thinking…' : 'Find My Tools'}
                </button>
              </div>

              {/* Example chips */}
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="mono-label mr-1 self-center">Try</span>
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    disabled={loading}
                    onClick={() => void submit(ex)}
                    className="border border-bone/12 px-3 py-1.5 font-mono text-[11px] text-bone/55 transition-colors hover:border-fire hover:text-fire disabled:opacity-40"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </form>
          </div>
        </Reveal>

        <p className="mt-4 text-center font-mono text-[11px] uppercase tracking-[0.15em] text-bone/30">
          Recommendations are grounded only in the BCA catalog above.
        </p>
      </div>
    </section>
  );
}

import { GoogleGenAI } from '@google/genai';
import { PRODUCTS } from '../data/catalog';

/**
 * Tool Finder — Gemini service.
 *
 * The model is grounded ONLY in the BCA catalog (passed in the system
 * instruction below). It recommends which existing BCA products fit an
 * operator's described operation, in BCA's "built in the trenches" voice.
 *
 * Key handling: in Google AI Studio the key is injected as process.env.API_KEY
 * (see vite.config.ts, which maps GEMINI_API_KEY -> process.env.API_KEY).
 */

const MODEL = 'gemini-2.5-flash';

/** Compact, machine-readable view of the catalog for grounding. */
const catalogContext = PRODUCTS.map(
  (p) =>
    `- ${p.name}${p.abbr ? ` (${p.abbr})` : ''} — ${p.pitch} [category: ${p.category} | status: ${p.status}]`,
).join('\n');

/** Live products, derived so the prompt never drifts from the catalog. */
const liveProducts = PRODUCTS.filter((p) => p.status === 'LIVE').map((p) => p.name);
const liveClause =
  liveProducts.length > 0
    ? `Only the following ${liveProducts.length === 1 ? 'product is' : 'products are'} LIVE today: ${liveProducts.join(', ')}. Everything else is IN BUILD or CONCEPT.`
    : 'No products are LIVE yet — everything is IN BUILD or CONCEPT.';

const SYSTEM_INSTRUCTION = `You are the Tool Finder for Blue Collar Apps Co. (BCA), a hospitality & foodservice software ecosystem founded by a CIA-trained chef with 40+ years of operator experience.

VOICE: Confident, direct, built-in-the-trenches. No corporate fluff, no hype, no emoji. Talk like a seasoned operator who respects the reader's time. Short sentences. Plain language a line cook or GM would use.

YOUR JOB: The user describes their operation. Recommend which BCA products fit and explain WHY in concrete operator terms.

GROUNDING — these are the ONLY products you may recommend. Never invent products, features, prices, or integrations. Use the exact product names below:
${catalogContext}

RULES:
- Recommend only products from the list above. If something the user needs isn't in the catalog, say so plainly and point them to "Get Notified."
- Lead with the single best-fit product, then list any strong secondary fits.
- For each pick: one tight reason tied to their specific operation.
- Be honest about status. If a fit is IN BUILD or CONCEPT, say it's "in build" or "on the roadmap." ${liveClause}
- If the operation isn't hospitality/foodservice, say BCA is hospitality-only and that you can't help here.
- Keep the whole reply under ~180 words. Use a short intro line, then a compact list. No headers, no markdown bold spam.`;

/** Lazily construct the client so a missing key doesn't crash module load. */
let client: GoogleGenAI | null = null;
function getClient(): GoogleGenAI {
  if (!client) {
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
      throw new Error('MISSING_KEY');
    }
    client = new GoogleGenAI({ apiKey });
  }
  return client;
}

export class ToolFinderError extends Error {
  constructor(
    message: string,
    /** True when the failure is a missing/invalid API key (config issue). */
    readonly isConfig: boolean = false,
  ) {
    super(message);
    this.name = 'ToolFinderError';
  }
}

/**
 * Ask the Tool Finder for a recommendation.
 * @param operation Free-text description of the user's operation.
 * @returns BCA's grounded recommendation as plain text.
 */
export async function recommendTools(operation: string): Promise<string> {
  let ai: GoogleGenAI;
  try {
    ai = getClient();
  } catch {
    throw new ToolFinderError(
      'Tool Finder needs a Gemini API key to run. Add GEMINI_API_KEY and reload — or just browse the catalog above.',
      true,
    );
  }

  try {
    const response = await ai.models.generateContent({
      model: MODEL,
      contents: operation,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        temperature: 0.6,
        // Keep latency low for a chat-style interaction.
        maxOutputTokens: 512,
      },
    });

    const text = response.text?.trim();
    if (!text) {
      throw new ToolFinderError('The Tool Finder came back empty. Try rephrasing your operation.');
    }
    return text;
  } catch (err) {
    if (err instanceof ToolFinderError) throw err;
    // Network / quota / model errors land here.
    throw new ToolFinderError(
      "Couldn't reach the Tool Finder right now. Give it another shot in a moment.",
    );
  }
}

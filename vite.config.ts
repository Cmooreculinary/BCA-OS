import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// AI Studio injects the key as GEMINI_API_KEY. We expose it to the client as
// process.env.API_KEY (the convention the Gemini SDK call reads from below).
//
// SECURITY NOTE: `define` inlines this value into the client bundle at build
// time, so any key used in a deployed build is publicly extractable. This is
// the standard AI Studio single-page model. Before a public production deploy,
// either (a) proxy the Gemini call through a server-side function so the key
// never reaches the browser, or (b) use a restricted, quota-capped AI Studio
// key that is rotated regularly. See README "Security" for details.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    // Base public path. Defaults to "/" (AI Studio, Vercel, Netlify, local).
    // For GitHub Pages project sites the app is served from /<repo>/, so the
    // Pages workflow sets VITE_BASE=/<repo>/ at build time.
    base: env.VITE_BASE || '/',
    plugins: [react()],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY ?? env.API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY ?? env.API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
  };
});

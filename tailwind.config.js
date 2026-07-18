/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        fire: {
          DEFAULT: '#EC5B13',
          600: '#D24E0C',
          400: '#F47A3C',
        },
        obsidian: {
          DEFAULT: '#0D0D0D',
          800: '#141414',
          700: '#1A1A1A',
          600: '#242424',
        },
        bone: '#F5F2EC',
        amber: {
          edge: '#E6A23C',
        },
      },
      fontFamily: {
        display: ['"Bebas Neue"', 'Impact', 'sans-serif'],
        body: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        display: '0.02em',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-dot': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.35' },
        },
        'blink': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'pulse-dot': 'pulse-dot 1.6s ease-in-out infinite',
        'blink': 'blink 1s step-end infinite',
      },
    },
  },
  plugins: [],
};

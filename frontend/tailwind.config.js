/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'terminal-bg': '#0d0d0d',
        'panel-bg': '#111111',
        'panel-border': '#1e1e1e',
        'text-primary': '#cccccc',
        'text-muted': '#555555',
        'allow': '#00ff88',
        'warn': '#ffaa00',
        'block': '#ff3333',
        'user-bubble': '#1a1a1a',
        'bot-bubble': '#161616',
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'monospace'],
      }
    },
  },
  plugins: [],
}

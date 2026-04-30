/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'terminal-bg': '#080b10',
        'panel-bg': '#101720',
        'panel-soft': '#131d29',
        'panel-elevated': '#182331',
        'panel-border': '#273447',
        'text-primary': '#e6edf3',
        'text-muted': '#8a97a8',
        'text-faint': '#586575',
        'accent': '#38d8c6',
        'accent-soft': '#12333a',
        'allow': '#42e89f',
        'warn': '#f7b955',
        'block': '#ff5c6c',
        'user-bubble': '#173147',
        'bot-bubble': '#121b27',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"Cascadia Code"', 'monospace'],
      }
    },
  },
  plugins: [],
}

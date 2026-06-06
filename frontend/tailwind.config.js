/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        canvas: 'var(--canvas)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        border: 'var(--border)',
        surface: 'var(--surface)',
        accent: {
          DEFAULT: '#3B5BDB',
          hover: '#2F4DBF',
          subtle: '#EEF2FF',
        },
        severity: {
          red: '#DC2626',
          'red-bg': '#FEF2F2',
          yellow: '#D97706',
          'yellow-bg': '#FFFBEB',
          green: '#16A34A',
          'green-bg': '#F0FDF4',
        },
      },
    },
  },
  plugins: [],
}

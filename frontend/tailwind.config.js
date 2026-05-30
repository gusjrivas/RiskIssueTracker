/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        canvas: '#F5F5F3',
        ink: '#0A0A0A',
        muted: '#6B7280',
        border: '#E5E5E3',
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

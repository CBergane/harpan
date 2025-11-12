/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './team/templates/**/*.html',
    './blog/templates/**/*.html',
    './contact/templates/**/*.html',
  ],
  safelist: [
    'min-h-[80vh]','md:min-h-[90vh]','lg:min-h-screen',
    'h-[85svh]','md:h-[92svh]','lg:h-screen',
    'will-change-[transform]','transform-gpu'
  ],
  theme: {
    extend: {
      colors: {
        // Harpans Redovisning Theme
        'primary': {
          50: '#fdf2f3',
          100: '#fce7e8',
          200: '#fad0d3',
          300: '#f5a8ad',
          400: '#ed7580',
          500: '#e14d5a',
          600: '#cd2e3f',
          700: '#ac2232',
          800: '#4a0416',  // Main brand color - Mörk burgundy
          900: '#3d0312',
        },
        'background': {
          DEFAULT: '#F5E2E3',  // Ljus rosa/beige bakgrund
          light: '#ebdcdfff',
          dark: '#eecbceff',
        },
        'accent': {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },
      fontFamily: {
        sans: ['Arimo', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #4a0416 0%, #ac2232 100%)',
        'gradient-hero': 'linear-gradient(135deg, #4a0416 0%, #cd2e3f 100%)',
        'gradient-cta': 'linear-gradient(135deg, #3d0312 0%, #4a0416 100%)',
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(74, 4, 22, 0.3)',
        'elegant': '0 4px 6px -1px rgba(74, 4, 22, 0.1), 0 2px 4px -1px rgba(74, 4, 22, 0.06)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
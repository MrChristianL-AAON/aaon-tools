// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'aaon-blue': '#0053A0',
        'aaon-blue-light': '#0066C3',
        'aaon-blue-dark': '#004080',
        'light-background': '#F5F8FB',
        'card-background': '#FFFFFF',
        'input-background': '#F8FAFC',
        'input-border': '#E2E8F0',
        'dark-text': '#1E293B',
        'light-text': '#64748B',
        'navbar-text': '#FFFFFF'
      },
      spacing: {
        '88': '22rem',
        '96': '24rem',
        '105': '26.25rem',
        '115': '28.75rem',
        '128': '32rem',
        '144': '36rem',
        '240': '60rem',
      },
      maxWidth: {
        '115': '28.75rem',
        '240': '60rem',
      },
      transitionProperty: {
        'width': 'width',
        'height': 'height',
      },
      screens: {
        'xs': '480px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}
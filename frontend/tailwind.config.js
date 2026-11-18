/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: '#1B5E20',
          dark: '#0D3311',
          light: '#2E7D32',
        },
        leaf: {
          DEFAULT: '#4CAF50',
          light: '#81C784',
          dark: '#388E3C',
        },
        cream: {
          DEFAULT: '#F8F7F0',
          dark: '#EFECE0',
        },
        earth: {
          DEFAULT: '#A67C52',
          light: '#C49A6C',
          dark: '#7D5A36',
        }
      },
      fontFamily: {
        sans: ['Noto Sans Kannada', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

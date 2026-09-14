/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        // Semantic safety colors
        safety: {
          safe: '#10b981', // emerald-500
          warning: '#f59e0b', // amber-500
          critical: '#ef4444', // red-500
          info: '#3b82f6', // blue-500
        }
      }
    },
  },
  plugins: [],
}

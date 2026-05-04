/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'xingwen-gold': '#D4AF37',
        'xingwen-dark': '#3D3228',
      },
    },
  },
  plugins: [],
}

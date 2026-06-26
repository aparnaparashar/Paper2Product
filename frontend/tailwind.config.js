/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: { 50:"#f0f4ff", 100:"#dde6ff", 400:"#7b93f8", 500:"#4f6ef7", 600:"#3b57e8", 700:"#2d44cc" }
      },
      fontFamily: { sans: ["Inter","system-ui","sans-serif"] }
    }
  },
  plugins: []
};

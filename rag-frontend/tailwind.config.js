/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        trusteq: {
          DEFAULT: "#04223fff",
          light: "#053581ff", // optionally, a lighter variant
        },
      },
    },
  },
  plugins: [],
}
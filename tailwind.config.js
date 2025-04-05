/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./index.html",
      "./cart.html",
      "./login.html",
      "./signup.html",
      "./**/*.js"
    ],
    theme: {
      extend: {
        colors: {
          primary: "#8F87F1",
          secondary: "#C68EFD",
          accent: "#E9A5F1",
          light: "#FED2E2",
          dark: "#1F2937", // for dark mode base
        },
      },
    },
    darkMode: 'class', // Enables class-based dark mode (e.g., `dark:`)
    plugins: [],
  }
  
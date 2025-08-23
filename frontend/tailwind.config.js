/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",         // include Vite's index.html
        "./src/**/*.{js,ts,jsx,tsx}", // scan all React/TSX files
    ],
    theme: {
        extend: {}, // you can customize here later
    },
    plugins: [],
}

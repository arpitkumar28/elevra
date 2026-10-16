import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "#155b48",
          sage: "#dce9d1",
          dark: "#17251f",
          background: "#f6f8f3",
          white: "#FFFFFF",
          success: "#16A34A",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

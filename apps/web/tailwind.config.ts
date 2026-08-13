import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          yellow: "#F5C542",
          secondary: "#FFD966",
          dark: "#111827",
          background: "#FFFCF2",
          white: "#FFFFFF",
          success: "#16A34A",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

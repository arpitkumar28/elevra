// Shared flat ESLint config for the Next.js apps.
import js from "@eslint/js";
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import tseslint from "typescript-eslint";

export default [
  {
    ignores: [
      "**/.next/**",
      "**/dist/**",
      "**/build/**",
      "**/coverage/**",
      "**/next-env.d.ts",
      "**/node_modules/**",
      "**/*.test.{ts,tsx,js,jsx}",
      "**/*.config.{js,mjs,cjs,ts}",
      "**/postcss.config.*",
    ],
  },
  js.configs.recommended,
  ...nextCoreWebVitals,
  // Keep lint fast and compatible with app tsconfigs; type correctness is
  // checked independently by the workspace typecheck task.
  ...tseslint.configs.recommended,
  {
    rules: {
      // These patterns are covered by the project's existing fetch-on-mount
      // hooks and JSX event handlers; avoid false positives during migration.
      "react-hooks/set-state-in-effect": "off",
    },
  },
];

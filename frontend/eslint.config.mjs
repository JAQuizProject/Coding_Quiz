import js from "@eslint/js";
import nextPlugin from "@next/eslint-plugin-next";
import jsxA11yPlugin from "eslint-plugin-jsx-a11y";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import globals from "globals";

const eslintConfig = [
  {
    ignores: [".next/**", "node_modules/**", "out/**", "dist/**", "coverage/**"],
  },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx,mjs}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.serviceworker,
        firebase: "readonly",
      },
    },
    plugins: {
      "@next/next": nextPlugin,
      "jsx-a11y": jsxA11yPlugin,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
      ...jsxA11yPlugin.configs.recommended.rules,
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs["core-web-vitals"].rules,
      "react/no-unknown-property": "off",
      "react/prop-types": "off",
      "react/react-in-jsx-scope": "off",
    },
    settings: {
      next: {
        rootDir: ".",
      },
      react: {
        version: "detect",
      },
    },
  },
];

export default eslintConfig;

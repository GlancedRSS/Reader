import { dirname } from "path";
import { fileURLToPath } from "url";
import pluginNext from "@next/eslint-plugin-next";
import pluginSortKeysFix from "eslint-plugin-sort-keys-fix";
import pluginStylisticJs from "@stylistic/eslint-plugin";
import reactPlugin from "eslint-plugin-react";
import { FlatCompat } from "@eslint/eslintrc";
import prettierPlugin from "eslint-plugin-prettier";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    plugins: {
      "@next/next": pluginNext,
      "sort-keys-fix": pluginSortKeysFix,
      "react": reactPlugin,
      "prettier": prettierPlugin,
      "@stylistic/js": pluginStylisticJs
    },
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      "sort-keys-fix/sort-keys-fix": "warn",
      "react/boolean-prop-naming": "warn",
      "react/checked-requires-onchange-or-readonly": "warn",
      "react/hook-use-state": "warn",
      "react/jsx-closing-bracket-location": "warn",
      "react/jsx-child-element-spacing": "warn",
      "react/jsx-curly-brace-presence": "warn",
      "react/jsx-curly-newline": "off",
      "react/jsx-equals-spacing": "warn",
      "react/jsx-first-prop-new-line": "warn",
      "react/jsx-handler-names": "off",
      "react/jsx-max-props-per-line": "warn",
      "react/jsx-no-leaked-render": "warn",
      "react/jsx-no-target-blank": "warn",
      "react/jsx-no-undef": "warn",
      "react/jsx-no-useless-fragment": "warn",
      "react/jsx-pascal-case": "warn",
      "react/jsx-props-no-multi-spaces": "warn",
      "react/jsx-props-no-spread-multi": "warn",
      "react/jsx-sort-props": "warn",
      "react/jsx-tag-spacing": "warn",
      "react/jsx-wrap-multilines": "warn",
      "react/no-typos": "warn",
      "react/no-unescaped-entities": "warn",
      "react/no-unused-state": "warn",
      "react/prefer-es6-class": "warn",
      "react/sort-default-props": "warn",
      "prettier/prettier": "warn",
      "@stylistic/js/eol-last": ["error", "always"],
      "@stylistic/js/linebreak-style": ["error", "unix"]
    }
  }
]

export default eslintConfig

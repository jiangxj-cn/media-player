import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      // 入口文件不需要 Fast Refresh
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true, allowExportNames: ['default'] }
      ],
    },
  },
  // 入口文件禁用 react-refresh 规则
  {
    files: ['**/main.tsx'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
  // Toast 相关文件禁用 react-refresh 规则（全局 API 模式）
  {
    files: ['**/components/Toast/*.tsx'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
])
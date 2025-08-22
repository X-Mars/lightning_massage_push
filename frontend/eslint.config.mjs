import js from '@eslint/js';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import vue from 'eslint-plugin-vue';
import prettier from 'eslint-plugin-prettier';
import { config as loadEnv } from 'dotenv';
import vueParser from 'vue-eslint-parser';

// 加载 .env（支持 VITE_NODE_ENV）
loadEnv();

const isProd = process.env.VITE_NODE_ENV === 'production';

export default [
  // 忽略
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '**/*.d.ts',
      'eslint.config.*',
      '.eslintrc.*',
      'vite.config.*',
  'test-env.js',
  'test-console.js',
    ],
  },

  // 仅对 JS/JSX 应用推荐规则，避免干扰 .vue 解析
  { files: ['**/*.{js,cjs,mjs,jsx}'], ...js.configs.recommended },

  // TS 支持（用于 .ts/.tsx/.js 等文件）
  {
    files: ['**/*.{js,cjs,mjs,ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // 浏览器常用全局
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        location: 'readonly',
        localStorage: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        HTMLElement: 'readonly',
        // Node 常用全局（例如在构建脚本里）
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        global: 'readonly',
        globalThis: 'readonly',
      },
    },
    plugins: { '@typescript-eslint': tsPlugin, prettier },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-console': isProd ? 'warn' : 'off',
      'no-debugger': isProd ? 'warn' : 'off',
    },
  },

  // Vue 官方扁平基础（更少格式化告警）
  ...vue.configs['flat/essential'],

  // Vue 项目自定义覆盖（对 *.vue 生效）
  {
    files: ['**/*.vue'],
    languageOptions: {
      // 显式指定 Vue 解析器，并让 <script> 使用 TS 解析器
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        location: 'readonly',
        localStorage: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
  setInterval: 'readonly',
  clearInterval: 'readonly',
  HTMLElement: 'readonly',
      },
    },
    plugins: { '@typescript-eslint': tsPlugin, prettier },
    rules: {
      // 关闭基础 no-unused-vars，统一用 TS 规则
      'no-unused-vars': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'error',
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      'no-console': isProd ? 'warn' : 'off',
      'no-debugger': isProd ? 'warn' : 'off',
      // 关闭大量布局类规则
      ...vue.configs['no-layout-rules'].rules,
    },
  },
];

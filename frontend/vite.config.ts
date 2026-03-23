import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  build: {
    // 代码分割优化
    rollupOptions: {
      output: {
        // 手动分割 chunks
        manualChunks: {
          // React 核心库单独打包
          'react-vendor': ['react', 'react-dom'],
          // Plyr 播放器单独打包 (较大)
          'player-vendor': ['plyr', 'hls.js'],
          // 状态管理
          'store-vendor': ['zustand'],
          // 拖拽库
          'dnd-vendor': ['@dnd-kit/core', '@dnd-kit/sortable', '@dnd-kit/utilities'],
          // 数据库
          'db-vendor': ['dexie'],
        },
        // 优化 chunk 文件名
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId 
            ? chunkInfo.facadeModuleId.split('/').pop() 
            : 'chunk';
          return `assets/js/${chunkInfo.name || facadeModuleId}-[hash].js`;
        },
        // 入口文件名
        entryFileNames: 'assets/js/[name]-[hash].js',
        // 静态资源文件名
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || '';
          if (name.endsWith('.css')) {
            return 'assets/css/[name]-[hash][extname]';
          }
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(name)) {
            return 'assets/images/[name]-[hash][extname]';
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(name)) {
            return 'assets/fonts/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
    // 提高 chunk 大小警告阈值
    chunkSizeWarningLimit: 500,
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 启用 source map 用于调试（生产环境可关闭）
    sourcemap: false,
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['react', 'react-dom', 'zustand', 'plyr', 'hls.js'],
    exclude: [],
  },
})
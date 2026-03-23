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
        manualChunks: (id) => {
          // React 核心库单独打包
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/')) {
            return 'react-vendor'
          }
          // Plyr 播放器单独打包 (较大)
          if (id.includes('node_modules/plyr/') || id.includes('node_modules/hls.js/')) {
            return 'player-vendor'
          }
          // 状态管理
          if (id.includes('node_modules/zustand/')) {
            return 'store-vendor'
          }
          // 拖拽库
          if (id.includes('node_modules/@dnd-kit/')) {
            return 'dnd-vendor'
          }
          // 数据库
          if (id.includes('node_modules/dexie/')) {
            return 'db-vendor'
          }
        },
        // 优化 chunk 文件名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        // 入口文件名
        entryFileNames: 'assets/js/[name]-[hash].js',
        // 静态资源文件名
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || ''
          if (name.endsWith('.css')) {
            return 'assets/css/[name]-[hash][extname]'
          }
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(name)) {
            return 'assets/images/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(name)) {
            return 'assets/fonts/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        },
      },
    },
    // 提高 chunk 大小警告阈值
    chunkSizeWarningLimit: 500,
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 启用 source map 用于调试（生产环境可关闭）
    sourcemap: false,
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['react', 'react-dom', 'zustand', 'plyr', 'hls.js'],
  },
})
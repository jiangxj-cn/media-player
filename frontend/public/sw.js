/**
 * Service Worker for Media Player PWA
 * 提供离线缓存和后台播放支持
 */

const CACHE_NAME = 'media-player-v2';
const STATIC_CACHE = 'static-v2';
const DYNAMIC_CACHE = 'dynamic-v2';

// 静态资源列表
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// 安装事件 - 缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
          .map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// 请求拦截策略
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API 请求 - 网络优先
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // 静态资源 - 缓存优先
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // 视频流 - 仅网络
  if (isVideoRequest(url)) {
    event.respondWith(networkOnly(request));
    return;
  }

  // 默认 - 网络优先
  event.respondWith(networkFirst(request));
});

// 缓存优先策略
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    return new Response('Offline', { status: 503 });
  }
}

// 网络优先策略
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ error: 'Network error' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 仅网络策略
async function networkOnly(request) {
  return fetch(request);
}

// 判断是否为静态资源
function isStaticAsset(pathname) {
  return /\.(js|css|png|jpg|jpeg|gif|svg|ico|woff2?)$/i.test(pathname) ||
         pathname === '/' ||
         pathname === '/index.html';
}

// 判断是否为视频请求
function isVideoRequest(url) {
  return url.pathname.startsWith('/api/proxy') ||
         url.pathname.endsWith('.m3u8') ||
         url.pathname.endsWith('.mp4') ||
         url.pathname.endsWith('.webm');
}

// 消息处理 - 用于后台播放控制
self.addEventListener('message', (event) => {
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
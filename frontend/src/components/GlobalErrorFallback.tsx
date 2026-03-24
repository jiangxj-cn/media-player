export default function GlobalErrorFallback() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="text-center">
        <div className="text-6xl mb-4">😢</div>
        <h1 className="text-2xl font-bold text-white mb-2">出错了</h1>
        <p className="text-gray-400 mb-4">应用加载失败，请刷新页面重试</p>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary hover:bg-primary/80 text-white rounded-lg transition-colors"
        >
          刷新页面
        </button>
      </div>
    </div>
  )
}
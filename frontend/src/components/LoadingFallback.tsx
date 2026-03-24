export default function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin text-4xl mb-4">🎵</div>
        <p className="text-gray-400">加载中...</p>
      </div>
    </div>
  )
}
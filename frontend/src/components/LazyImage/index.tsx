/**
 * 懒加载图片组件
 * 使用 Intersection Observer API 实现图片懒加载
 */

import { useEffect, useRef, useState, memo } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  placeholder?: string
  onClick?: () => void
  onLoad?: () => void
  onError?: () => void
}

// 默认占位图 - 灰色背景带图标
const DEFAULT_PLACEHOLDER = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Crect fill="%23374151" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" fill="%239CA3AF" font-size="30"%3E🎬%3C/text%3E%3C/svg%3E'

function LazyImage({ 
  src, 
  alt, 
  className = '', 
  placeholder = DEFAULT_PLACEHOLDER,
  onClick,
  onLoad,
  onError
}: LazyImageProps) {
  const imgRef = useRef<HTMLImageElement>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    const img = imgRef.current
    if (!img) return

    // 检查是否支持 IntersectionObserver
    if (!('IntersectionObserver' in window)) {
      // 不支持则直接加载 - 使用 RAF 避免同步 setState 警告
      requestAnimationFrame(() => setIsInView(true))
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true)
            observer.disconnect()
          }
        })
      },
      {
        rootMargin: '100px', // 提前 100px 开始加载
        threshold: 0.1
      }
    )

    observer.observe(img)

    return () => {
      observer.disconnect()
    }
  }, [])

  const handleLoad = () => {
    setIsLoaded(true)
    onLoad?.()
  }

  const handleError = () => {
    setHasError(true)
    onError?.()
  }

  return (
    <img
      ref={imgRef}
      src={isInView && !hasError ? src : placeholder}
      alt={alt}
      className={`${className} transition-opacity duration-300 ${
        isLoaded || hasError ? 'opacity-100' : 'opacity-70'
      }`}
      loading="lazy"
      decoding="async"
      onClick={onClick}
      onLoad={handleLoad}
      onError={handleError}
      style={{
        objectFit: 'cover',
      }}
    />
  )
}

export default memo(LazyImage)
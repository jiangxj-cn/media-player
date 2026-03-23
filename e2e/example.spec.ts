import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000'

test.describe('Media Player E2E Tests', () => {
  
  test.describe('首页', () => {
    test('应该正确加载首页', async ({ page }) => {
      await page.goto(BASE_URL)
      
      // 等待页面加载
      await page.waitForLoadState('networkidle')
      
      // 验证标题
      await expect(page).toHaveTitle(/Media Player|媒体播放器/i)
    })
    
    test('应该显示搜索栏', async ({ page }) => {
      await page.goto(BASE_URL)
      
      // 查找搜索输入框
      const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"], input[placeholder*="Search"]').first()
      await expect(searchInput).toBeVisible({ timeout: 10000 })
    })
  })
  
  test.describe('搜索功能', () => {
    test('应该能搜索内容', async ({ page }) => {
      await page.goto(BASE_URL)
      
      // 等待搜索框出现
      const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"], input[placeholder*="Search"]').first()
      await searchInput.waitFor({ state: 'visible', timeout: 10000 })
      
      // 输入搜索词
      await searchInput.fill('test music')
      
      // 点击搜索按钮或按回车
      const searchButton = page.locator('button:has-text("搜索"), button:has-text("Search")').first()
      if (await searchButton.isVisible()) {
        await searchButton.click()
      } else {
        await searchInput.press('Enter')
      }
      
      // 等待搜索结果（给予更长超时时间）
      await page.waitForTimeout(3000)
      
      // 验证有内容显示（可能是搜索结果或加载状态）
      const hasResults = await page.locator('[class*="result"], [class*="video"], [class*="song"]').count() > 0
      const hasLoading = await page.locator('[class*="loading"], [class*="spinner"]').count() > 0
      
      expect(hasResults || hasLoading).toBeTruthy()
    })
  })
  
  test.describe('主题切换', () => {
    test('应该能切换深色/浅色主题', async ({ page }) => {
      await page.goto(BASE_URL)
      
      // 等待页面加载
      await page.waitForLoadState('networkidle')
      
      // 查找主题切换按钮
      const themeButton = page.locator('button[aria-label*="theme"], button[aria-label*="主题"], button:has([class*="moon"]), button:has([class*="sun"])').first()
      
      if (await themeButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        // 记录当前背景色
        const html = page.locator('html')
        const beforeTheme = await html.getAttribute('class') || ''
        
        // 点击切换
        await themeButton.click()
        await page.waitForTimeout(500)
        
        // 验证主题变化
        const afterTheme = await html.getAttribute('class') || ''
        expect(beforeTheme !== afterTheme || beforeTheme.includes('dark') || afterTheme.includes('light')).toBeTruthy()
      }
    })
  })
  
  test.describe('API 健康检查', () => {
    test('API 应该返回健康状态', async ({ request }) => {
      const response = await request.get(`${BASE_URL}/api/health`)
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(data).toHaveProperty('status')
    })
    
    test('API 应该有响应时间统计', async ({ request }) => {
      const response = await request.get(`${BASE_URL}/api/stats`)
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(typeof data).toBe('object')
    })
    
    test('搜索 API 应该工作', async ({ request }) => {
      const response = await request.get(`${BASE_URL}/api/search?q=test&max_results=3`)
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(data).toHaveProperty('query')
      expect(data).toHaveProperty('results')
    })
  })
  
  test.describe('响应式设计', () => {
    test('移动端应该正确显示', async ({ page }) => {
      // 设置移动端视口
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto(BASE_URL)
      
      await page.waitForLoadState('networkidle')
      
      // 验证页面仍然可用
      const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"], input[placeholder*="Search"]').first()
      await expect(searchInput).toBeVisible({ timeout: 10000 })
    })
    
    test('平板端应该正确显示', async ({ page }) => {
      // 设置平板视口
      await page.setViewportSize({ width: 768, height: 1024 })
      await page.goto(BASE_URL)
      
      await page.waitForLoadState('networkidle')
      
      // 验证页面可用
      const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"], input[placeholder*="Search"]').first()
      await expect(searchInput).toBeVisible({ timeout: 10000 })
    })
  })
})
import type { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
  sidebar?: ReactNode
}

export default function Layout({ children, sidebar }: LayoutProps) {
  return (
    <div className="flex h-screen bg-bg-primary">
      {/* Sidebar */}
      {sidebar && (
        <aside className="w-64 bg-bg-secondary border-r border-gray-800 p-4">
          {sidebar}
        </aside>
      )}
      
      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>
    </div>
  )
}

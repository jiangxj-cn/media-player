import { useState, useEffect } from 'react'
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  defaultView?: 'login' | 'register'
  onAuthSuccess: () => void
}

export default function AuthModal({ isOpen, onClose, defaultView = 'login', onAuthSuccess }: AuthModalProps) {
  const [view, setView] = useState<'login' | 'register'>(defaultView)
  
  useEffect(() => {
    if (isOpen) {
      setView(defaultView)
    }
  }, [isOpen, defaultView])
  
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-6 w-full max-w-md mx-4">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        {view === 'login' ? (
          <LoginForm
            onLogin={() => onAuthSuccess()}
            onSwitchToRegister={() => setView('register')}
            onClose={onClose}
          />
        ) : (
          <RegisterForm
            onRegister={() => onAuthSuccess()}
            onSwitchToLogin={() => setView('login')}
            onClose={onClose}
          />
        )}
      </div>
    </div>
  )
}
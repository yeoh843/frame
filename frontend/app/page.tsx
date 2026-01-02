'use client'

import { useState, useEffect } from 'react'
import VideoUpload from '@/components/VideoUpload'
import VideoList from '@/components/VideoList'
import { useAuthStore } from '@/store/authStore'

export default function Home() {
  const { user, isAuthenticated, fetchUser } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [hasToken, setHasToken] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        setHasToken(!!token)
        if (token) {
          // Add timeout to prevent infinite loading
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Auth check timeout')), 10000)
          )
          await Promise.race([fetchUser(), timeoutPromise])
        }
      } catch (error) {
        console.error('Auth check failed:', error)
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [fetchUser])

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">AI Video Generation Platform</h1>
          <div className="text-center py-12">
            <p className="text-xl">Loading...</p>
          </div>
        </div>
      </main>
    )
  }

  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  const showAuthenticated = !!token

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">AI Video Generation Platform</h1>
        
        {showAuthenticated ? (
          <div className="space-y-8">
            <VideoUpload />
            <VideoList />
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-xl mb-4">Please log in to create videos</p>
            <a href="/login" className="text-blue-600 hover:underline">Login</a>
          </div>
        )}
      </div>
    </main>
  )
}





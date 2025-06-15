'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import { Youtube, LogIn, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading, login } = useAuth();

  useEffect(() => {
    // Check if user is already authenticated (has token in URL params)
    const token = searchParams.get('token');
    const userId = searchParams.get('user');
    
    if (token && userId) {
      // Use the auth context to login
      const handleLogin = async () => {
        await login(token, userId);
        
        // Clear URL params
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.delete('token');
        newUrl.searchParams.delete('user');
        window.history.replaceState({}, '', newUrl.toString());
        
        // Immediately redirect to dashboard
        router.push('/dashboard');
      };
      
      handleLogin();
    }
  }, [searchParams, login, router]);

  useEffect(() => {
    // Redirect to dashboard if already authenticated
    if (isAuthenticated && !authLoading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get authorization URL from backend
      const response = await axios.get('http://localhost:8000/api/auth/login');
      const { auth_url } = response.data;
      
      // Redirect to Google OAuth
      window.location.href = auth_url;
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to initiate login. Please try again.');
      setIsLoading(false);
    }
  };

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Don't show login page if already authenticated
  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
              <Youtube className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              WatchLog Insights
            </h2>
            <p className="text-gray-600 mb-8">
              Understand your YouTube subscription patterns with data-driven insights
            </p>
          </div>

          {/* Login Form */}
          <div className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
              ) : (
                <LogIn className="h-5 w-5 mr-2" />
              )}
              {isLoading ? 'Connecting...' : 'Sign in with Google'}
            </button>

            <div className="text-center">
              <p className="text-sm text-gray-500">
                By signing in, you agree to our{' '}
                <a href="#" className="text-red-600 hover:text-red-500">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="#" className="text-red-600 hover:text-red-500">
                  Privacy Policy
                </a>
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              What you'll get:
            </h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 h-5 w-5 text-green-500 mt-0.5">
                  ✓
                </div>
                <span className="ml-3 text-sm text-gray-600">
                  Detailed analysis of your subscription patterns
                </span>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 h-5 w-5 text-green-500 mt-0.5">
                  ✓
                </div>
                <span className="ml-3 text-sm text-gray-600">
                  Category breakdown and content preferences
                </span>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 h-5 w-5 text-green-500 mt-0.5">
                  ✓
                </div>
                <span className="ml-3 text-sm text-gray-600">
                  Top channels and subscriber insights
                </span>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 h-5 w-5 text-green-500 mt-0.5">
                  ✓
                </div>
                <span className="ml-3 text-sm text-gray-600">
                  Secure and private data handling
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 
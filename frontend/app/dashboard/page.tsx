'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  Users, 
  TrendingUp, 
  Youtube, 
  LogOut, 
  RefreshCw, 
  User,
  Eye,
  Hash
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ProtectedRoute from '../components/ProtectedRoute';

interface DashboardData {
  total_subscriptions: number;
  category_breakdown: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
  top_category: string;
  top_channels: Array<{
    channel: string;
    subscriber_count: number;
    category: string;
    video_count: number;
  }>;
  subscriber_distribution: Array<{
    range: string;
    count: number;
    percentage: number;
  }>;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncResult, setSyncResult] = useState<{
    message: string;
    status: string;
    channel_name?: string;
    subscription_count?: number;
    note?: string;
  } | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();

  useEffect(() => {
    // Check if user is authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    // If authenticated, load dashboard data
    if (isAuthenticated && !authLoading) {
      loadDashboardData();
    }
  }, [isAuthenticated, authLoading, router]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('http://localhost:8000/api/dashboard');
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncData = async () => {
    setIsSyncing(true);
    setSyncResult(null);
    setError(null);
    
    try {
      const syncResponse = await axios.post('http://localhost:8000/api/sync-youtube-data');
      setSyncResult(syncResponse.data);
      
      // Reload dashboard data after sync
      await loadDashboardData();
      
      // Clear sync result after 10 seconds
      setTimeout(() => {
        setSyncResult(null);
      }, 10000);
      
    } catch (err: any) {
      console.error('Sync error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to sync YouTube data';
      setError(errorMessage);
      
      // Try to extract sync result from error response
      if (err.response?.data) {
        setSyncResult({
          message: err.response.data.message || errorMessage,
          status: 'error',
          note: err.response.data.note
        });
      }
    } finally {
      setIsSyncing(false);
    }
  };

  const formatSubscriberCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  // Show loading while checking authentication or loading data
  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your subscription insights...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Please log in to view your dashboard</p>
          <button 
            onClick={() => router.push('/login')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Failed to load data</p>
          <button 
            onClick={() => router.push('/login')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Youtube className="h-8 w-8 text-red-600 mr-3" />
                <h1 className="text-xl font-semibold text-gray-900">WatchLog Insights</h1>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  {user.picture ? (
                    <img 
                      src={user.picture} 
                      alt={user.name}
                      className="h-8 w-8 rounded-full"
                    />
                  ) : (
                    <User className="h-8 w-8 text-gray-400" />
                  )}
                  <span className="text-sm text-gray-700">{user.name}</span>
                </div>
                
                <button
                  onClick={handleSyncData}
                  disabled={isSyncing}
                  className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <RefreshCw className={`h-4 w-4 mr-1 ${isSyncing ? 'animate-spin' : ''}`} />
                  {isSyncing ? 'Syncing...' : 'Sync Data'}
                </button>
                
                <button
                  onClick={logout}
                  className="flex items-center px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Sync Result Notification */}
          {syncResult && (
            <div className={`mb-6 border rounded-lg p-4 ${
              syncResult.status === 'success' 
                ? 'bg-green-50 border-green-200' 
                : syncResult.status === 'partial_success'
                ? 'bg-yellow-50 border-yellow-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  {syncResult.status === 'success' ? (
                    <div className="w-5 h-5 bg-green-400 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  ) : syncResult.status === 'partial_success' ? (
                    <div className="w-5 h-5 bg-yellow-400 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                  ) : (
                    <div className="w-5 h-5 bg-red-400 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <h3 className={`text-sm font-medium ${
                    syncResult.status === 'success' 
                      ? 'text-green-800' 
                      : syncResult.status === 'partial_success'
                      ? 'text-yellow-800'
                      : 'text-red-800'
                  }`}>
                    Data Sync {syncResult.status === 'success' ? 'Completed' : 
                               syncResult.status === 'partial_success' ? 'Partially Completed' : 'Failed'}
                  </h3>
                  <div className={`mt-1 text-sm ${
                    syncResult.status === 'success' 
                      ? 'text-green-700' 
                      : syncResult.status === 'partial_success'
                      ? 'text-yellow-700'
                      : 'text-red-700'
                  }`}>
                    <p>{syncResult.message}</p>
                    {syncResult.channel_name && (
                      <p className="mt-1">
                        Connected to channel: <span className="font-medium">{syncResult.channel_name}</span>
                      </p>
                    )}
                    {syncResult.subscription_count && (
                      <p className="mt-1">
                        Subscriptions found: <span className="font-medium">{syncResult.subscription_count}</span>
                      </p>
                    )}
                    {syncResult.note && (
                      <p className="mt-2 text-xs bg-white/50 p-2 rounded border">
                        <strong>Note:</strong> {syncResult.note}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSyncResult(null)}
                  className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {error && !syncResult && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {/* Data Source Info */}
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <Eye className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Data Source</h3>
                <div className="mt-1 text-sm text-blue-700">
                  <p>This dashboard combines real YouTube API data with simulated viewing patterns to provide comprehensive insights.</p>
                  <p className="mt-1">
                    <strong>Real data:</strong> Channel information, subscriber counts, video counts, and categories from your YouTube subscriptions.
                  </p>
                  <p className="mt-1">
                    <strong>Simulated data:</strong> Viewing patterns and time-based analytics to demonstrate the full potential of the platform.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Users className="h-8 w-8 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Subscriptions</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.total_subscriptions}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Top Category</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.top_category}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Hash className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Categories</p>
                  <p className="text-2xl font-semibold text-gray-700">
                    {dashboardData.category_breakdown.length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Category Breakdown */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardData.category_breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, percentage }) => `${category} (${percentage.toFixed(1)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {dashboardData.category_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Subscriber Distribution */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Subscriber Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dashboardData.subscriber_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Channels */}
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Channels by Subscriber Count</h3>
            <div className="space-y-3">
              {dashboardData.top_channels.map((channel, index) => (
                <div key={channel.channel} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-500 w-6">#{index + 1}</span>
                    <div className="ml-3">
                      <span className="text-sm font-medium text-gray-900">{channel.channel}</span>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                          {channel.category}
                        </span>
                        <span className="text-xs text-gray-500">
                          {channel.video_count} videos
                        </span>
                      </div>
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-600">
                    {formatSubscriberCount(channel.subscriber_count)} subscribers
                  </span>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
} 
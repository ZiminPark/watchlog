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
  Clock, 
  TrendingUp, 
  Youtube, 
  LogOut, 
  RefreshCw, 
  User,
  Calendar,
  Eye
} from 'lucide-react';

interface DashboardData {
  total_watch_time: number;
  daily_average: number;
  top_category: string;
  category_breakdown: Array<{
    category: string;
    minutes: number;
    percentage: number;
  }>;
  top_channels: Array<{
    channel: string;
    minutes: number;
  }>;
  daily_pattern: Array<{
    day: string;
    minutes: number;
  }>;
}

interface UserInfo {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncResult, setSyncResult] = useState<{
    message: string;
    status: string;
    channel_name?: string;
    note?: string;
  } | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    checkAuthAndLoadData();
  }, [selectedPeriod]);

  const checkAuthAndLoadData = async () => {
    // Check for token in URL params first (from OAuth callback)
    const tokenFromUrl = searchParams.get('token');
    const userIdFromUrl = searchParams.get('user');
    
    let token = tokenFromUrl || localStorage.getItem('access_token');
    let userId = userIdFromUrl || localStorage.getItem('user_id');
    
    if (tokenFromUrl && userIdFromUrl) {
      // Store tokens from URL params
      localStorage.setItem('access_token', tokenFromUrl);
      localStorage.setItem('user_id', userIdFromUrl);
      
      // Clear URL params
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete('token');
      newUrl.searchParams.delete('user');
      window.history.replaceState({}, '', newUrl.toString());
    }
    
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      // Set up axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Load user info
      const userResponse = await axios.get('http://localhost:8000/api/auth/me');
      setUserInfo(userResponse.data);
      
      // Load dashboard data
      await loadDashboardData();
    } catch (err) {
      console.error('Auth error:', err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/dashboard?days=${selectedPeriod}`);
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
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

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your insights...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData || !userInfo) {
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
                {userInfo.picture ? (
                  <img 
                    src={userInfo.picture} 
                    alt={userInfo.name}
                    className="h-8 w-8 rounded-full"
                  />
                ) : (
                  <User className="h-8 w-8 text-gray-400" />
                )}
                <span className="text-sm text-gray-700">{userInfo.name}</span>
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
                onClick={handleLogout}
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
              <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">About Your Data</h3>
              <div className="mt-1 text-sm text-blue-700">
                <p>
                  Due to YouTube API privacy restrictions, actual watch history is not accessible. 
                  This dashboard shows:
                </p>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li><strong>Real data:</strong> Your channel info, subscriptions, playlists, and video categories</li>
                  <li><strong>Simulated data:</strong> Watch times and viewing timestamps (for demo purposes)</li>
                </ul>
                <p className="mt-2 text-xs">
                  Click "Sync Data" to refresh with your latest YouTube account information.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Period Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Analysis Period
          </label>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Watch Time</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Math.floor(dashboardData.total_watch_time / 60)}h {dashboardData.total_watch_time % 60}m
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
                <p className="text-sm font-medium text-gray-500">Daily Average</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Math.floor(dashboardData.daily_average / 60)}h {Math.round(dashboardData.daily_average % 60)}m
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Eye className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Top Category</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.top_category}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
                  dataKey="minutes"
                >
                  {dashboardData.category_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Daily Pattern */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Viewing Pattern</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardData.daily_pattern}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="minutes" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Channels */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Channels</h3>
          <div className="space-y-3">
            {dashboardData.top_channels.map((channel, index) => (
              <div key={channel.channel} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-500 w-6">#{index + 1}</span>
                  <span className="ml-3 text-sm font-medium text-gray-900">{channel.channel}</span>
                </div>
                <span className="text-sm text-gray-600">
                  {Math.floor(channel.minutes / 60)}h {channel.minutes % 60}m
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
} 
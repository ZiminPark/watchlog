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
    try {
      await axios.post('http://localhost:8000/api/sync-youtube-data');
      await loadDashboardData();
    } catch (err) {
      console.error('Sync error:', err);
      setError('Failed to sync YouTube data');
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
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

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
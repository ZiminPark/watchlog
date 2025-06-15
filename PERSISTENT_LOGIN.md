# Persistent Login Implementation

This document explains how persistent login has been implemented in the WatchLog Insights application to ensure users stay logged in across browser sessions.

## Overview

The persistent login system ensures that users remain authenticated even after closing and reopening their browser, refreshing the page, or navigating between different pages within the application.

## Key Components

### 1. Authentication Context (`frontend/app/contexts/AuthContext.tsx`)

The `AuthContext` provides centralized authentication state management across the entire application:

- **State Management**: Manages user authentication state, loading states, and user information
- **Token Validation**: Validates JWT tokens and checks for expiration
- **Automatic Token Setup**: Configures axios interceptors for automatic token handling
- **Login/Logout Functions**: Provides methods for authentication actions

```typescript
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string, userId: string) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}
```

### 2. Protected Route Component (`frontend/app/components/ProtectedRoute.tsx`)

A wrapper component that ensures users are authenticated before accessing protected pages:

- **Authentication Check**: Verifies user authentication status
- **Loading States**: Shows loading indicators while checking authentication
- **Automatic Redirects**: Redirects unauthenticated users to login page
- **Fallback Support**: Supports custom fallback UI for unauthenticated users

### 3. Authentication Utilities (`frontend/app/utils/auth.ts`)

Utility functions for token management and axios configuration:

- **Axios Interceptors**: Automatically adds auth tokens to requests and handles token refresh
- **Token Validation**: Validates token format and expiration
- **Automatic Token Refresh**: Handles token expiration by attempting to refresh tokens
- **Error Handling**: Clears invalid tokens and redirects to login on authentication failures

### 4. Enhanced Login Page (`frontend/app/login/page.tsx`)

Updated login page with improved authentication handling:

- **Existing Token Check**: Checks for valid existing tokens on page load
- **Automatic Redirects**: Redirects authenticated users to dashboard
- **Token Validation**: Validates tokens before storing them
- **URL Parameter Handling**: Processes OAuth callback tokens from URL parameters

## How It Works

### 1. Initial Authentication Check

When the application loads:

1. **AuthProvider Initialization**: The `AuthProvider` runs on app startup
2. **Token Retrieval**: Checks `localStorage` for existing `access_token` and `user_id`
3. **Token Validation**: Validates token format and expiration
4. **API Verification**: Makes a request to `/api/auth/me` to verify token validity
5. **State Update**: Updates authentication state based on validation results

### 2. Persistent Session Management

Once authenticated:

1. **Token Storage**: Tokens are stored in `localStorage` for persistence
2. **Automatic Headers**: Axios interceptors automatically add auth headers to requests
3. **Token Refresh**: Handles token expiration by attempting to refresh tokens
4. **Session Continuity**: Users remain logged in across browser sessions

### 3. Route Protection

For protected routes:

1. **Authentication Check**: `ProtectedRoute` component checks authentication status
2. **Loading State**: Shows loading indicator while checking authentication
3. **Conditional Rendering**: Only renders protected content for authenticated users
4. **Automatic Redirects**: Redirects unauthenticated users to login page

### 4. Login Flow Enhancement

When users visit the login page:

1. **Existing Token Check**: Checks for valid existing tokens
2. **Automatic Redirect**: Redirects authenticated users to dashboard
3. **OAuth Processing**: Handles OAuth callback tokens from URL parameters
4. **Token Storage**: Stores new tokens and updates authentication state

## Key Features

### ✅ Persistent Sessions
- Users stay logged in across browser sessions
- Tokens persist in `localStorage`
- Automatic token validation on app startup

### ✅ Automatic Token Management
- Axios interceptors handle token injection
- Automatic token refresh on expiration
- Graceful handling of invalid tokens

### ✅ Route Protection
- Protected routes automatically check authentication
- Loading states during authentication checks
- Automatic redirects for unauthenticated users

### ✅ Enhanced User Experience
- No need to re-login on page refresh
- Seamless navigation between pages
- Clear loading and error states

### ✅ Security
- Token expiration validation
- Automatic cleanup of invalid tokens
- Secure token storage in `localStorage`

## Usage Examples

### Using the Auth Context

```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <p>Welcome, {user?.name}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Protecting Routes

```typescript
import ProtectedRoute from '../components/ProtectedRoute';

function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Protected dashboard content</div>
    </ProtectedRoute>
  );
}
```

### Custom Fallback for Protected Routes

```typescript
function DashboardPage() {
  return (
    <ProtectedRoute 
      fallback={
        <div className="custom-login-prompt">
          <h2>Please log in to access the dashboard</h2>
          <button onClick={() => router.push('/login')}>
            Go to Login
          </button>
        </div>
      }
    >
      <div>Protected dashboard content</div>
    </ProtectedRoute>
  );
}
```

## Configuration

### Environment Variables

Ensure your backend has the following endpoints configured:

- `GET /api/auth/me` - Get current user information
- `POST /api/auth/refresh` - Refresh access token (optional)

### Token Configuration

The system expects JWT tokens with the following structure:

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "profile_picture_url",
  "exp": 1234567890
}
```

## Security Considerations

1. **Token Storage**: Tokens are stored in `localStorage` which is accessible to JavaScript
2. **Token Expiration**: Tokens have expiration times and are validated on each check
3. **Automatic Cleanup**: Invalid tokens are automatically removed from storage
4. **HTTPS Required**: In production, always use HTTPS to protect token transmission
5. **Token Refresh**: Implement token refresh for better security in production

## Troubleshooting

### Common Issues

1. **Tokens not persisting**: Check if `localStorage` is available and not blocked
2. **Automatic logout**: Verify token expiration and backend `/api/auth/me` endpoint
3. **Infinite redirects**: Ensure authentication state is properly managed
4. **CORS issues**: Verify backend CORS configuration for frontend domain

### Debug Mode

Enable debug logging by adding console logs in the `AuthContext`:

```typescript
const checkAuth = async (): Promise<boolean> => {
  console.log('Checking authentication...');
  // ... rest of the function
};
```

## Future Enhancements

1. **Refresh Token Support**: Implement refresh token functionality for better security
2. **Remember Me Option**: Add option to extend token expiration
3. **Multi-tab Support**: Handle authentication state across multiple browser tabs
4. **Offline Support**: Cache user data for offline access
5. **Session Management**: Add ability to view and manage active sessions 
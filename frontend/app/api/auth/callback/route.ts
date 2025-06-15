import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const token = searchParams.get('token');
  const user = searchParams.get('user');

  if (token && user) {
    // Redirect to dashboard with token and user info
    const dashboardUrl = new URL('/dashboard', request.url);
    dashboardUrl.searchParams.set('token', token);
    dashboardUrl.searchParams.set('user', user);
    
    return NextResponse.redirect(dashboardUrl);
  }

  // If no token, redirect to login
  return NextResponse.redirect(new URL('/login', request.url));
} 
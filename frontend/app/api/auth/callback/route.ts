import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  if (code && state) {
    // Redirect to backend OAuth callback
    const backendUrl = new URL('/api/auth/callback', 'http://localhost:8000');
    backendUrl.searchParams.set('code', code);
    backendUrl.searchParams.set('state', state);
    
    return NextResponse.redirect(backendUrl);
  }

  // If no code, redirect to login
  return NextResponse.redirect(new URL('/login', request.url));
} 
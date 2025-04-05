import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// List of public paths that don't require authentication
const PUBLIC_PATHS = ['/login', '/', '/auth/callback', '/api/auth'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if the path is public
  if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }
  
  // Check if user is authenticated - MSAL stores tokens in sessionStorage, but we can check for our auth cookie
  // In a production app, you'd use a more robust server-side session check
  const authCookie = request.cookies.get('auth_session');
  const msalAccount = request.cookies.get('msal.account');
  
  if (!authCookie && !msalAccount) {
    // Redirect to login page if not authenticated
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  // User is authenticated, allow access
  return NextResponse.next();
}

// Configure which routes the middleware runs on
export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|assets|.*\\.svg).*)',
  ],
};

import { NextResponse } from 'next/server'

import type { NextRequest } from 'next/server'

const publicRoutes = [
	'/sign-in',
	'/sign-up',
	'/robots.txt',
	'/api/health',
	'/api/image-proxy'
]

function isPublicRoute(pathname: string): boolean {
	return publicRoutes.some(
		(route) => pathname === route || pathname.startsWith(route + '/')
	)
}

export default function middleware(request: NextRequest) {
	const { pathname } = request.nextUrl

	if (isPublicRoute(pathname)) {
		return NextResponse.next()
	}

	const sessionCookie = request.cookies.get('session_id')
	if (!sessionCookie && !pathname.startsWith('/api/')) {
		const url = request.nextUrl.clone()
		url.pathname = '/sign-in'
		return NextResponse.redirect(url)
	}

	return NextResponse.next()
}

export const config = {
	matcher: [
		'/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip)).*)',
		'/(api|trpc)(.*)'
	]
}

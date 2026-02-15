import { usePathname } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'

import { useUserPreferences } from '@/hooks/api'

export function useSplitLayout() {
	const [isDesktop, setIsDesktop] = useState(false)
	const pathname = usePathname()
	const { data: preferences } = useUserPreferences()

	useEffect(() => {
		const checkSize = () => {
			setIsDesktop(window.innerWidth >= 1024)
		}

		checkSize()
		window.addEventListener('resize', checkSize)
		return () => window.removeEventListener('resize', checkSize)
	}, [])

	const splitRoutes = useMemo(
		() => [
			'/articles',
			'/articles/unread',
			'/articles/read',
			'/articles/search'
		],
		[]
	)

	const splitRoutePatterns = useMemo(
		() => ['/feeds', '/folders', '/read-later', '/tags'],
		[]
	)

	const splitRouteBlacklist = useMemo(
		() => ['/tags', '/tags/read', '/tags/unread'],
		[]
	)

	const isSplitRoute = useMemo(() => {
		if (splitRoutes.includes(pathname)) {
			return true
		}

		if (splitRouteBlacklist.includes(pathname)) {
			return false
		}

		return splitRoutePatterns.some((pattern) => pathname.startsWith(pattern))
	}, [pathname, splitRoutes, splitRouteBlacklist, splitRoutePatterns])

	const shouldShowSplitLayout = useMemo(() => {
		return preferences?.app_layout === 'split' && isDesktop && isSplitRoute
	}, [preferences?.app_layout, isDesktop, isSplitRoute])

	const sidebarBreakpoints = useMemo(
		() => ({
			compact: preferences?.app_layout === 'split' ? 'xl:hidden' : 'lg:hidden',
			desktop:
				preferences?.app_layout === 'split' ? 'max-xl:hidden' : 'max-lg:hidden',
			mainMargin: preferences?.app_layout === 'split' ? 'xl:ml-72' : 'lg:ml-72'
		}),
		[preferences?.app_layout]
	)

	return {
		isDesktop,
		shouldShowSplitLayout,
		sidebarBreakpoints
	}
}

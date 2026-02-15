'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'

import type { TabSection } from '@/types/layout'

export const ARTICLE_TAB_CONFIG: TabSection[] = [
	{ id: 'all', label: 'All', route: '' },
	{ id: 'unread', label: 'Unread', route: 'unread' },
	{ id: 'read', label: 'Read', route: 'read' }
]

export function useDynamicTabNavigation(baseRoute: string) {
	const pathname = usePathname()
	const router = useRouter()

	const [animationState, setAnimationState] = useState({
		animationClass: '',
		key: 0
	})

	const currentSection = getCurrentSection(pathname, baseRoute)
	const dynamicTabs = generateDynamicTabs(baseRoute)

	const handleTabChange = (sectionId: string) => {
		const tab = dynamicTabs.find((t) => t.id === sectionId)
		if (tab) {
			router.push(tab.route)
		}
	}

	return {
		animationState,
		currentPath: pathname,
		currentSection,
		dynamicTabs,
		handleTabChange,
		setAnimationState
	}
}

function getCurrentSection(pathname: string, baseRoute: string): string {
	const normalizedPathname = pathname.replace(/\/$/, '')
	const normalizedBaseRoute = baseRoute.replace(/\/$/, '')

	if (normalizedPathname === normalizedBaseRoute) {
		return 'all'
	}

	const pathnameParts = normalizedPathname.split('/')
	const baseRouteParts = normalizedBaseRoute.split('/')
	const sectionParts = pathnameParts.slice(baseRouteParts.length)
	const section = sectionParts.join('/')

	return section || 'all'
}

function generateDynamicTabs(baseRoute: string): TabSection[] {
	const normalizedBaseRoute = baseRoute.replace(/\/$/, '')

	return ARTICLE_TAB_CONFIG.map((tab) => {
		if (tab.id === 'all' || !tab.route || tab.route === '') {
			return {
				...tab,
				route: normalizedBaseRoute
			}
		}

		const normalizedTabRoute = tab.route.replace(/^\//, '')
		return {
			...tab,
			route: `${normalizedBaseRoute}/${normalizedTabRoute}`
		}
	})
}

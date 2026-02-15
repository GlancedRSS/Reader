'use client'

import { Navigation } from '@/components/layout/navbar/navigation'
import { useLayoutStore } from '@/stores/layout'
import { useRouter } from 'next/navigation'

import { MOBILE_NAVIGATION_LINKS } from '@/constants/links'

import { useSidebarToggle } from '@/hooks/ui/layout'

interface MobileBottomNavProps {
	className?: string
}

export function MobileBottomNav({ className }: MobileBottomNavProps) {
	const router = useRouter()
	const { toggleSidebar } = useSidebarToggle()
	const openModal = useLayoutStore((state) => state.openDiscoveryModal)

	const tabs = MOBILE_NAVIGATION_LINKS.map((link) => ({
		description: `Navigate to ${link.name}`,
		icon: <link.icon className='w-5 h-5' />,
		id: link.href.replace(/\//g, '') || 'home',
		label: link.name
	}))

	const handleTabChange = (tabId: string) => {
		const link = MOBILE_NAVIGATION_LINKS.find(
			(navLink) => (navLink.href.replace(/\//g, '') || 'home') === tabId
		)

		if (link) {
			if (link.href === '#menu') {
				toggleSidebar()
			} else if (link.href === '#discover') {
				openModal()
			} else {
				router.push(link.href)
			}
		}
	}

	return (
		<Navigation
			{...(className && { className })}
			onChange={handleTabChange}
			options={tabs}
		/>
	)
}

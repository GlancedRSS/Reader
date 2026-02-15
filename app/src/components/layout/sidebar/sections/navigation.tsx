import { AnimatedTab } from '@/components/layout/common'
import { usePathname, useRouter } from 'next/navigation'

import { NAVIGATION_LINKS } from '@/constants/links'

import { useSidebarToggle } from '@/hooks/ui/layout'

export function Navigation({
	variant = 'full'
}: {
	variant?: 'full' | 'compact'
}) {
	const pathname = usePathname()
	const router = useRouter()
	const { closeSidebar } = useSidebarToggle()

	const tabItems = NAVIGATION_LINKS.map((item) => {
		return {
			href: item.href,
			icon: item.icon,
			icon_active: item.icon_active,
			id: item.name,
			label: item.name
		}
	})

	const handleItemClick = (item: (typeof tabItems)[0]) => {
		router.push(item.href)
		closeSidebar()
	}

	return (
		<div className='px-2 py-2 border-b border-border/80'>
			<AnimatedTab
				className='w-full'
				currentPath={pathname}
				items={tabItems}
				onItemClick={handleItemClick}
				variant={variant}
			/>
		</div>
	)
}

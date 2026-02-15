'use client'

import { Logo } from '@/components'
import VirtualizedTree from '@/components/layout/features/feeds/virtualized-tree'
import { Navigation } from '@/components/layout/sidebar/sections/navigation'
import { Search } from '@/components/layout/sidebar/sections/search'
import UserMenu from '@/components/layout/sidebar/sections/user-menu'
import Link from 'next/link'
import { FiSidebar } from 'react-icons/fi'

import { Button } from '@/components/ui/button'

import { useSidebarToggle } from '@/hooks/ui/layout'

export const CompactSidebar = () => {
	const { toggleSidebar } = useSidebarToggle()

	const handleExpand = () => {
		toggleSidebar()
	}

	return (
		<div className='w-16 bg-sidebar-background border-r border-border/40 flex flex-col relative h-full'>
			<Link
				className='p-3 border-b border-border/40 flex justify-center'
				href='/articles'
			>
				<Logo
					size='small'
					variant='icon'
				/>
			</Link>

			<div className='p-3 border-b border-border/40 flex justify-center'>
				<Button
					aria-label='Collapse sidebar'
					className='w-12 h-10'
					onClick={handleExpand}
					variant='ghost'
				>
					<FiSidebar className='w-5 h-5' />
				</Button>
			</div>

			<div>
				<Navigation variant='compact' />

				<div className='flex flex-col gap-1 p-2'>
					<Search variant='compact' />
				</div>
			</div>

			<VirtualizedTree variant='compact' />

			<div className='border-t border-border/40 p-2'>
				<UserMenu variant='compact' />
			</div>
		</div>
	)
}

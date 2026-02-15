import { Logo } from '@/components'
import VirtualizedTree from '@/components/layout/features/feeds/virtualized-tree'
import { Navigation } from '@/components/layout/sidebar/sections/navigation'
import { Search } from '@/components/layout/sidebar/sections/search'
import UserMenu from '@/components/layout/sidebar/sections/user-menu'

export default function Sidebar() {
	return (
		<div
			className='w-72 bg-sidebar-background border-r border-border/80 flex flex-col relative h-full overflow-hidden'
			data-sidebar='true'
		>
			<div className='px-4 py-4 border-b border-border/80 flex items-center justify-center sm:hidden'>
				<Logo size='small' />
				<div className='flex items-center gap-2'>
					<Search />
				</div>
			</div>

			<div className='px-4 py-4 border-b border-border/80 flex items-center justify-between max-sm:hidden'>
				<Logo
					size='small'
					variant='wordmark'
				/>
				<div className='flex items-center gap-2'>
					<Search />
				</div>
			</div>

			<Navigation />

			<VirtualizedTree />

			<UserMenu />
		</div>
	)
}

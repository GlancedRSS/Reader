import Link from 'next/link'
import {
	IoLogOutOutline,
	IoLogoGithub,
	IoOptionsOutline,
	IoPersonCircleOutline
} from 'react-icons/io5'
import { TbExternalLink } from 'react-icons/tb'

import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'

import { useLogout } from '@/hooks/api/auth'
import { useMe } from '@/hooks/api/me'
import { useSidebarToggle } from '@/hooks/ui/layout'

import type { UserResponse } from '@/types/api'

export default function UserMenu({
	variant = 'full'
}: {
	variant?: 'full' | 'compact'
}) {
	const { data: user, isLoading } = useMe()
	const { closeSidebar } = useSidebarToggle()
	const logout = useLogout()

	const getDisplayName = (user: UserResponse | null | undefined): string => {
		if (!user) return 'User'
		if (user.first_name && user.last_name) {
			return `${user.first_name} ${user.last_name}`
		}
		if (user.first_name) return user.first_name
		if (user.username) return user.username
		return 'User'
	}

	const displayName = getDisplayName(user)
	const handleNavigationClick = () => {
		closeSidebar()
	}

	if (isLoading) {
		return (
			<div
				className={
					variant === 'compact' ? '' : 'w-full p-2 border-t border-border/80'
				}
			>
				<Skeleton
					className={
						variant === 'compact' ? 'w-12 h-12' : 'justify-start w-full h-9'
					}
				/>
			</div>
		)
	}

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				{variant === 'compact' ? (
					<Button
						aria-label='User menu'
						className='w-12 h-12 p-0'
						variant='ghost'
					>
						<IoPersonCircleOutline className='size-5' />
					</Button>
				) : (
					<div className='w-full p-2 border-t border-border/80'>
						<Button
							className='w-full sm:px-2 px-2 flex justify-between gap-2'
							variant='ghost'
						>
							<div className='flex gap-1 max-w-52 mx-auto'>
								<span className='text-muted-foreground'>Signed in as</span>
								<span className='truncate'>{displayName}</span>
							</div>
						</Button>
					</div>
				)}
			</DropdownMenuTrigger>
			<DropdownMenuContent
				align='center'
				className='w-48'
				sideOffset={8}
			>
				<DropdownMenuItem
					className='mx-auto'
					disabled
				>
					Glanced Reader v{process.env.APP_VERSION || '0.0.0'}
				</DropdownMenuItem>
				<DropdownMenuSeparator />
				<DropdownMenuItem asChild>
					<div
						className='flex'
						onClick={() =>
							window.open(
								'https://github.com/glancedrss/reader',
								'_blank',
								'noopener,noreferrer'
							)
						}
					>
						<IoLogoGithub className='w-4 h-4 mr-2' />
						<span className='flex-1'>GitHub</span>
						<TbExternalLink className='w-4 h-4 ml-2' />
					</div>
				</DropdownMenuItem>
				<DropdownMenuItem asChild>
					<Link
						href='/settings/account'
						onClick={handleNavigationClick}
					>
						<IoOptionsOutline className='w-4 h-4 mr-2' />
						Settings
					</Link>
				</DropdownMenuItem>
				<DropdownMenuSeparator />
				<DropdownMenuItem
					onClick={logout}
					variant='destructive'
				>
					<IoLogOutOutline className='w-4 h-4 mr-2' />
					Sign Out
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	)
}

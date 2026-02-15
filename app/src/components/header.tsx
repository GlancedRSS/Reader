'use client'

import { FeedSettingsModal } from '@/components/articles/layout/controls/settings'
import { FolderSettingsModal } from '@/components/folders/settings-modal'
import { TagSettingsModal } from '@/components/tags/settings-modal'
import { ReactNode, useState } from 'react'
import { IoFolderOutline, IoPricetagOutline } from 'react-icons/io5'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger
} from '@/components/ui/tooltip'

import {
	type FolderListResponse,
	type TagListResponse,
	type UserFeedResponse
} from '@/types/api'

import { cn } from '@/utils'
import { getLogoUrl } from '@/utils/logo'

interface HeaderProps {
	title?: string
	website?: string | undefined | null
	feed?: UserFeedResponse | undefined
	folder?: FolderListResponse | undefined
	tag?: TagListResponse | undefined
	type?: 'feed' | 'folder' | 'tag'
	children?: ReactNode
	className?: string
}

export function Header({
	title,
	website,
	feed,
	folder,
	tag,
	type,
	children,
	className
}: HeaderProps) {
	const [logoError, setLogoError] = useState(false)
	const [isSettingsOpen, setIsSettingsOpen] = useState(false)
	const logoUrl = website ? getLogoUrl(website) : null
	const currentLogo = logoError ? null : logoUrl

	if (title) {
		return (
			<>
				<h1
					className={cn(
						'text-[2rem] font-extrabold tracking-tight p-4 leading-9 flex items-center gap-3',
						className
					)}
				>
					{type === 'folder' ? (
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<button
										className='hover:scale-105 text-foreground transition-all duration-200 cursor-pointer'
										onClick={() => setIsSettingsOpen(true)}
										type='button'
									>
										<IoFolderOutline className='size-9' />
									</button>
								</TooltipTrigger>
								<TooltipContent>
									<p>Folder settings</p>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					) : type === 'tag' ? (
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<button
										className='hover:scale-105 text-foreground transition-all duration-200 cursor-pointer'
										onClick={() => setIsSettingsOpen(true)}
										type='button'
									>
										<IoPricetagOutline className='size-9' />
									</button>
								</TooltipTrigger>
								<TooltipContent>
									<p>Tag settings</p>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					) : currentLogo ? (
						feed ? (
							<TooltipProvider>
								<Tooltip>
									<TooltipTrigger asChild>
										<button
											className='hover:scale-105 hover:ring-2 hover:ring-ring rounded-full transition-all duration-200 cursor-pointer'
											onClick={() => setIsSettingsOpen(true)}
											type='button'
										>
											<Avatar className='size-9 sm:size-9 shrink-0'>
												<AvatarImage
													alt={title}
													onError={() => setLogoError(true)}
													src={currentLogo || ''}
												/>
												<AvatarFallback className='text-xs font-medium'>
													{title.slice(0, 2).toUpperCase()}
												</AvatarFallback>
											</Avatar>
										</button>
									</TooltipTrigger>
									<TooltipContent>
										<p>Feed settings</p>
									</TooltipContent>
								</Tooltip>
							</TooltipProvider>
						) : (
							<Avatar className='size-9 sm:size-9 shrink-0'>
								<AvatarImage
									alt={title}
									onError={() => setLogoError(true)}
									src={currentLogo || ''}
								/>
								<AvatarFallback className='text-xs font-medium'>
									{title.slice(0, 2).toUpperCase()}
								</AvatarFallback>
							</Avatar>
						)
					) : null}
					<span className='truncate'>{title}</span>
				</h1>

				{feed && type === 'feed' ? (
					<FeedSettingsModal
						feed={feed}
						isOpen={isSettingsOpen}
						onOpenChange={setIsSettingsOpen}
					/>
				) : folder && type === 'folder' ? (
					<FolderSettingsModal
						folder={folder}
						isOpen={isSettingsOpen}
						onOpenChange={setIsSettingsOpen}
					/>
				) : tag && type === 'tag' ? (
					<TagSettingsModal
						isOpen={isSettingsOpen}
						onOpenChange={setIsSettingsOpen}
						tag={tag}
					/>
				) : null}
			</>
		)
	}
	return children
}

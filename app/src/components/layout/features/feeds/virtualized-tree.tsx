'use client'

import { getInitials } from '@/components/layout/features/feeds/get-initials'
import {
	FlattenedTreeItem,
	useFlattenedTree
} from '@/components/layout/features/feeds/use-flattened-tree'
import { useLayoutStore } from '@/stores/layout'
import { usePathname, useRouter } from 'next/navigation'
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { BsPinAngle } from 'react-icons/bs'
import {
	IoAdd,
	IoChevronDown,
	IoFolderOutline,
	IoLogoRss
} from 'react-icons/io5'
import { List } from 'react-window'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { ButtonGroup } from '@/components/ui/button-group'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'

import { useFolderTree } from '@/hooks/api'
import { useSidebarToggle } from '@/hooks/ui/layout'

import { cn } from '@/utils'
import { getLogoUrl } from '@/utils/logo'

const MAX_DEPTH = 3
const DEFAULT_ROW_HEIGHT = 40

interface TreeRowProps {
	data: FlattenedTreeItem[]
	index: number
	style: React.CSSProperties
	setRowHeight: (index: number, height: number) => void
	onFolderToggle: (folderId: string) => void
	onFolderNavigate: (folderId: string) => void
	onFeedClick: (feedId: string) => void
	selectedFeedId: string | null
}

const TreeRow = memo(function TreeRow({
	data,
	index,
	style,
	setRowHeight,
	onFolderToggle,
	onFolderNavigate,
	onFeedClick,
	selectedFeedId
}: TreeRowProps) {
	const item = data[index]
	const rowRef = useRef<HTMLDivElement>(null)
	const [imgError, setImgError] = useState(false)

	useEffect(() => {
		if (rowRef.current) {
			const height = rowRef.current.offsetHeight
			if (height && height > 0) {
				setRowHeight(index, height)
			}
		}
	}, [index, setRowHeight])

	const indentClass = useMemo(() => {
		switch (item?.depth) {
			case 0:
				return 'pl-0'
			case 1:
				return 'pl-4'
			case 2:
				return 'pl-8'
			case 3:
				return 'pl-12'
			default:
				return 'pl-0'
		}
	}, [item?.depth])

	const handleFolderClick = useCallback(() => {
		const folderKey = item?.id ?? '__uncategorized__'
		if (item?.type === 'folder') {
			onFolderToggle(folderKey)
		}
	}, [item?.id, item?.type, onFolderToggle])

	const handleNavigateToFolder = useCallback(() => {
		if (item?.id) {
			onFolderNavigate(item.id)
		}
	}, [item?.id, onFolderNavigate])

	const handleFeedClick = useCallback(() => {
		if (item?.id) {
			onFeedClick(item.id)
		}
	}, [item?.id, onFeedClick])

	if (item?.type === 'feed') {
		const isSelected = selectedFeedId === item?.id
		const logoUrl = item?.website ? getLogoUrl(item?.website) : null
		const currentSrc = imgError ? null : logoUrl

		return (
			<div
				className={cn(indentClass, 'flex items-center')}
				ref={rowRef}
				style={style}
			>
				<Button
					className={cn(
						'w-full h-auto justify-start whitespace-normal text-left px-2 sm:px-2 group',
						item?.unread_count > 0
							? 'font-medium text-foreground'
							: 'font-normal text-muted-foreground',
						isSelected && 'bg-accent/10'
					)}
					onClick={handleFeedClick}
					variant='ghost'
				>
					<div className='relative shrink-0'>
						<Avatar
							className={cn(
								'size-5 transition-all duration-200',
								item?.is_active === false && 'grayscale opacity-50'
							)}
						>
							<AvatarImage
								alt={item?.name}
								onError={() => setImgError(true)}
								src={currentSrc || ''}
							/>
							<AvatarFallback
								className={cn(
									'text-[9px] font-medium',
									item?.unread_count > 0
										? 'bg-primary/10 text-primary'
										: 'bg-muted-foreground/10 text-muted-foreground'
								)}
							>
								{getInitials(item?.name)}
							</AvatarFallback>
						</Avatar>
					</div>
					<span className='flex-1 truncate min-w-0'>{item?.name}</span>
					{item?.is_pinned ? (
						<span className='text-xs rounded-full text-muted-foreground shrink-0 ml-2'>
							<BsPinAngle className='w-4 h-4' />
						</span>
					) : null}
					{item?.unread_count > 0 && (
						<span className='text-xs rounded-full text-muted-foreground shrink-0'>
							{item?.unread_count > 999
								? `${Math.floor(item?.unread_count / 100) / 10}K+`
								: item?.unread_count}
						</span>
					)}
				</Button>
			</div>
		)
	}

	// Folder rendering
	const canExpand = (item?.depth ?? 0) < MAX_DEPTH && item?.hasChildren

	return (
		<div
			className={cn(indentClass)}
			ref={rowRef}
			style={style}
		>
			<ButtonGroup className='w-full'>
				<Button
					aria-label={item?.isExpanded ? 'Collapse folder' : 'Expand folder'}
					className='h-auto w-8 p-0 shrink-0'
					disabled={!canExpand}
					onClick={handleFolderClick}
					variant='ghost'
				>
					<IoChevronDown
						className={cn(
							'w-3.5 h-3.5 transition-transform duration-200',
							!item?.isExpanded && '-rotate-90'
						)}
					/>
				</Button>
				<Button
					className='flex-1 h-auto justify-start text-left pl-1 pr-2 sm:px-2 font-medium text-sm hover:bg-accent/50'
					disabled={!item?.id}
					onClick={handleNavigateToFolder}
					variant='ghost'
				>
					<span className='flex-1 text-left truncate min-w-0'>
						{item?.name}
					</span>
					{item?.is_pinned ? (
						<span className='text-xs rounded-full text-muted-foreground shrink-0 ml-2'>
							<BsPinAngle className='w-4 h-4' />
						</span>
					) : null}
					{(item?.unread_count ?? 0) > 0 && (
						<span className='text-xs rounded-full text-muted-foreground shrink-0 ml-2'>
							{item?.unread_count ?? 0}
						</span>
					)}
				</Button>
			</ButtonGroup>
		</div>
	)
})

const CompactFeedButton = memo(function CompactFeedButton({
	feed,
	isSelected,
	onClick
}: {
	feed: FlattenedTreeItem
	isSelected: boolean
	onClick: (feedId: string) => void
}) {
	const [imgError, setImgError] = useState(false)
	const logoUrl = feed.website ? getLogoUrl(feed.website) : null

	return (
		<Button
			aria-label={feed.name}
			className={cn(
				'w-12 h-12 p-0 shrink-0',
				isSelected
					? 'bg-accent text-accent-foreground'
					: 'text-muted-foreground hover:text-accent-foreground',
				feed.is_active === false && 'grayscale opacity-50'
			)}
			onClick={() => feed.id && onClick(feed.id)}
			variant='ghost'
		>
			<div className='relative'>
				<Avatar className='w-7 h-7'>
					<AvatarImage
						alt={feed.name}
						onError={() => setImgError(true)}
						src={imgError ? undefined : logoUrl || ''}
					/>
					<AvatarFallback
						className={cn(
							'text-[8px] font-medium',
							feed.unread_count > 0
								? 'bg-primary/10 text-primary'
								: 'bg-muted-foreground/10 text-muted-foreground'
						)}
					>
						{getInitials(feed.name)}
					</AvatarFallback>
				</Avatar>
				{feed.unread_count > 0 && (
					<span className='absolute -top-1 -right-2 w-fit px-1 h-4 bg-accent text-accent-foreground text-[8px] rounded-full flex items-center justify-center'>
						{feed.unread_count > 999
							? `${Math.floor(feed.unread_count / 1000)}K+`
							: feed.unread_count > 99
								? '99+'
								: feed.unread_count}
					</span>
				)}
			</div>
		</Button>
	)
})

interface FeedsHeaderButtonProps {
	disabled?: boolean
	className?: string
}

const FeedsHeaderButton = memo(function FeedsHeaderButton({
	disabled = false,
	className
}: FeedsHeaderButtonProps) {
	const openModal = useLayoutStore((state) => state.openDiscoveryModal)
	const openFolderModal = useLayoutStore((state) => state.openFolderModal)

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button
					aria-label='Add feeds or folders'
					className={cn(
						'h-6 w-6 p-0 text-muted-foreground hover:text-foreground',
						className
					)}
					disabled={disabled}
					size='sm'
					variant='ghost'
				>
					<IoAdd className='w-4 h-4' />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent
				align='end'
				className='w-40'
				sideOffset={4}
			>
				<DropdownMenuItem onClick={openModal}>
					<IoLogoRss className='w-4 h-4 mr-2' />
					<span>Add feed</span>
				</DropdownMenuItem>
				<DropdownMenuItem onClick={() => openFolderModal()}>
					<IoFolderOutline className='w-4 h-4 mr-2' />
					<span>New folder</span>
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	)
})

interface VirtualizedTreeProps {
	variant?: 'full' | 'compact'
}

const VirtualizedTree = memo(function VirtualizedTree({
	variant = 'full'
}: VirtualizedTreeProps) {
	const router = useRouter()
	const { closeSidebar } = useSidebarToggle()
	const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
	const [toggledFolderId, setToggledFolderId] = useState<string | null>(null)
	const pathname = usePathname()

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const listRef = useRef<any>(null)

	const selectedFeedId = pathname.match(/^\/feeds\/([^/]+)/)?.[1] || null

	const { data: folderTree, isLoading, error } = useFolderTree()

	const flattenedTree = useFlattenedTree(folderTree, expandedFolders, MAX_DEPTH)

	const rowHeightsCache = useRef<Record<number, number>>({})
	const measuredIndices = useRef<Set<number>>(new Set())

	const getRowHeight = useCallback((index: number) => {
		return rowHeightsCache.current[index] ?? DEFAULT_ROW_HEIGHT
	}, [])

	const setRowHeight = useCallback((index: number, height: number) => {
		const isNewMeasurement = !measuredIndices.current.has(index)
		if (isNewMeasurement) {
			rowHeightsCache.current[index] = height
			measuredIndices.current.add(index)
		}
	}, [])

	useEffect(() => {
		if (toggledFolderId && listRef.current) {
			const index = flattenedTree.findIndex(
				(item) =>
					item?.type === 'folder' &&
					(toggledFolderId === '__uncategorized__'
						? item?.id === null
						: item?.id === toggledFolderId)
			)

			if (index !== -1) {
				requestAnimationFrame(() => {
					if (listRef.current) {
						listRef.current.scrollToRow({
							behavior: 'auto',
							index
						})
					}
				})
			}

			setToggledFolderId(null)
		}
	}, [flattenedTree, toggledFolderId])

	const handleFolderToggle = useCallback((folderId: string) => {
		setToggledFolderId(folderId)
		setExpandedFolders((prev) => {
			const newExpanded = new Set(prev)
			if (newExpanded.has(folderId)) {
				newExpanded.delete(folderId)
			} else {
				newExpanded.add(folderId)
			}
			return newExpanded
		})
	}, [])

	const handleFeedClick = useCallback(
		(feedId: string) => {
			router.push(`/feeds/${feedId}`)
			closeSidebar()
		},
		[router, closeSidebar]
	)

	const handleFolderNavigate = useCallback(
		(folderId: string) => {
			router.push(`/folders/${folderId}`)
			closeSidebar()
		},
		[router, closeSidebar]
	)

	const rowProps = useMemo(
		() => ({
			data: flattenedTree,
			onFeedClick: handleFeedClick,
			onFolderNavigate: handleFolderNavigate,
			onFolderToggle: handleFolderToggle,
			selectedFeedId
		}),
		[
			flattenedTree,
			handleFolderToggle,
			handleFeedClick,
			handleFolderNavigate,
			selectedFeedId
		]
	)

	const pinnedFeeds = useMemo(() => {
		if (!folderTree) return []

		const pinned: FlattenedTreeItem[] = []

		function traverse(folders: typeof folderTree) {
			if (!folders) return

			for (const folder of folders) {
				for (const feed of folder.feeds) {
					if (feed.is_pinned) {
						pinned.push({
							depth: 0,
							hasChildren: false,
							id: feed.id,
							isExpanded: false,
							is_active: feed.is_active,
							is_pinned: feed.is_pinned,
							name: feed.title,
							parentId: folder.id ?? null,
							type: 'feed',
							unread_count: feed.unread_count,
							website: feed.website
						})
					}
				}
				traverse(folder.subfolders)
			}
		}

		traverse(folderTree)
		return pinned
	}, [folderTree])

	if (isLoading) {
		return (
			<div className='flex flex-col h-full flex-1 min-h-0'>
				<div className='pl-2 pt-2 shrink-0 pb-2'>
					<div className='flex items-center justify-between px-2'>
						<h3 className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
							Feeds
						</h3>
						<FeedsHeaderButton disabled />
					</div>
				</div>
				<ScrollArea className='px-2 h-[calc(100%-2.5rem)]'>
					<div className='space-y-1.5 pb-1.5'>
						{Array.from({ length: 12 }).map((_, index) => (
							<Skeleton
								className='h-9 w-68'
								key={index}
							/>
						))}
					</div>
				</ScrollArea>
			</div>
		)
	}

	if (error) {
		return (
			<div className='flex flex-col h-full flex-1 min-h-0'>
				<div className='pl-2 pt-2 shrink-0 pb-2'>
					<div className='flex items-center justify-between px-2'>
						<h3 className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
							Feeds
						</h3>
					</div>
				</div>
				<ScrollArea className='px-2 h-[calc(100%-2.5rem)]'>
					<div className='p-4 text-sm text-muted-foreground'>
						Failed to load feeds. Please try again.
					</div>
				</ScrollArea>
			</div>
		)
	}

	if (variant === 'compact') {
		return (
			<div className='flex-1 min-h-0 border-t border-border/40'>
				<ScrollArea className='h-full p-2'>
					<div className='flex flex-col gap-2'>
						{pinnedFeeds.map((feed) => (
							<CompactFeedButton
								feed={feed}
								isSelected={selectedFeedId === feed.id}
								key={feed.id}
								onClick={handleFeedClick}
							/>
						))}
					</div>
				</ScrollArea>
			</div>
		)
	}

	if (!flattenedTree || flattenedTree.length === 0) {
		return (
			<div className='flex flex-col h-full flex-1 min-h-0'>
				<div className='pl-2 pt-2 shrink-0 pb-2'>
					<div className='flex items-center justify-between px-2'>
						<h3 className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
							Feeds
						</h3>
						<FeedsHeaderButton />
					</div>
				</div>
				<div className='flex flex-col items-center justify-center h-full text-sm text-muted-foreground text-center px-4'>
					Add your first feed to start reading
				</div>
			</div>
		)
	}

	return (
		<div className='flex flex-col h-full flex-1 min-h-0'>
			<div className='pl-2 pt-2 shrink-0 pb-2'>
				<div className='flex items-center justify-between px-2'>
					<h3 className='text-xs font-medium text-muted-foreground uppercase tracking-wider'>
						Feeds
					</h3>
					<FeedsHeaderButton />
				</div>
			</div>

			<div className='flex-1 min-h-0 px-2'>
				<List
					className='pb-1.5'
					listRef={listRef}
					// eslint-disable-next-line @typescript-eslint/no-explicit-any
					rowComponent={TreeRow as any}
					rowCount={flattenedTree.length}
					rowHeight={getRowHeight}
					rowProps={{
						...rowProps,
						setRowHeight
					}}
				/>
			</div>
		</div>
	)
})

export default VirtualizedTree

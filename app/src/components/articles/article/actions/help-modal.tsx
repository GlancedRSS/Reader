'use client'

import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle
} from '@/components/ui/dialog'
import {
	Drawer,
	DrawerContent,
	DrawerHeader,
	DrawerTitle
} from '@/components/ui/drawer'

import { useIsMobile } from '@/hooks/ui/media-query'

interface HelpModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

export function HelpModal({ isOpen, onOpenChange }: HelpModalProps) {
	const isMobile = useIsMobile()

	const shortcuts = [
		{ description: 'Next article', key: 'J' },
		{ description: 'Previous article', key: 'K' },
		{ description: 'Bookmark / Read later', key: 'S' },
		{ description: 'Open original article', key: 'V' },
		{ description: 'Manage tags', key: 'T' },
		{ description: 'Toggle full content', key: 'C' },
		{ description: 'Add/Edit notes', key: 'N' },
		{ description: 'Preferences', key: 'P' },
		{ description: 'Show this help', key: '?' }
	]

	const content = (
		<div className='space-y-3'>
			{shortcuts.map((shortcut) => (
				<div
					className='flex items-center justify-between'
					key={shortcut.key}
				>
					<span className='text-sm text-muted-foreground'>
						{shortcut.description}
					</span>
					<kbd className='rounded border border-border bg-muted px-2 py-1 text-xs font-medium'>
						{shortcut.key}
					</kbd>
				</div>
			))}
		</div>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={onOpenChange}
					open={isOpen}
				>
					<DialogContent className='sm:max-w-sm'>
						<DialogHeader>
							<DialogTitle>Keyboard Shortcuts</DialogTitle>
						</DialogHeader>
						{content}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={onOpenChange}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Keyboard Shortcuts</DrawerTitle>
						</DrawerHeader>
						<div className='px-4 pb-6'>{content}</div>
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}

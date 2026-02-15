import { CommandPalette } from '@/components/search'
import { useState } from 'react'
import { IoSearch } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'

export function Search({
	variant = 'default'
}: {
	variant?: 'default' | 'compact'
}) {
	const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

	const renderSearch = () => {
		if (variant === 'compact') {
			return (
				<Button
					aria-label='Search'
					className='w-12 h-12 p-0 text-muted-foreground hover:text-accent-foreground'
					onClick={() => setCommandPaletteOpen(true)}
					variant='ghost'
				>
					<IoSearch className='w-5 h-5' />
				</Button>
			)
		}
		return (
			<button
				className='hidden sm:flex items-center w-[130px] h-8 bg-muted-foreground/5 hover:bg-muted-foreground/10 border rounded-lg pl-2 pr-1 text-sm text-muted-foreground cursor-pointer transition-all duration-200 justify-between'
				onClick={() => setCommandPaletteOpen(true)}
			>
				<div className='flex items-center space-x-2'>
					<IoSearch className='w-4 h-4 shrink-0' />
					<span>Search</span>
				</div>
				<Hotkey>⌘ K</Hotkey>
			</button>
		)
	}

	return (
		<>
			{renderSearch()}
			<CommandPalette
				isOpen={commandPaletteOpen}
				onClose={() => setCommandPaletteOpen(false)}
			/>
		</>
	)
}

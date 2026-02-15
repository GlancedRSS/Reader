'use client'

import { Button } from '@/components/ui/button'

import type { Command } from '@/types/layout'

interface SearchCommandsProps {
	commands: Command[]
	onCommandSelect: (command: Command) => void
	title: string
}

export function SearchCommands({
	commands,
	onCommandSelect,
	title
}: SearchCommandsProps) {
	if (commands.length === 0) {
		return null
	}

	return (
		<div className='space-y-2'>
			<h3 className='text-sm font-medium text-muted-foreground px-3'>
				{title}
			</h3>
			{commands.map((command, index) => (
				<Button
					className='w-full justify-start'
					key={`${command.name}-${index}`}
					onClick={() => onCommandSelect(command)}
					variant='ghost'
				>
					{command.name}
				</Button>
			))}
		</div>
	)
}

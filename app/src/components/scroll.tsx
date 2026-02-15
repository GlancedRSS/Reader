import { ReactNode } from 'react'

import { ScrollArea } from '@/components/ui/scroll-area'

interface ScrollWrapperProps {
	children: ReactNode
}

export function ScrollWrapper({ children }: ScrollWrapperProps) {
	return (
		<ScrollArea className='h-[calc(100dvh-7rem-3.25rem-0.75rem)] md:h-[calc(100dvh-5rem-2.5rem)]'>
			<div className='space-y-6 px-4 pb-4'>{children}</div>
		</ScrollArea>
	)
}

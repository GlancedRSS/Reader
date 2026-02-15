import * as PopoverPrimitive from '@radix-ui/react-popover'
import * as React from 'react'

import { cn } from '@/utils'

function Popover({
	...props
}: React.ComponentProps<typeof PopoverPrimitive.Root>) {
	return (
		<PopoverPrimitive.Root
			data-slot='popover'
			{...props}
		/>
	)
}

function PopoverTrigger({
	...props
}: React.ComponentProps<typeof PopoverPrimitive.Trigger>) {
	return (
		<PopoverPrimitive.Trigger
			data-slot='popover-trigger'
			{...props}
		/>
	)
}

function PopoverContent({
	className,
	align = 'center',
	sideOffset = 4,
	...props
}: React.ComponentProps<typeof PopoverPrimitive.Content>) {
	return (
		<PopoverPrimitive.Portal>
			<PopoverPrimitive.Content
				align={align}
				className={cn(
					'z-50 w-72 origin-(--radix-popover-content-transform-origin) rounded-lg border border-border/80 bg-background/90 p-4 backdrop-blur-xs data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 outline-hidden',
					className
				)}
				data-slot='popover-content'
				sideOffset={sideOffset}
				{...props}
			/>
		</PopoverPrimitive.Portal>
	)
}

function PopoverAnchor({
	...props
}: React.ComponentProps<typeof PopoverPrimitive.Anchor>) {
	return (
		<PopoverPrimitive.Anchor
			data-slot='popover-anchor'
			{...props}
		/>
	)
}

export { Popover, PopoverAnchor, PopoverContent, PopoverTrigger }

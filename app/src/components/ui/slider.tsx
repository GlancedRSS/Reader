import * as SliderPrimitive from '@radix-ui/react-slider'
import * as React from 'react'

import { cn } from '@/utils'

type SliderProps = React.ComponentProps<typeof SliderPrimitive.Root>

function Slider({
	className,
	defaultValue,
	value,
	min = 0,
	max = 100,
	...props
}: SliderProps) {
	const _values = React.useMemo(
		() =>
			Array.isArray(value)
				? value
				: Array.isArray(defaultValue)
					? defaultValue
					: [min, max],
		[value, defaultValue, min, max]
	)

	const rootProps: SliderProps & { dataSlot?: string } = {
		...props,
		className: cn(
			'relative flex w-full touch-none items-center select-none data-disabled:opacity-50 data-[orientation=vertical]:h-full data-[orientation=vertical]:min-h-44 data-[orientation=vertical]:w-auto data-[orientation=vertical]:flex-col',
			className
		),
		dataSlot: 'slider',
		max,
		min
	}

	if (defaultValue !== undefined) {
		rootProps.defaultValue = defaultValue
	}

	if (value !== undefined) {
		rootProps.value = value
	}

	return (
		<SliderPrimitive.Root {...rootProps}>
			<SliderPrimitive.Track
				className={cn(
					'bg-muted-foreground/20 relative grow overflow-hidden rounded-full data-[orientation=horizontal]:h-2 data-[orientation=horizontal]:w-full data-[orientation=vertical]:h-full data-[orientation=vertical]:w-2 sm:h-1.5 sm:data-[orientation=horizontal]:h-1.5'
				)}
				data-slot='slider-track'
			>
				<SliderPrimitive.Range
					className={cn(
						'bg-primary absolute data-[orientation=horizontal]:h-full data-[orientation=vertical]:w-full'
					)}
					data-slot='slider-range'
				/>
			</SliderPrimitive.Track>
			{Array.from({ length: _values.length }, (_, index) => (
				<SliderPrimitive.Thumb
					className='border-primary bg-background ring-ring/50 block size-5 shrink-0 rounded-full border shadow-sm transition-[color,box-shadow] hover:ring-4 focus-visible:ring-4 focus-visible:outline-hidden disabled:pointer-events-none disabled:opacity-50 sm:size-4'
					data-slot='slider-thumb'
					key={index}
				/>
			))}
		</SliderPrimitive.Root>
	)
}

export { Slider }

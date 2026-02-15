import * as ProgressPrimitive from '@radix-ui/react-progress'
import * as React from 'react'

import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

import { cn } from '@/utils'

type ProgressVariant = 'default' | 'multiple'

interface ProgressMultipleProps {
	total: number
	success: number
	failed: number
	duplicates: number
}

interface ProgressProps
	extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> {
	variant?: ProgressVariant
	value?: number
	multiple?: ProgressMultipleProps
}

const Progress = React.forwardRef<
	React.ElementRef<typeof ProgressPrimitive.Root>,
	ProgressProps
>(({ className, value, variant = 'default', multiple, ...props }, ref) => {
	if (variant === 'multiple' && multiple) {
		const { total, success, failed, duplicates } = multiple
		const successPercent = total > 0 ? (success / total) * 100 : 0
		const failedPercent = total > 0 ? (failed / total) * 100 : 0
		const othersPercent = total > 0 ? (duplicates / total) * 100 : 0

		return (
			<ProgressPrimitive.Root
				className={cn(
					'relative h-5 w-full overflow-hidden rounded-full bg-muted sm:h-4',
					className
				)}
				ref={ref}
				{...props}
			>
				{successPercent > 0 && (
					<Tooltip>
						<TooltipTrigger asChild>
							<div
								className='absolute cursor-pointer left-0 top-0 h-full bg-green-500 transition-all'
								style={{ width: `${successPercent}%` }}
							/>
						</TooltipTrigger>
						<TooltipContent>
							<p>{success} imported</p>
						</TooltipContent>
					</Tooltip>
				)}
				{othersPercent > 0 && (
					<Tooltip>
						<TooltipTrigger asChild>
							<div
								className='absolute cursor-pointer top-0 h-full bg-amber-500 transition-all'
								style={{
									left: `${successPercent}%`,
									width: `${othersPercent}%`
								}}
							/>
						</TooltipTrigger>
						<TooltipContent>
							<p>{duplicates} duplicates</p>
						</TooltipContent>
					</Tooltip>
				)}
				{failedPercent > 0 && (
					<Tooltip>
						<TooltipTrigger asChild>
							<div
								className='absolute cursor-pointer top-0 h-full bg-red-500 transition-all'
								style={{
									left: `${successPercent + othersPercent}%`,
									width: `${failedPercent}%`
								}}
							/>
						</TooltipTrigger>
						<TooltipContent>
							<p>{failed} failed</p>
						</TooltipContent>
					</Tooltip>
				)}
			</ProgressPrimitive.Root>
		)
	}

	return (
		<ProgressPrimitive.Root
			className={cn(
				'relative h-5 w-full overflow-hidden rounded-full bg-muted sm:h-4',
				className
			)}
			ref={ref}
			{...props}
		>
			<ProgressPrimitive.Indicator
				className='h-full w-full flex-1 bg-primary transition-all'
				style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
			/>
		</ProgressPrimitive.Root>
	)
})
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }

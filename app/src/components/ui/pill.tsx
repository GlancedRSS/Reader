import { cva } from 'class-variance-authority'
import * as React from 'react'

import type { VariantProps } from 'class-variance-authority'

import { cn } from '@/utils'

const pillVariants = cva(
	'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ',
	{
		defaultVariants: {
			variant: 'default'
		},
		variants: {
			variant: {
				default: 'border-transparent bg-accent text-accent-foreground',
				destructive:
					'border-transparent bg-destructive-accent text-destructive-accent-foreground',
				outline: 'text-foreground border-border',
				warning:
					'border-transparent bg-warning-accent text-warning-accent-foreground'
			}
		}
	}
)

export interface PillProps
	extends React.ComponentProps<'span'>,
		VariantProps<typeof pillVariants> {}

function Pill({ className, variant, ...props }: PillProps) {
	return (
		<span
			className={cn(pillVariants({ variant }), className)}
			{...props}
		/>
	)
}

export { Pill, pillVariants }

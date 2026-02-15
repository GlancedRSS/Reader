import { Slot } from '@radix-ui/react-slot'
import { cva } from 'class-variance-authority'
import * as React from 'react'

import type { VariantProps } from 'class-variance-authority'

import { cn } from '@/utils'

const buttonVariants = cva(
	"inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-ring/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive backdrop-blur-sm",
	{
		defaultVariants: {
			size: 'default',
			variant: 'default'
		},
		variants: {
			size: {
				default:
					'h-10 px-6 py-2 has-[>svg]:px-4 sm:h-9 sm:px-4 sm:has-[>svg]:px-3',
				icon: 'size-11 sm:size-9',
				lg: 'h-11 rounded-lg px-8 has-[>svg]:px-6 sm:h-10 sm:px-6 sm:has-[>svg]:px-4',
				sm: 'h-9 rounded-lg gap-1.5 px-4 has-[>svg]:px-3',
				standard: 'h-9 px-4 has-[>svg]:px-3'
			},
			variant: {
				default:
					'bg-primary/85 text-primary-foreground shadow-lg shadow-black/5 dark:shadow-white/10 hover:bg-primary/95 hover:shadow-xl hover:shadow-black/10 dark:hover:shadow-white/20 active:scale-[0.98] active:shadow-md border border-white/10 dark:border-white/5',
				destructive:
					'bg-destructive/85 text-white shadow-lg shadow-destructive/20 dark:shadow-destructive/30 hover:bg-destructive/95 hover:shadow-xl hover:shadow-destructive/25 dark:hover:shadow-destructive/35 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/70 active:scale-[0.98] active:shadow-md border border-white/10 dark:border-white/5',
				ghost:
					'bg-transparent dark:bg-transparent hover:bg-white/10 dark:hover:bg-accent hover:text-accent-foreground hover:bg-accent dark:hover:text-accent-foreground active:scale-[0.98] hover:shadow-sm hover:shadow-black/5 dark:hover:shadow-white/10 active:shadow-md active:shadow-black/10 dark:active:shadow-white/20',
				link: 'text-primary underline-offset-4 hover:underline hover:text-primary/80 active:scale-[0.98] transition-all duration-150',
				muted:
					'bg-white/10 dark:bg-accent text-accent-foreground bg-accent dark:text-accent-foreground hover:bg-white/5 hover:dark:bg-black/5 active:scale-[0.98] active:shadow-md border border-transparent hover:border-border hover:shadow-sm hover:shadow-black/5 dark:hover:shadow-white/10 active:shadow-md active:shadow-black/10 dark:active:shadow-white/20',
				outline:
					'border hover:border-accent dark:hover:border-accent bg-white/20 dark:bg-black/20 shadow-lg shadow-black/5 dark:shadow-white/10 hover:bg-white/30 dark:hover:bg-black/30 hover:text-accent-foreground hover:shadow-xl hover:shadow-black/10 dark:hover:shadow-white/20 active:scale-[0.98] active:shadow-md',
				secondary:
					'bg-secondary/85 text-secondary-foreground shadow-lg shadow-secondary/20 dark:shadow-secondary/30 hover:bg-secondary/95 hover:shadow-xl hover:shadow-secondary/25 dark:hover:shadow-secondary/35 active:scale-[0.98] active:shadow-md border border-white/10 dark:border-white/5'
			}
		}
	}
)

function Button({
	className,
	variant,
	size,
	asChild = false,
	...props
}: React.ComponentProps<'button'> &
	VariantProps<typeof buttonVariants> & {
		asChild?: boolean
	}) {
	const Comp = asChild ? Slot : 'button'

	return (
		<Comp
			className={cn(buttonVariants({ className, size, variant }))}
			data-slot='button'
			{...props}
		/>
	)
}

export { Button, buttonVariants }

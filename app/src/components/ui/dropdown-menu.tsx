'use client'

import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu'
import { cva } from 'class-variance-authority'
import * as React from 'react'
import { IoCheckmark, IoChevronForward, IoEllipse } from 'react-icons/io5'

import type { VariantProps } from 'class-variance-authority'

import { cn } from '@/utils'

const DropdownMenu = DropdownMenuPrimitive.Root

const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger

const DropdownMenuGroup = DropdownMenuPrimitive.Group

const DropdownMenuPortal = DropdownMenuPrimitive.Portal

const DropdownMenuSub = DropdownMenuPrimitive.Sub

const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup

const DropdownMenuSubTrigger = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.SubTrigger>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.SubTrigger> & {
		inset?: boolean
	}
>(({ className, inset, children, ...props }, ref) => (
	<DropdownMenuPrimitive.SubTrigger
		className={cn(
			'flex cursor-default select-none items-center rounded-sm px-4 py-2 text-sm outline-none focus:bg-accent data-[state=open]:bg-accent sm:px-2 sm:py-1.5 sm:text-xs',
			inset && 'pl-8 sm:pl-8',
			className
		)}
		ref={ref}
		{...props}
	>
		{children}
		<IoChevronForward className='ml-auto h-5 w-5 sm:h-4 sm:w-4' />
	</DropdownMenuPrimitive.SubTrigger>
))
DropdownMenuSubTrigger.displayName =
	DropdownMenuPrimitive.SubTrigger.displayName

const DropdownMenuSubContent = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.SubContent>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.SubContent>
>(({ className, ...props }, ref) => (
	<DropdownMenuPrimitive.SubContent
		className={cn(
			'z-50 min-w-[8rem] flex flex-col gap-0.5 overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
			className
		)}
		ref={ref}
		{...props}
	/>
))
DropdownMenuSubContent.displayName =
	DropdownMenuPrimitive.SubContent.displayName

const dropdownContentVariants = cva(
	'z-50 min-w-[8rem] flex flex-col gap-0.5 overflow-hidden p-1 text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 rounded-xl border border-border/50 bg-background/90 backdrop-blur-xs shadow-2xl shadow-black/5 [&_[role="menuitem"]]:rounded-lg [&_[role="menuitem"]]:border [&_[role="menuitem"]]:border-transparent [&_[role="menuitem"]]:cursor-pointer [&_[role="menuitem"]]:transition-all [&_[role="menuitem"]]:duration-200 [&_[role="menuitem"]]:ease-out [&_[role="menuitem"]]:focus:border-primary/20 [&_[role="menuitem"]]:focus:shadow-sm [&_[role="menuitem"][data-destructive="true"]]:focus:border-destructive/20 [&_[role="menuitem"][data-destructive="true"]]:focus:shadow-sm [&_[role="menuitem"]:data-[state=open]:animate-in [&_[role="menuitem"]:data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
	{
		variants: {
			variant: {
				default: ''
			}
		}
	}
)

const DropdownMenuContent = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.Content>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content> &
		VariantProps<typeof dropdownContentVariants>
>(({ className, sideOffset = 4, variant, ...props }, ref) => (
	<DropdownMenuPrimitive.Portal>
		<DropdownMenuPrimitive.Content
			className={cn(dropdownContentVariants({ className, variant }))}
			ref={ref}
			sideOffset={sideOffset}
			{...props}
		/>
	</DropdownMenuPrimitive.Portal>
))
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName

const dropdownMenuItemVariants = cva(
	'relative flex cursor-default select-none items-center px-4 py-2 text-sm outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 sm:px-2 sm:py-1.5 sm:text-xs',
	{
		defaultVariants: {
			variant: 'default'
		},
		variants: {
			variant: {
				default:
					'rounded-sm transition-colors focus:bg-accent focus:text-accent-foreground',
				destructive:
					'rounded-sm transition-colors focus:bg-destructive-accent focus:text-destructive-accent-foreground'
			}
		}
	}
)

const DropdownMenuItem = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.Item>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> &
		VariantProps<typeof dropdownMenuItemVariants> & {
			inset?: boolean
		}
>(({ className, inset, variant, ...props }, ref) => (
	<DropdownMenuPrimitive.Item
		className={cn(
			dropdownMenuItemVariants({ variant }),
			inset && 'pl-8',
			className
		)}
		data-destructive={variant === 'destructive' ? 'true' : undefined}
		ref={ref}
		{...props}
	/>
))
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName

const DropdownMenuCheckboxItem = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.CheckboxItem>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.CheckboxItem>
>(({ className, children, checked, ...props }, ref) => {
	const itemProps: Omit<
		React.ComponentProps<typeof DropdownMenuPrimitive.CheckboxItem>,
		'ref'
	> = {
		className: cn(
			'relative flex cursor-default select-none items-center rounded-sm py-2 pl-8 pr-4 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-disabled:pointer-events-none data-disabled:opacity-50 sm:py-1.5 sm:pr-2 sm:text-xs',
			className
		),
		...props
	}

	if (checked !== undefined) {
		itemProps.checked = checked
	}

	return (
		<DropdownMenuPrimitive.CheckboxItem
			ref={ref}
			{...itemProps}
		>
			<span className='absolute left-2 flex h-5 w-5 items-center justify-center sm:h-3.5 sm:w-3.5'>
				<DropdownMenuPrimitive.ItemIndicator>
					<IoCheckmark className='h-4 w-4 sm:h-3 sm:w-3' />
				</DropdownMenuPrimitive.ItemIndicator>
			</span>
			{children}
		</DropdownMenuPrimitive.CheckboxItem>
	)
})
DropdownMenuCheckboxItem.displayName =
	DropdownMenuPrimitive.CheckboxItem.displayName

const DropdownMenuRadioItem = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.RadioItem>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.RadioItem>
>(({ className, children, ...props }, ref) => (
	<DropdownMenuPrimitive.RadioItem
		className={cn(
			'relative flex cursor-default select-none items-center rounded-sm py-2 pl-8 pr-4 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-disabled:pointer-events-none data-disabled:opacity-50 sm:py-1.5 sm:pr-2 sm:text-xs',
			className
		)}
		ref={ref}
		{...props}
	>
		<span className='absolute left-2 flex h-5 w-5 items-center justify-center sm:h-3.5 sm:w-3.5'>
			<DropdownMenuPrimitive.ItemIndicator>
				<IoEllipse className='h-3 w-3 fill-current sm:h-2 sm:w-2' />
			</DropdownMenuPrimitive.ItemIndicator>
		</span>
		{children}
	</DropdownMenuPrimitive.RadioItem>
))
DropdownMenuRadioItem.displayName = DropdownMenuPrimitive.RadioItem.displayName

const DropdownMenuLabel = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.Label>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label> & {
		inset?: boolean
	}
>(({ className, inset, ...props }, ref) => (
	<DropdownMenuPrimitive.Label
		className={cn(
			'px-4 py-2 text-sm font-semibold sm:px-2 sm:py-1.5 sm:text-xs',
			inset && 'pl-8 sm:pl-8',
			className
		)}
		ref={ref}
		{...props}
	/>
))
DropdownMenuLabel.displayName = DropdownMenuPrimitive.Label.displayName

const DropdownMenuSeparator = React.forwardRef<
	React.ElementRef<typeof DropdownMenuPrimitive.Separator>,
	React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>
>(({ className, ...props }, ref) => (
	<DropdownMenuPrimitive.Separator
		className={cn('-mx-1 my-1 h-px bg-border', className)}
		ref={ref}
		{...props}
	/>
))
DropdownMenuSeparator.displayName = DropdownMenuPrimitive.Separator.displayName

const DropdownMenuShortcut = ({
	className,
	...props
}: React.HTMLAttributes<HTMLSpanElement>) => {
	return (
		<span
			className={cn(
				'ml-auto text-sm tracking-widest opacity-60 sm:text-xs',
				className
			)}
			{...props}
		/>
	)
}
DropdownMenuShortcut.displayName = 'DropdownMenuShortcut'

export {
	DropdownMenu,
	DropdownMenuCheckboxItem,
	DropdownMenuContent,
	DropdownMenuGroup,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuPortal,
	DropdownMenuRadioGroup,
	DropdownMenuRadioItem,
	DropdownMenuSeparator,
	DropdownMenuShortcut,
	DropdownMenuSub,
	DropdownMenuSubContent,
	DropdownMenuSubTrigger,
	DropdownMenuTrigger
}

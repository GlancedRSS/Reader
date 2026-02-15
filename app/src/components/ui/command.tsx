'use client'

import { cva } from 'class-variance-authority'
import { Command as CommandPrimitive } from 'cmdk'
import * as React from 'react'
import { IoSearch } from 'react-icons/io5'

import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'

import type { VariantProps } from 'class-variance-authority'

import { cn } from '@/utils'

const commandVariants = cva(
	'text-popover-foreground flex h-full w-full flex-col overflow-hidden rounded-xl border border-border/50 bg-background/95 backdrop-blur-xs shadow-2xl',
	{
		variants: {
			variant: {
				default: ''
			}
		}
	}
)

function Command({
	className,
	variant,
	...props
}: React.ComponentProps<typeof CommandPrimitive> &
	VariantProps<typeof commandVariants>) {
	return (
		<CommandPrimitive
			className={cn(commandVariants({ variant }), className)}
			data-slot='command'
			style={{
				backgroundImage:
					'radial-gradient(ellipse 60% 2px at 50% 0%, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 50%, transparent 80%)',
				backgroundPosition: 'top center',
				backgroundRepeat: 'no-repeat'
			}}
			{...props}
		/>
	)
}

function CommandDialog({
	title = 'Command Palette',
	description = 'Search for a command to run...',
	children,
	className,
	showCloseButton = true,
	variant,
	shouldFilter,
	...props
}: React.ComponentProps<typeof Dialog> & {
	title?: string
	description?: string
	className?: string
	showCloseButton?: boolean
	variant?: 'default'
	shouldFilter?: boolean
}) {
	return (
		<Dialog {...props}>
			<DialogHeader className='sr-only'>
				<DialogTitle>{title}</DialogTitle>
				<DialogDescription>{description}</DialogDescription>
			</DialogHeader>
			<DialogContent
				className={cn('overflow-hidden p-0', className)}
				showCloseButton={showCloseButton}
			>
				<Command
					className='**:[[cmdk-group-heading]]:text-muted-foreground **:data-[slot=command-input-wrapper]:h-12 **:[[cmdk-group-heading]]:px-2 **:[[cmdk-group-heading]]:font-medium **:[[cmdk-group]]:px-2 [&_[cmdk-group]:not([hidden])_~[cmdk-group]]:pt-0 [&_[cmdk-input-wrapper]_svg]:h-5 [&_[cmdk-input-wrapper]_svg]:w-5 **:[[cmdk-input]]:h-12 **:[[cmdk-item]]:px-2 **:[[cmdk-item]]:py-3 [&_[cmdk-item]_svg]:h-5 [&_[cmdk-item]_svg]:w-5'
					{...(shouldFilter !== undefined && { shouldFilter })}
					variant={variant}
				>
					{children}
				</Command>
			</DialogContent>
		</Dialog>
	)
}

function CommandInput({
	className,
	...props
}: React.ComponentProps<typeof CommandPrimitive.Input>) {
	return (
		<div
			className='flex h-9 items-center gap-2 border-b px-3 bg-transparent'
			data-slot='command-input-wrapper'
		>
			<IoSearch className='size-4 shrink-0 opacity-50' />
			<CommandPrimitive.Input
				className={cn(
					'placeholder:text-muted-foreground flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-hidden disabled:cursor-not-allowed disabled:opacity-50',
					className
				)}
				data-slot='command-input'
				{...props}
			/>
		</div>
	)
}

function CommandList({
	className,
	...props
}: React.ComponentProps<typeof CommandPrimitive.List>) {
	return (
		<ScrollArea className='h-[300px]'>
			<CommandPrimitive.List
				className={cn('scroll-py-1 pb-1', className)}
				data-slot='command-list'
				{...props}
			/>
		</ScrollArea>
	)
}

function CommandEmpty({
	...props
}: React.ComponentProps<typeof CommandPrimitive.Empty>) {
	return (
		<CommandPrimitive.Empty
			className='py-32 text-center text-sm'
			data-slot='command-empty'
			{...props}
		/>
	)
}

function CommandGroup({
	className,
	...props
}: React.ComponentProps<typeof CommandPrimitive.Group>) {
	return (
		<CommandPrimitive.Group
			className={cn(
				'text-foreground **:[[cmdk-group-heading]]:text-muted-foreground overflow-hidden p-1 **:[[cmdk-group-heading]]:px-2 **:[[cmdk-group-heading]]:py-1.5 **:[[cmdk-group-heading]]:text-xs **:[[cmdk-group-heading]]:font-medium',
				className
			)}
			data-slot='command-group'
			{...props}
		/>
	)
}

function CommandSeparator({
	className,
	...props
}: React.ComponentProps<typeof CommandPrimitive.Separator>) {
	return (
		<CommandPrimitive.Separator
			className={cn('bg-border my-1.5 -mx-1 h-px', className)}
			data-slot='command-separator'
			{...props}
		/>
	)
}

function CommandItem({
	className,
	...props
}: React.ComponentProps<typeof CommandPrimitive.Item>) {
	return (
		<CommandPrimitive.Item
			className={cn(
				"data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground [&_svg:not([class*='text-'])]:text-muted-foreground relative flex cursor-pointer items-center gap-2 rounded-lg border border-transparent px-2 py-2! text-sm outline-hidden select-none transition-all duration-100 ease-out data-[selected=true]:border-primary/20 data-[selected=true]:shadow-sm data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
				className
			)}
			data-slot='command-item'
			{...props}
		/>
	)
}

function CommandShortcut({
	className,
	...props
}: React.ComponentProps<'span'>) {
	return (
		<span
			className={cn(
				'text-muted-foreground ml-auto text-xs tracking-widest',
				className
			)}
			data-slot='command-shortcut'
			{...props}
		/>
	)
}

export {
	Command,
	CommandDialog,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem,
	CommandList,
	CommandSeparator,
	CommandShortcut
}

'use client'

import * as React from 'react'
import { IoEye, IoEyeOff } from 'react-icons/io5'
import { LuCircleAlert } from 'react-icons/lu'

import { Input } from '@/components/ui/input'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

import { cn } from '@/utils'
import { getPasswordStrength } from '@/utils/auth'

interface PasswordProps extends React.ComponentProps<'input'> {
	error?: string | null
	showRequirements?: boolean
}

export function Password({
	className,
	error,
	showRequirements = false,
	...props
}: PasswordProps) {
	const [isVisible, setIsVisible] = React.useState(false)
	const [passwordStrength, setPasswordStrength] = React.useState(
		getPasswordStrength('')
	)

	const toggleVisibility = () => setIsVisible(!isVisible)

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (showRequirements) {
			setPasswordStrength(getPasswordStrength(e.target.value))
		}
		props.onChange?.(e)
	}

	const shouldShowTooltip =
		showRequirements &&
		props.value &&
		(passwordStrength.feedback.suggestions.length ||
			passwordStrength.feedback.warning)

	return (
		<div className='space-y-4'>
			<div className='relative mb-0!'>
				<Input
					{...props}
					className={cn(
						'pr-24 sm:pr-20',
						'placeholder:text-foreground/60 bg-background/80',
						error &&
							'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20',
						className
					)}
					onChange={handleChange}
					type={isVisible ? 'text' : 'password'}
				/>

				{shouldShowTooltip ? (
					<Tooltip>
						<TooltipTrigger asChild>
							<button
								className='absolute right-10 top-0 h-full px-2 items-center justify-center hover:bg-transparent focus:outline-none focus:ring-0 transition-all duration-200 group hidden md:flex'
								tabIndex={-1}
								type='button'
							>
								<LuCircleAlert className='h-4 w-4 text-muted-foreground/50 group-hover:text-muted-foreground group-active:text-foreground transition-colors duration-200' />
							</button>
						</TooltipTrigger>
						<TooltipContent
							className='max-w-xs p-3 bg-background border shadow-lg'
							side='right'
							sideOffset={8}
						>
							<div className='space-y-2'>
								{passwordStrength.feedback.suggestions.length > 0 ? (
									<div className='space-y-4'>
										{passwordStrength.feedback.suggestions.map(
											(suggestion, index) => (
												<div
													className='flex items-start gap-2.5'
													key={index}
												>
													<span className='w-1.5 h-1.5 bg-muted-foreground rounded-full mt-1.5 shrink-0'></span>
													<p className='text-xs text-muted-foreground leading-relaxed'>
														{suggestion}
													</p>
												</div>
											)
										)}
									</div>
								) : null}

								{passwordStrength.feedback.warning ? (
									<div
										className={`flex items-start gap-2.5 ${passwordStrength.feedback.suggestions.length > 0 ? 'pt-2 border-t' : ''}`}
									>
										<span className='w-1.5 h-1.5 bg-muted-foreground rounded-full mt-1.5 shrink-0'></span>
										<p className='text-xs text-muted-foreground leading-relaxed'>
											{passwordStrength.feedback.warning}
										</p>
									</div>
								) : null}
							</div>
						</TooltipContent>
					</Tooltip>
				) : null}

				<button
					className='absolute right-0 top-0 h-full px-4 py-2 flex items-center justify-center hover:bg-transparent focus:outline-none focus:ring-0 transition-all duration-200 group sm:px-3'
					onClick={toggleVisibility}
					tabIndex={-1}
					type='button'
				>
					{isVisible ? (
						<IoEyeOff className='h-5 w-5 text-muted-foreground/50 group-hover:text-muted-foreground group-active:text-foreground transition-colors duration-200 sm:h-4 sm:w-4' />
					) : (
						<IoEye className='h-5 w-5 text-muted-foreground/50 group-hover:text-muted-foreground group-active:text-foreground transition-colors duration-200 sm:h-4 sm:w-4' />
					)}
				</button>
			</div>

			{error ? <p className='text-xs text-destructive'>{error}</p> : null}
		</div>
	)
}

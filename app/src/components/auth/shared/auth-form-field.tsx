import { forwardRef } from 'react'

import { Input } from '@/components/ui/input'

interface AuthFormFieldProps {
	id: string
	type: string
	value: string
	onChange: (value: string) => void
	error?: string | null
	placeholder?: string
	autoComplete?: string
	autoFocus?: boolean
	maxLength?: number
	minLength?: number
	pattern?: string
	'aria-label'?: string
	required?: boolean
}

export const AuthFormField = forwardRef<HTMLInputElement, AuthFormFieldProps>(
	(
		{
			id,
			type,
			value,
			onChange,
			error,
			placeholder,
			autoComplete,
			autoFocus,
			maxLength,
			minLength,
			pattern,
			'aria-label': ariaLabel,
			required
		},
		ref
	) => {
		return (
			<>
				<Input
					aria-describedby={error ? `${id}-error` : undefined}
					aria-invalid={!!error}
					aria-label={ariaLabel}
					autoComplete={autoComplete}
					autoFocus={autoFocus}
					className='placeholder:text-foreground/60 bg-background/80'
					maxLength={maxLength}
					minLength={minLength}
					onChange={(e) => onChange(e.target.value)}
					pattern={pattern}
					placeholder={placeholder}
					ref={ref}
					required={required}
					type={type}
					value={value}
				/>
				{error ? (
					<p
						className='text-xs text-destructive'
						id={`${id}-error`}
						role='alert'
					>
						{error}
					</p>
				) : null}
			</>
		)
	}
)

AuthFormField.displayName = 'AuthFormField'

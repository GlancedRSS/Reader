'use client'

import {
	AuthFormField,
	AuthSubmitButton,
	BaseAuthForm
} from '@/components/auth/shared'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { toast } from 'sonner'

import { Label } from '@/components/ui/label'
import { Password } from '@/components/ui/password'

import { register } from '@/hooks/api/auth'

export function SignUpForm() {
	const router = useRouter()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [isLoading, setIsLoading] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()

		setIsLoading(true)
		try {
			await register({ password, username })
			toast.success('Account created! Please sign in.')
			router.push('/sign-in')
		} catch (err) {
			toast.error(err instanceof Error ? err.message : 'Registration failed')
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<BaseAuthForm
			heading="Welcome! Let's create your account"
			onSubmit={handleSubmit}
		>
			<div className='flex flex-col gap-2'>
				<Label htmlFor='username'>Username</Label>
				<AuthFormField
					aria-label='Username'
					autoComplete='username'
					autoFocus
					id='username'
					onChange={(value) => setUsername(value)}
					placeholder='Choose a username'
					type='text'
					value={username}
				/>
			</div>

			<div className='flex flex-col gap-2'>
				<Label htmlFor='password'>Password</Label>
				<Password
					aria-label='Create password'
					id='password'
					onChange={(e) => setPassword(e.target.value)}
					placeholder='Create a strong password'
					showRequirements
					value={password}
				/>
			</div>

			<AuthSubmitButton
				disabled={!username.trim() || !password.trim()}
				isLoading={isLoading}
				loadingText='Creating Account...'
				text='Create Account'
			/>

			<div className='text-center text-sm'>
				<span className='text-muted-foreground/80'>
					Already have an account?{' '}
				</span>
				<Link
					className='text-muted-foreground/80 hover:text-accent-foreground transition-colors duration-200 underline'
					href='/sign-in'
				>
					Sign In
				</Link>
			</div>
		</BaseAuthForm>
	)
}

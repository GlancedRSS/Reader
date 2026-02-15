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

import { login } from '@/hooks/api/auth'

interface SignInFormProps {
	redirectUrl?: string | undefined
}

export function SignInForm({ redirectUrl }: SignInFormProps) {
	const router = useRouter()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [isLoading, setIsLoading] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()

		setIsLoading(true)
		try {
			await login({ password, username })
			toast.success('Welcome back!')
			router.push(redirectUrl || '/')
		} catch (err) {
			toast.error(err instanceof Error ? err.message : 'Login failed')
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<BaseAuthForm
			heading='Welcome back! Sign in to your account'
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
					placeholder='Enter your username'
					type='text'
					value={username}
				/>
			</div>

			<div className='flex flex-col gap-2'>
				<Label htmlFor='password'>Password</Label>
				<Password
					aria-label='Password'
					id='password'
					onChange={(e) => setPassword(e.target.value)}
					placeholder='Enter your password'
					showRequirements={false}
					value={password}
				/>
			</div>

			<AuthSubmitButton
				disabled={!username.trim() || !password.trim()}
				isLoading={isLoading}
				loadingText='Signing In...'
				text='Sign In'
			/>

			<div className='text-center text-sm'>
				<span className='text-muted-foreground/80'>
					Don&apos;t have an account?{' '}
				</span>
				<Link
					className='text-muted-foreground/80 hover:text-accent-foreground transition-colors duration-200 underline'
					href='/sign-up'
				>
					Sign Up
				</Link>
			</div>
		</BaseAuthForm>
	)
}

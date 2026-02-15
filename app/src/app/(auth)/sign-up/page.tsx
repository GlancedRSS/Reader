import { SignUpForm } from '@/components/auth'

import type { Metadata } from 'next'

export const metadata: Metadata = {
	title: 'Sign Up | Glanced Reader'
}

export default function SignUpPage() {
	return (
		<div className='flex flex-col gap-4'>
			<SignUpForm />
		</div>
	)
}

import { SignInForm } from '@/components/auth'

import type { Metadata } from 'next'

export const metadata: Metadata = {
	title: 'Sign In | Glanced Reader'
}

export default async function SignInPage(props: {
	searchParams: Promise<{ redirect?: string }>
}) {
	const searchParams = await props.searchParams
	const redirectUrl = searchParams.redirect

	return (
		<div className='flex flex-col gap-4'>
			<SignInForm redirectUrl={redirectUrl} />
		</div>
	)
}

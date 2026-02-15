import { Logo } from '@/components'

import { Card, CardHeader } from '@/components/ui/card'

export default function AuthLayout({
	children
}: {
	children: React.ReactNode
}) {
	return (
		<div className='flex items-center justify-center w-screen h-dvh'>
			<div className='sm:hidden w-full h-full flex flex-col justify-center px-6'>
				<div className='flex flex-col space-y-4'>
					<div className='flex items-center justify-center'>
						<Logo size='large' />
					</div>
					<div>{children}</div>
				</div>
			</div>

			<Card
				className='hidden sm:block max-w-96 p-6 w-full rounded-2xl'
				variant='translucent'
			>
				<CardHeader className='flex items-center justify-center py-4'>
					<Logo />
				</CardHeader>
				{children}
			</Card>
		</div>
	)
}

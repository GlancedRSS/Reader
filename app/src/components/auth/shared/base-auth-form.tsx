'use client'

interface BaseAuthFormProps {
	children: React.ReactNode
	heading: string
	onSubmit: (e: React.FormEvent) => void
}

export function BaseAuthForm({
	children,
	heading,
	onSubmit
}: BaseAuthFormProps) {
	return (
		<div className='flex flex-col'>
			<div className='flex flex-col gap-6'>
				<div className='text-center'>
					<h1 className='text-muted-foreground/80'>{heading}</h1>
				</div>

				<form
					className='flex flex-col gap-4'
					onSubmit={onSubmit}
				>
					{children}
				</form>
			</div>
		</div>
	)
}

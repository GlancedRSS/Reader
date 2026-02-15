import { ReactNode } from 'react'

interface SectionProps {
	title: string
	children: ReactNode
}

export function Section({ title, children }: SectionProps) {
	return (
		<div className='space-y-3'>
			<h3 className='text-base font-semibold'>{title}</h3>
			<div className='space-y-6'>{children}</div>
		</div>
	)
}

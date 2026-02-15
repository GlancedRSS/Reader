'use client'

import Link from 'next/link'
import { useRef } from 'react'

import { Button } from '@/components/ui/button'

import { useStaggerReveal } from '@/hooks/ui/stagger-reveal'

export default function NotFound() {
	const containerRef = useRef<HTMLDivElement>(null)
	const textRef = useRef<HTMLDivElement>(null)

	useStaggerReveal(containerRef, textRef)

	return (
		<div
			className='flex min-h-screen items-center justify-center p-6'
			ref={containerRef}
			style={{ opacity: 0 }}
		>
			<div className='max-w-md text-center'>
				<div
					className='space-y-4'
					ref={textRef}
				>
					<div>
						<h1 className='text-7xl font-bold text-foreground'>404</h1>
						<h2 className='mt-2 text-xl font-semibold text-foreground'>
							Nothing to See Here
						</h2>
					</div>
					<p className='text-muted-foreground'>
						Well, this is awkward. The page you wanted isn&apos;t here.
					</p>
					<div className='flex justify-center pt-4'>
						<Button
							asChild
							variant='default'
						>
							<Link href='/'>Go Home</Link>
						</Button>
					</div>
				</div>
			</div>
		</div>
	)
}

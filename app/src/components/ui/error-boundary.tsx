'use client'

import React from 'react'
import { IoAlertCircleOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface ErrorBoundaryProps {
	children: React.ReactNode
	fallback?: React.ComponentType<{ error: Error; reset: () => void }>
}

interface ErrorBoundaryState {
	hasError: boolean
	error: Error | null
}

export class ErrorBoundary extends React.Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props)
		this.state = { error: null, hasError: false }
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { error, hasError: true }
	}

	componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		console.error('Error caught by boundary:', error, errorInfo)
	}

	reset = () => {
		this.setState({ error: null, hasError: false })
	}

	render() {
		if (this.state.hasError && this.state.error) {
			const FallbackComponent = this.props.fallback || DefaultErrorFallback
			return (
				<FallbackComponent
					error={this.state.error}
					reset={this.reset}
				/>
			)
		}

		return this.props.children
	}
}

function DefaultErrorFallback({
	error,
	reset
}: {
	error: Error
	reset: () => void
}) {
	return (
		<Card className='p-6'>
			<div className='flex flex-col items-center justify-center text-center'>
				<div className='mb-4'>
					<div className='w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mx-auto'>
						<IoAlertCircleOutline className='w-8 h-8 text-destructive' />
					</div>
				</div>
				<h2 className='text-lg font-semibold mb-2'>Something went wrong</h2>
				<p className='text-sm text-muted-foreground mb-6 max-w-md'>
					{error.message ||
						'An unexpected error occurred while loading this content.'}
				</p>
				<Button onClick={reset}>Try again</Button>
			</div>
		</Card>
	)
}

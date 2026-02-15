'use client'

import React from 'react'

interface ErrorBoundaryState {
	hasError: boolean
	error?: Error
}

class VirtualizationErrorBoundary extends React.Component<
	React.PropsWithChildren<Record<string, never>>,
	ErrorBoundaryState
> {
	constructor(props: React.PropsWithChildren<Record<string, never>>) {
		super(props)
		this.state = { hasError: false }
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { error, hasError: true }
	}

	componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		console.error('Virtualization Error Boundary caught:', error, errorInfo)
	}

	render() {
		if (this.state.hasError) {
			return (
				<div className='flex flex-col items-center justify-center h-64 p-4'>
					<div className='text-center space-y-4'>
						<h3 className='text-lg font-semibold text-destructive'>
							Something went wrong with article display
						</h3>
						<p className='text-muted-foreground max-w-md'>
							{this.state.error?.message ||
								'There was an error rendering the articles. Please refresh the page or try again later.'}
						</p>
						<button
							className='px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors'
							onClick={() => window.location.reload()}
						>
							Refresh Page
						</button>
					</div>
				</div>
			)
		}

		return this.props.children
	}
}

export default VirtualizationErrorBoundary

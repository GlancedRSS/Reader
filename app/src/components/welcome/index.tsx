'use client'

import { Logo } from '@/components/logo'
import { useRef } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'

import { useDiscoveryFlow } from '@/hooks/features/discovery'
import { useStaggerReveal } from '@/hooks/ui/stagger-reveal'

export function Welcome() {
	const containerRef = useRef<HTMLDivElement>(null)
	const contentRef = useRef<HTMLDivElement>(null)

	useStaggerReveal(containerRef, contentRef, {
		delay: 0.2,
		duration: 0.5,
		stagger: 0.1
	})

	const discovery = useDiscoveryFlow({
		onSuccess: () => {}
	})

	return (
		<div
			className='flex items-center justify-center min-h-dvh w-full'
			ref={containerRef}
		>
			<div
				className='max-w-md w-full mx-auto px-6'
				ref={contentRef}
			>
				<div className='flex justify-center mb-6'>
					<Logo
						size='large'
						variant='logo'
					/>
				</div>

				<div className='text-center space-y-2 mb-8'>
					<h1 className='text-2xl font-semibold tracking-tight'>
						Let&apos;s add some feeds
					</h1>
					<p className='text-muted-foreground text-sm'>
						Subscribe via RSS or import from OPML
					</p>
				</div>

				<div className='space-y-4'>
					{discovery.showSelect ? (
						<div className='space-y-2'>
							<Label>Select a feed</Label>
							<Select
								disabled={discovery.isSubscribing}
								onValueChange={discovery.setSelectedFeedUrl}
								value={discovery.selectedFeedUrl}
							>
								<SelectTrigger>
									<SelectValue placeholder='Select a feed' />
								</SelectTrigger>
								<SelectContent>
									{discovery.feeds.map((feedUrl) => (
										<SelectItem
											key={feedUrl}
											value={feedUrl}
										>
											{feedUrl}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>
					) : (
						<div className='space-y-2'>
							<Label htmlFor='url'>Website URL</Label>
							<Input
								autoFocus
								disabled={discovery.isDiscovering}
								id='url'
								onChange={(e) => discovery.setUrl(e.target.value)}
								onKeyDown={(e) => {
									if (e.key === 'Enter' && discovery.url.trim()) {
										discovery.handleDiscoverFeeds()
									}
								}}
								placeholder='https://example.com'
								type='url'
								value={discovery.url}
							/>
						</div>
					)}

					<input
						accept='.opml'
						className='hidden'
						disabled={discovery.isImporting}
						onChange={discovery.handleOpmlImport}
						ref={discovery.fileInputRef}
						type='file'
					/>

					{discovery.showSelect ? (
						<div className='flex gap-2'>
							<Button
								className='flex-1'
								disabled={discovery.isSubscribing}
								onClick={discovery.resetToInitial}
								variant='outline'
							>
								Back
							</Button>
							<Button
								className='flex-1'
								disabled={discovery.isSubscribing || !discovery.selectedFeedUrl}
								onClick={discovery.handleSubscribe}
							>
								{discovery.isSubscribing ? 'Subscribing...' : 'Subscribe'}
							</Button>
						</div>
					) : (
						<div className='flex gap-2'>
							<Button
								className='flex-1'
								disabled={discovery.isImporting || discovery.isDiscovering}
								onClick={() => discovery.fileInputRef.current?.click()}
								variant='outline'
							>
								{discovery.isImporting ? 'Importing...' : 'Import OPML'}
							</Button>
							<Button
								className='flex-1'
								disabled={discovery.isDiscovering || !discovery.url.trim()}
								onClick={discovery.handleDiscoverFeeds}
							>
								{discovery.isDiscovering ? 'Discovering...' : 'Discover Feeds'}
							</Button>
						</div>
					)}
				</div>
			</div>
		</div>
	)
}

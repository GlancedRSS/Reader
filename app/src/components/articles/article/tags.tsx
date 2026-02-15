'use client'

import Link from 'next/link'
import * as React from 'react'

import { Button } from '@/components/ui/button'
import {
	Popover,
	PopoverContent,
	PopoverTrigger
} from '@/components/ui/popover'
import { Skeleton } from '@/components/ui/skeleton'

import type { TagListResponse } from '@/types/api'

const textMeasurementCache = new Map<string, number>()

function estimateTagWidth(tagName: string): number {
	if (textMeasurementCache.has(tagName)) {
		return textMeasurementCache.get(tagName)!
	}

	const canvas = document.createElement('canvas')
	const context = canvas.getContext('2d')
	if (!context) {
		const fallback = 100
		textMeasurementCache.set(tagName, fallback)
		return fallback
	}

	context.font = '12px system-ui, -apple-system, sans-serif'
	const textWidth = context.measureText(tagName).width

	const width = textWidth + 24 + 8

	textMeasurementCache.set(tagName, width)

	return width
}

export default function Tags({
	data,
	loading
}: {
	data: TagListResponse[]
	loading: boolean
}) {
	const containerRef = React.useRef<HTMLDivElement>(null)
	const [visibleTagCount, setVisibleTagCount] = React.useState(data.length)

	const calculateVisibleTags = React.useCallback(() => {
		const container = containerRef.current
		if (!container) return

		const containerWidth = container.offsetWidth
		const gapWidth = 12
		const moreButtonWidth = 80

		let accumulatedWidth = 0
		let visibleCount = 0

		for (let i = 0; i < data.length; i++) {
			const tagWidth = estimateTagWidth(data?.[i]?.name as string)
			const hasMoreTags = i < data.length - 1
			const totalWidth =
				accumulatedWidth +
				tagWidth +
				(i > 0 ? gapWidth : 0) +
				(hasMoreTags ? moreButtonWidth + gapWidth : 0)

			if (totalWidth <= containerWidth) {
				accumulatedWidth += tagWidth + (i > 0 ? gapWidth : 0)
				visibleCount++
			} else {
				break
			}
		}

		setVisibleTagCount(visibleCount)
	}, [data])

	React.useEffect(() => {
		const container = containerRef.current
		if (!container) return

		const resizeObserver = new ResizeObserver(() => {
			calculateVisibleTags()
		})

		resizeObserver.observe(container)
		calculateVisibleTags()

		return () => {
			resizeObserver.disconnect()
		}
	}, [calculateVisibleTags])

	React.useEffect(() => {
		calculateVisibleTags()
	}, [data, calculateVisibleTags])

	if (loading) {
		return (
			<div className='flex items-center gap-3 pb-4'>
				<Skeleton className='h-6.5 w-20 rounded-full' />
				<Skeleton className='h-6.5 w-24 rounded-full' />
				<Skeleton className='h-6.5 w-16 rounded-full' />
			</div>
		)
	}

	if (!data.length) {
		return null
	}

	const visibleTags = data.slice(0, visibleTagCount)
	const hiddenTags = data.slice(visibleTagCount)
	const hasHiddenTags = hiddenTags.length > 0

	return (
		<div
			className='flex items-center gap-3 mb-4 overflow-hidden'
			ref={containerRef}
		>
			{visibleTags.map((tag) => (
				<Button
					asChild
					className='px-3 py-1 h-auto text-xs rounded-full shrink-0'
					key={tag.id}
					size='standard'
					variant='muted'
				>
					<Link href={`/tags/${tag.id}`}>{tag.name}</Link>
				</Button>
			))}

			{hasHiddenTags ? (
				<Popover>
					<PopoverTrigger asChild>
						<Button
							aria-label={`Show ${hiddenTags.length} more tags`}
							className='px-3 py-1 h-auto text-xs rounded-full shrink-0'
							size='standard'
							variant='muted'
						>
							+{hiddenTags.length}
						</Button>
					</PopoverTrigger>
					<PopoverContent
						align='start'
						className='w-auto max-w-sm'
					>
						<div className='flex flex-wrap gap-2 max-h-32 overflow-y-auto'>
							{hiddenTags.map((tag) => (
								<Button
									asChild
									className='px-2 py-1 h-auto text-xs rounded-full'
									key={tag.id}
									size='standard'
									variant='muted'
								>
									<Link href={`/tags/${tag.id}`}>{tag.name}</Link>
								</Button>
							))}
						</div>
					</PopoverContent>
				</Popover>
			) : null}
		</div>
	)
}

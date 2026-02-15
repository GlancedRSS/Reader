'use client'

import ArticleContainer from '@/components/articles/article/container'
import { useLayoutStore } from '@/stores/layout'

import { Separator } from '@/components/ui/separator'

interface SplitLayoutProps {
	children?: React.ReactNode
}

export function SplitLayout({ children }: SplitLayoutProps) {
	const { selectedArticleId } = useLayoutStore()

	return (
		<div className='flex'>
			<div className='w-sm mx-auto'>{children}</div>
			<Separator
				className='h-dvh'
				orientation='vertical'
			/>
			<div className='flex-1'>
				{selectedArticleId ? (
					<div className='h-full'>
						<ArticleContainer id={selectedArticleId} />
					</div>
				) : (
					<div className='h-full flex items-center justify-center text-muted-foreground'>
						<div className='text-center'>
							<p className='text-lg font-medium'>Select an article to read</p>
							<p className='text-sm mt-2'>
								Choose an article from the list to view it here
							</p>
						</div>
					</div>
				)}
			</div>
		</div>
	)
}

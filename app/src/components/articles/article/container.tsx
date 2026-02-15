'use client'

import Actions from '@/components/articles/article/actions'
import Content from '@/components/articles/article/content'
import { FloatingNav } from '@/components/articles/article/floating-nav'
import Header from '@/components/articles/article/header'
import Tags from '@/components/articles/article/tags'
import { useRouter } from 'next/navigation'
import { useEffect, useRef } from 'react'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { ErrorBoundary } from '@/components/ui/error-boundary'
import { ScrollArea } from '@/components/ui/scroll-area'

import { useArticle } from '@/hooks/api'
import { useArticleNavigation } from '@/hooks/features/navigation/article'
import useMetadata from '@/hooks/navigation/metadata'

export default function ArticleContainer({ id }: { id: string }) {
	const containerRef = useRef<HTMLDivElement>(null)
	const router = useRouter()
	const { mutate } = useSWRConfig()

	const {
		data: articleData,
		error: articleError,
		isLoading: articleLoading
	} = useArticle(id)

	const { goToNext, goToPrevious, hasNext, hasPrevious } =
		useArticleNavigation(id)

	// Mutate tree cache after article loads (backend marks it as read automatically)
	useEffect(() => {
		if (articleData && !articleLoading) {
			mutate('/folders/tree')
		}
	}, [articleData, articleLoading, mutate])

	useMetadata(
		articleLoading
			? 'Loading... | Glanced Reader'
			: articleData?.title
				? `${articleData?.title} | Glanced Reader`
				: 'Article | Glanced Reader'
	)

	if (articleError) {
		console.error(articleError.message)
		toast.error(articleError.message)
		router.replace('/articles')
	}

	return (
		<>
			<ScrollArea className='px-4 h-[calc(100dvh-3.5rem)] sm:h-dvh'>
				<div
					className='max-w-4xl mx-auto py-4 max-sm:pb-16 sm:pb-28 md:pb-16'
					ref={containerRef}
				>
					<ErrorBoundary>
						<Header
							data={articleData}
							loading={articleLoading}
						/>
					</ErrorBoundary>

					<ErrorBoundary>
						<Tags
							data={articleData?.tags || []}
							loading={articleLoading}
						/>
					</ErrorBoundary>

					<ErrorBoundary>
						<Content
							data={articleData}
							loading={articleLoading}
						/>
					</ErrorBoundary>

					<ErrorBoundary>
						<Actions
							articleId={id}
							articleTags={articleData?.tags || []}
							containerRef={containerRef as React.RefObject<HTMLElement | null>}
							hasNext={hasNext}
							hasPrevious={hasPrevious}
							link={articleData?.canonical_url}
							loading={articleLoading}
							onNext={goToNext}
							onPrevious={goToPrevious}
							readLater={articleData?.read_later}
							title={articleData?.title}
						/>
					</ErrorBoundary>
				</div>
			</ScrollArea>

			<FloatingNav
				disabledLeft={!hasPrevious}
				disabledRight={!hasNext}
				onLeft={goToPrevious}
				onRight={goToNext}
			/>
		</>
	)
}

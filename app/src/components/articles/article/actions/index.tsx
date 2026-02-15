'use client'

import { Bookmark } from '@/components/articles/article/actions/bookmark'
import { Help } from '@/components/articles/article/actions/help'
import { NextArticle } from '@/components/articles/article/actions/next-article'
import { OriginalLink } from '@/components/articles/article/actions/original-link'
import { Preferences } from '@/components/articles/article/actions/preferences'
import { PreviousArticle } from '@/components/articles/article/actions/previous-article'
import { Share } from '@/components/articles/article/actions/share'
import { Tags } from '@/components/articles/article/actions/tags'
import { useRef } from 'react'

import { ButtonGroup } from '@/components/ui/button-group'
import { TooltipProvider } from '@/components/ui/tooltip'

import { useUpdateArticleState } from '@/hooks/api'
import { useContainerBounds } from '@/hooks/ui/container-bounds'
import { useArticleHotkeys } from '@/hooks/ui/layout/keyboard-shortcuts'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { BookmarkRef } from '@/components/articles/article/actions/bookmark'
import type { HelpRef } from '@/components/articles/article/actions/help'
import type { NextArticleRef } from '@/components/articles/article/actions/next-article'
import type { OriginalLinkRef } from '@/components/articles/article/actions/original-link'
import type { PreferencesRef } from '@/components/articles/article/actions/preferences'
import type { PreviousArticleRef } from '@/components/articles/article/actions/previous-article'
import type { ShareRef } from '@/components/articles/article/actions/share'
import type { TagsRef } from '@/components/articles/article/actions/tags'
import type { TagListResponse } from '@/types/api'

export interface ArticleActionsProps {
	articleId: string
	articleTags?: TagListResponse[]
	containerRef?: React.RefObject<HTMLElement | null>
	link: string | undefined
	loading?: boolean
	readLater?: boolean | undefined
	title?: string | undefined
	hasNext?: boolean
	hasPrevious?: boolean
	onNext?: () => void
	onPrevious?: () => void
}

export default function ArticleActions({
	articleId,
	articleTags,
	containerRef,
	hasNext = false,
	hasPrevious = false,
	link,
	loading,
	onNext,
	onPrevious,
	readLater,
	title
}: ArticleActionsProps) {
	const updateArticleState = useUpdateArticleState(articleId)
	const isMobile = useIsMobile()

	const shareRef = useRef<ShareRef>(null)
	const originalLinkRef = useRef<OriginalLinkRef>(null)
	const bookmarkRef = useRef<BookmarkRef>(null)
	const tagsRef = useRef<TagsRef>(null)
	const preferencesRef = useRef<PreferencesRef>(null)
	const helpRef = useRef<HelpRef>(null)
	const previousArticleRef = useRef<PreviousArticleRef>(null)
	const nextArticleRef = useRef<NextArticleRef>(null)
	const defaultContainerRef = useRef<HTMLElement | null>(null)

	useArticleHotkeys(
		{
			'?': () => !isMobile && helpRef.current?.trigger(),
			j: () => !isMobile && onNext?.(),
			k: () => !isMobile && onPrevious?.(),
			p: () => preferencesRef.current?.trigger(),
			s: () => bookmarkRef.current?.trigger(),
			t: () => tagsRef.current?.trigger(),
			v: () => originalLinkRef.current?.trigger()
		},
		!loading
	)

	const bounds = useContainerBounds(containerRef || defaultContainerRef)

	if (loading) {
		return null
	}

	return (
		<TooltipProvider>
			<div
				className='fixed bottom-16 md:bottom-4 z-40 flex justify-center'
				style={{
					left: bounds.left,
					width: bounds.width
				}}
			>
				<div className='bg-background/70 backdrop-blur-xs rounded-xl shadow-2xl'>
					<ButtonGroup className='mx-auto'>
						{!isMobile && (
							<PreviousArticle
								disabled={!hasPrevious}
								onNavigate={onPrevious ?? (() => {})}
								ref={previousArticleRef}
							/>
						)}
						{!isMobile && (
							<NextArticle
								disabled={!hasNext}
								onNavigate={onNext ?? (() => {})}
								ref={nextArticleRef}
							/>
						)}
						<Share
							link={link}
							ref={shareRef}
							title={title}
						/>
						<OriginalLink
							link={link}
							ref={originalLinkRef}
						/>
						<Bookmark
							articleId={articleId}
							readLater={readLater ?? false}
							ref={bookmarkRef}
							updateArticleState={updateArticleState}
						/>
						<Tags
							articleId={articleId}
							articleTags={articleTags ?? []}
							ref={tagsRef}
						/>
						<Preferences ref={preferencesRef} />
						{!isMobile && <Help ref={helpRef} />}
					</ButtonGroup>
				</div>
			</div>
		</TooltipProvider>
	)
}

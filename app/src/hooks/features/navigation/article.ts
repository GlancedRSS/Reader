import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import { useRouter } from 'next/navigation'
import { useMemo } from 'react'

import { useSplitLayout } from '@/hooks/ui/layout'

export function useArticleNavigation(currentArticleId: string) {
	const router = useRouter()
	const allArticles = useArticlesPaginationStore((state) => state.allArticles)
	const markArticleAsRead = useArticlesPaginationStore(
		(state) => state.markArticleAsRead
	)
	const setSelectedArticle = useLayoutStore((state) => state.setSelectedArticle)
	const { shouldShowSplitLayout } = useSplitLayout()

	const currentIndex = useMemo(
		() => allArticles.findIndex((article) => article.id === currentArticleId),
		[allArticles, currentArticleId]
	)

	const hasPrevious = currentIndex > 0
	const hasNext = currentIndex < allArticles.length - 1

	const goToPrevious = () => {
		if (!hasPrevious) return

		const currentArticle = allArticles[currentIndex]!
		if (currentArticle) {
			markArticleAsRead(currentArticle.id)
		}

		const previousArticle = allArticles[currentIndex - 1]!

		if (shouldShowSplitLayout) {
			setSelectedArticle(previousArticle.id)
		} else {
			router.push(`/articles/${previousArticle.id}`)
		}
	}

	const goToNext = () => {
		if (!hasNext) return

		const currentArticle = allArticles[currentIndex]!
		if (currentArticle) {
			markArticleAsRead(currentArticle.id)
		}

		const nextArticle = allArticles[currentIndex + 1]!

		if (shouldShowSplitLayout) {
			setSelectedArticle(nextArticle.id)
		} else {
			router.push(`/articles/${nextArticle.id}`)
		}
	}

	return {
		currentIndex,
		goToNext,
		goToPrevious,
		hasNext,
		hasPrevious,
		totalArticles: allArticles.length
	}
}

import { ArticleListResponse } from '@/types/api'

export function getSelectionClass(
	article: ArticleListResponse | undefined,
	selectedArticleId: string | null,
	type?: 'grid' | 'list' | 'magazine'
) {
	if (article?.id === selectedArticleId) {
		return `bg-accent dark:bg-accent/80 ${type === 'magazine' && 'rounded-xl'}`
	}
	return ''
}

export function getImageClass(article: ArticleListResponse | undefined) {
	if (article?.is_read) {
		return 'grayscale'
	}
	return ''
}

export function getTitleClass(
	article: ArticleListResponse | undefined,
	selectedArticleId: string | null
) {
	if (article?.id === selectedArticleId) {
		return 'text-accent-foreground'
	} else {
		if (article?.is_read) {
			return 'text-muted-foreground'
		}
	}
	return ''
}

export function getPublishedAtClass(
	article: ArticleListResponse | undefined,
	selectedArticleId: string | null
) {
	if (article?.id === selectedArticleId) {
		return 'text-foreground/80'
	}
	return 'text-muted-foreground'
}

export function getSummaryClass(
	article: ArticleListResponse | undefined,
	selectedArticleId: string | null
) {
	if (article?.id === selectedArticleId) {
		return 'text-foreground/90'
	}
	return 'text-muted-foreground'
}

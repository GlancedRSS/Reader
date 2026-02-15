import { createMutation, useStaticSWR } from '@/lib/swr-config'

import type {
	ArticleListQuery,
	ArticleListResponse,
	ArticleResponse,
	ArticleStateUpdateRequest,
	MarkAllReadRequest,
	PaginatedResponse,
	ResponseMessage
} from '@/types/api'
import type { QueryValue } from '@/utils/query'

import { buildQueryParams } from '@/utils/query'

export function useArticles(params?: ArticleListQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = `/articles${queryString ? `?${queryString}` : ''}`

	return useStaticSWR<PaginatedResponse<ArticleListResponse>>(url, {
		errorRetryCount: 0,
		shouldRetryOnError: false
	})
}

export function useArticle(articleId: string) {
	return useStaticSWR<ArticleResponse>(`/articles/${articleId}`)
}

export function useUpdateArticleState(articleId: string) {
	return createMutation<ArticleStateUpdateRequest, ResponseMessage>(
		`/articles/${articleId}`,
		'PUT'
	)
}

export function useMarkAllAsRead() {
	const mutation = createMutation<MarkAllReadRequest, ResponseMessage>(
		'/articles/mark-as-read',
		'POST'
	)

	return {
		...mutation,
		markAsRead: async (params?: Partial<MarkAllReadRequest>) => {
			const requestParams: MarkAllReadRequest = {
				is_read: true,
				...params
			}
			return mutation.mutate(requestParams)
		}
	}
}

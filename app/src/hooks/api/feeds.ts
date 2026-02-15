import { createMutation, useRealtimeSWR, useStaticSWR } from '@/lib/swr-config'

import {
	type PaginatedResponse,
	type ResponseMessage,
	type UserFeedListQuery,
	type UserFeedListResponse,
	type UserFeedResponse,
	type UserFeedUpdateRequest
} from '@/types/api'
import type { QueryValue } from '@/utils/query'

import { buildQueryParams } from '@/utils/query'

export function useFeeds(params?: UserFeedListQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = `/feeds?${queryString}`

	return useRealtimeSWR<PaginatedResponse<UserFeedListResponse>>(url)
}

export function useFeed(feedId: string) {
	return useStaticSWR<UserFeedResponse>(`/feeds/${feedId}`)
}

export function useUpdateFeed(feedId: string) {
	return createMutation<UserFeedUpdateRequest, ResponseMessage>(
		`/feeds/${feedId}`,
		'PUT'
	)
}

export function useDeleteFeed(feedId: string) {
	return createMutation<void, ResponseMessage>(`/feeds/${feedId}`, 'DELETE')
}

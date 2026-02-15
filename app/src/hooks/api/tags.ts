import { apiClient } from '@/lib/api'
import { createMutation, useStaticSWR } from '@/lib/swr-config'

import {
	ListResponse,
	PaginatedResponse,
	ResponseMessage,
	TagCreateRequest,
	TagListResponse,
	TagUpdateRequest
} from '@/types/api'
import type { QueryValue } from '@/utils/query'

import { buildQueryParams } from '@/utils/query'

export interface TagsListQuery {
	limit?: number
	offset?: number
}

export function useTags(params?: TagsListQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = `/tags?${queryString}`

	return useStaticSWR<PaginatedResponse<TagListResponse>>(url)
}

export function useTag(tagId: string) {
	return useStaticSWR<TagListResponse>(`/tags/${tagId}`)
}

export async function searchTags(
	query: string,
	limit: number = 50
): Promise<TagListResponse[]> {
	const queryString = buildQueryParams({ limit, q: query } as Record<
		string,
		QueryValue
	>)

	const response = await apiClient.get<ListResponse<TagListResponse>>(
		`/search/tags?${queryString}`
	)
	return response.data.data || []
}

export function useCreateTag() {
	return createMutation<TagCreateRequest, TagListResponse>('/tags', 'POST')
}

export function useUpdateTag(tagId: string) {
	return createMutation<TagUpdateRequest, ResponseMessage>(
		`/tags/${tagId}`,
		'PUT'
	)
}

export function useDeleteTag(tagId: string) {
	return createMutation<void, ResponseMessage>(`/tags/${tagId}`, 'DELETE')
}

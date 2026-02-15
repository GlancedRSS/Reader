import { createMutation, useStaticSWR } from '@/lib/swr-config'

import {
	FolderCreateRequest,
	FolderListResponse,
	FolderResponse,
	FolderTreeResponse,
	FolderUpdateRequest,
	ResponseMessage
} from '@/types/api'
import type { QueryValue } from '@/utils/query'

import { buildQueryParams } from '@/utils/query'

export function useFolder(folderId: string, limit?: number, offset?: number) {
	const queryString = buildQueryParams({ limit, offset } as Record<
		string,
		QueryValue
	>)
	const url = `/folders/${folderId}${queryString ? `?${queryString}` : ''}`
	return useStaticSWR<FolderResponse>(url)
}

export function useFolderTree() {
	return useStaticSWR<FolderTreeResponse[]>('/folders/tree')
}

export function useCreateFolder() {
	return createMutation<FolderCreateRequest, FolderListResponse>(
		'/folders',
		'POST'
	)
}

export function useUpdateFolder(folderId: string) {
	return createMutation<FolderUpdateRequest, ResponseMessage>(
		`/folders/${folderId}`,
		'PUT'
	)
}

export function useDeleteFolder(folderId: string) {
	return createMutation<void, ResponseMessage>(`/folders/${folderId}`, 'DELETE')
}

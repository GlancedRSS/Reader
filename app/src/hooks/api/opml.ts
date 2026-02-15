import { apiClient } from '@/lib/api'
import { createMutation, useStaticSWR } from '@/lib/swr-config'

import type {
	OpmlExportRequest,
	OpmlOperationResponse,
	ResponseMessage
} from '@/types/api'

export function useOPMLStatusDetails(jobId: string) {
	return useStaticSWR<OpmlOperationResponse>(`/opml/status/${jobId}`)
}

export function useUploadAndImportOPML() {
	return {
		async mutate({
			file,
			folderId
		}: {
			file: File
			folderId?: string
		}): Promise<ResponseMessage> {
			const formData = new FormData()
			formData.append('file', file)
			if (folderId) {
				formData.append('folder_id', folderId)
			}

			const params = folderId ? `?folder_id=${folderId}` : ''
			const response = await apiClient.post<ResponseMessage>(
				`/opml/upload${params}`,
				formData,
				{
					headers: {
						'Content-Type': 'multipart/form-data'
					},
					url: `/opml/upload${params}`
				}
			)
			return response.data
		}
	}
}

export function useExportOPML() {
	return createMutation<OpmlExportRequest, ResponseMessage>(
		'/opml/export',
		'POST'
	)
}

export function useRollbackOPML() {
	return {
		async mutate(importId: string): Promise<ResponseMessage> {
			const response = await apiClient.post<ResponseMessage>(
				`/opml/${importId}/rollback`,
				{},
				{
					url: `/opml/${importId}/rollback`
				}
			)
			return response.data
		}
	}
}

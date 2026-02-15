import { OpmlType } from '@/types/opml'

export interface OpmlOperationListResponse {
	id: string
	type: OpmlType
	status: string
	filename?: string
	file_size?: number
	created_at: string
}

// GET '/api/v1/opml/status/{job_id}'
export interface OpmlOperationResponse {
	id: string
	type: OpmlType
	status: string
	filename?: string
	file_size?: number
	created_at: string
	completed_at?: string
	total_feeds: number
	imported_feeds: number
	failed_feeds: number
	duplicate_feeds: number
	failed_feeds_log: Record<string, unknown> | Array<unknown> | null
}

// POST '/api/v1/opml/upload'
export interface OpmlUploadResponse {
	import_id: string
	filename: string
	file_size: number
	message: string
}

// POST '/api/v1/opml/export'
export interface OpmlExportRequest {
	folder_id?: string
}

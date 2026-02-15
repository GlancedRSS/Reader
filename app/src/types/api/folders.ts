// GET '/api/v1/folders'
export interface FolderListResponse {
	id: string
	name: string
	parent_id?: string
	feed_count: number
	unread_count: number
	is_pinned: boolean
	depth: number
}

// POST '/api/v1/folders'
export interface FolderCreateRequest {
	name: string
	parent_id?: string
}

// GET '/api/v1/folders/{folder_id}'
export interface FolderResponse {
	id: string
	name: string
	parent_id?: string
	feed_count: number
	unread_count: number
	is_pinned: boolean
	depth: number
	data: FolderListResponse[]
	pagination: Record<string, unknown>
}

// PUT '/api/v1/folders/{folder_id}'
export interface FolderUpdateRequest {
	name?: string
	parent_id?: string
	is_pinned?: boolean
}

// GET '/api/v1/folders/tree'
export interface FolderTreeResponse {
	id?: string | null // null for virtual folders like "Uncategorized"
	name: string
	parent_id?: string | null
	feed_count: number
	unread_count: number
	is_pinned: boolean
	depth: number
	feeds: FeedInFolderResponse[]
	subfolders: FolderTreeResponse[]
}

export interface FeedInFolderResponse {
	id: string
	title: string
	unread_count: number
	website?: string | null
	is_pinned: boolean
	is_active: boolean
}

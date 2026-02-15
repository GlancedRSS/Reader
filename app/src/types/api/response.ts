export interface PaginationMetadata {
	total?: number // Optional for cursor-based pagination
	limit?: number
	offset?: number
	has_more: boolean
	next_cursor?: string
}

export interface PaginatedResponse<T> {
	data: T[]
	pagination: PaginationMetadata
}

export interface ListResponse<T> {
	data: T[]
}

export interface ResponseMessage {
	message: string
}

// POST '/api/v1/tags'
export interface TagCreateRequest {
	name: string
}

// PUT '/api/v1/tags/{tag_id}'
export interface TagUpdateRequest {
	name?: string
}

// GET '/api/v1/tags'
// GET '/api/v1/tags/{tag_id}'
export interface TagListResponse {
	id: string
	name: string
	article_count: number
}

export type DiscoveryStatus =
	| 'existing'
	| 'moved'
	| 'subscribed'
	| 'pending'
	| 'failed'

// POST '/api/v1/discovery'
export interface FeedDiscoveryRequest {
	url: string
	folder_id?: string
}

// POST '/api/v1/discovery'
export interface FeedDiscoveryResponse {
	status: DiscoveryStatus
	message: string
}

// SSE event payload types

export interface NewArticlesPayload {
	[feedId: string]: number
}

export interface OpmlImportProgressPayload {
	import_id: string
	current: number
	total: number
	percentage: number
}

export interface OpmlExportCompletePayload {
	export_id: string
	total_feeds: number
	download_url: string
	filename: string
}

export interface OpmlImportCompletePayload {
	import_id: string
	total_feeds: number
	imported_feeds: number
	failed_feeds: number
	duplicate_feeds: number
}

export interface DiscoverySubscriptionSuccessPayload {
	title: string
	action: string
	message: string
}

export interface DiscoverySubscriptionFailedPayload {
	title: string
	action: string
	message: string
}

export interface DiscoveryAlreadySubscribedPayload {
	title: string
	action: string
	message: string
}

export interface DiscoveryFolderNotFoundPayload {
	title: string
	action: string
	message: string
}

export interface FeedResumeBackfillFailedPayload {
	feed_id: string
	user_feed_id: string
	error: string
}

export interface SSEEventHandlerMap {
	new_articles?: (payload: NewArticlesPayload) => void
	opml_import_progress?: (payload: OpmlImportProgressPayload) => void
	opml_import_complete?: (payload: OpmlImportCompletePayload) => void
	opml_export_complete?: (payload: OpmlExportCompletePayload) => void
	discovery_subscription_success?: (
		payload: DiscoverySubscriptionSuccessPayload
	) => void
	discovery_subscription_failed?: (
		payload: DiscoverySubscriptionFailedPayload
	) => void
	discovery_already_subscribed?: (
		payload: DiscoveryAlreadySubscribedPayload
	) => void
	discovery_folder_not_found?: (payload: DiscoveryFolderNotFoundPayload) => void
	feed_resume_backfill_failed?: (
		payload: FeedResumeBackfillFailedPayload
	) => void
}

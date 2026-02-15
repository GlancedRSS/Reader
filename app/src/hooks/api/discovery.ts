import { createMutation } from '@/lib/swr-config'

import { FeedDiscoveryRequest, FeedDiscoveryResponse } from '@/types/api'

export function useDiscoverFeeds() {
	return createMutation<FeedDiscoveryRequest, FeedDiscoveryResponse>(
		'/discovery',
		'POST'
	)
}

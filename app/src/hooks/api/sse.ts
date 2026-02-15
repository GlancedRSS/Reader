'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import type { SSEEventHandlerMap } from '@/types/api/sse'

interface UseSSEOptions {
	enabled?: boolean
	onEvents?: SSEEventHandlerMap
	onConnect?: () => void
	onError?: () => void
}

interface SSEState {
	connected: boolean
}

const SSE_EVENT_TYPES: (keyof SSEEventHandlerMap)[] = [
	'new_articles',
	'opml_import_progress',
	'opml_import_complete',
	'opml_export_complete',
	'discovery_subscription_success',
	'discovery_subscription_failed',
	'discovery_already_subscribed',
	'discovery_folder_not_found',
	'feed_resume_backfill_failed'
]

export function useSSE({
	enabled = true,
	onEvents,
	onConnect,
	onError
}: UseSSEOptions = {}) {
	const eventSourceRef = useRef<EventSource | null>(null)
	const optionsRef = useRef({ onConnect, onError, onEvents })
	const listenersRef = useRef<Map<string, (event: MessageEvent) => void>>(
		new Map()
	)

	const [state, setState] = useState<SSEState>({
		connected: false
	})

	useEffect(() => {
		optionsRef.current = { onConnect, onError, onEvents }
	})

	const connect = useCallback(() => {
		if (eventSourceRef.current) return

		const eventSource = new EventSource('/api/sse/notifications')
		eventSourceRef.current = eventSource

		eventSource.onopen = () => {
			setState({ connected: true })
			optionsRef.current.onConnect?.()
		}

		eventSource.onerror = () => {
			setState({ connected: false })
			optionsRef.current.onError?.()
		}

		for (const eventType of SSE_EVENT_TYPES) {
			const listener = (event: MessageEvent) => {
				try {
					const data = JSON.parse(event.data)
					optionsRef.current.onEvents?.[eventType]?.(data)
				} catch {
					console.error(
						`Failed to parse SSE event "${String(eventType)}":`,
						event.data
					)
				}
			}
			eventSource.addEventListener(String(eventType), listener)
			listenersRef.current.set(String(eventType), listener)
		}
	}, [])

	const disconnect = useCallback(() => {
		if (eventSourceRef.current) {
			for (const [eventType, listener] of listenersRef.current) {
				eventSourceRef.current.removeEventListener(eventType, listener)
			}
			listenersRef.current.clear()

			eventSourceRef.current.close()
			eventSourceRef.current = null
		}
		setState({ connected: false })
	}, [])

	useEffect(() => {
		if (enabled) {
			connect()
		} else {
			disconnect()
		}

		return disconnect
	}, [enabled, connect, disconnect])

	return {
		...state,
		connect,
		disconnect
	}
}

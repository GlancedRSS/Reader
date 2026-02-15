import { headers } from 'next/headers'

function getBackendUrl(): string {
	const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2076'
	return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl
}

export async function GET() {
	const backendUrl = getBackendUrl()
	const url = `${backendUrl}/api/v1/notifications`

	const headersList = await headers()
	const cookie = headersList.get('cookie')

	const abortController = new AbortController()

	const stream = new ReadableStream({
		cancel() {
			abortController.abort()
		},

		async start(controller) {
			try {
				const response = await fetch(url, {
					headers: {
						...(cookie ? { Cookie: cookie } : {})
					},
					signal: abortController.signal
				})

				if (!response.ok) {
					controller.close()
					return
				}

				if (!response.body) {
					controller.close()
					return
				}

				const reader = response.body.getReader()

				while (true) {
					const { done, value } = await reader.read()

					if (done) {
						break
					}

					if (abortController.signal.aborted) {
						reader.releaseLock()
						break
					}

					controller.enqueue(value)
				}

				controller.close()
			} catch (error) {
				if (!(error instanceof Error && error.name === 'AbortError')) {
					console.error('SSE stream error:', error)
				}
				controller.close()
			}
		}
	})

	return new Response(stream, {
		headers: {
			'Cache-Control': 'no-cache, no-transform',
			Connection: 'keep-alive',
			'Content-Type': 'text/event-stream',
			'X-Accel-Buffering': 'no'
		}
	})
}

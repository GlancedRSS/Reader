export function isAuthError(error: unknown): boolean {
	if (!error) return false
	const err = error as { status?: number }
	return err.status === 401 || err.status === 403
}

export function isNetworkError(error: unknown): boolean {
	if (!error) return false

	const message = (error as { message?: string }).message || ''
	const networkPatterns: (string | RegExp)[] = [
		'Failed to fetch',
		'NetworkError',
		'network error',
		'fetch failed',
		'ERR_INTERNET_DISCONNECTED',
		'ERR_NETWORK',
		'timeout',
		'ECONNREFUSED',
		'ENOTFOUND'
	]

	return networkPatterns.some((pattern) => {
		if (typeof pattern === 'string') {
			return message.includes(pattern)
		}
		if (pattern instanceof RegExp) {
			return pattern.test(message)
		}
		return false
	})
}

import { getReasonPhrase } from 'http-status-codes'

export interface ParsedError {
	message: string
	statusCode?: number
}

const ERROR_PATTERNS: Array<{
	pattern: RegExp
	message: string
}> = [
	{ message: 'Connection failed', pattern: /All connection attempts failed/i },
	{
		message: 'DNS lookup failed',
		pattern: /\[Errno 8\] nodename nor servname provided/i
	},
	{
		message: 'Connection refused',
		pattern: /ConnectError|connection refused/i
	},
	{ message: 'Request timeout', pattern: /TimeoutException|request timeout/i },
	{ message: 'Too many redirects', pattern: /TooManyRedirects/i },
	{ message: 'Response decoding failed', pattern: /DecodingError/i },

	// SSL/TLS errors
	{
		message: 'SSL certificate error',
		pattern: /SSL.*CERTIFICATE_VERIFY_FAILED/i
	},
	{ message: 'SSL certificate expired', pattern: /SSL.*CERTIFICATE_EXPIRED/i },
	{ message: 'SSL hostname mismatch', pattern: /SSL.*HOSTNAME_MISMATCH/i },
	{ message: 'SSL handshake failed', pattern: /SSL.*handshake failed/i },

	// Feed format errors
	{
		message: 'Invalid feed format',
		pattern: /does not appear to be a valid RSS\/Atom feed/i
	},
	{ message: 'No feed data', pattern: /no_feed_data/i },
	{ message: 'Empty feed', pattern: /no_entries/i },
	{ message: 'Feed too large', pattern: /Feed too large/i },

	// URL validation errors
	{ message: 'Invalid URL', pattern: /Invalid URL format/i },
	{
		message: 'Invalid URL scheme',
		pattern: /Only HTTP and HTTPS URLs are supported/i
	},
	{ message: 'URL not allowed', pattern: /localhost|private IP|not allowed/i },

	// Database/constraint errors
	{
		message: 'Invalid website URL',
		pattern: /violates check constraint.*feeds_website_check/i
	},

	// System errors
	{ message: 'Service unavailable', pattern: /Service unavailable/i },
	{ message: 'Database error', pattern: /Database error|database.*error/i }
]

export function parseFeedError(error: string): ParsedError {
	// Try to extract HTTP status code first
	const statusMatch = error.match(
		/Client error '(\d{3})|Server error '(\d{3})|status (\d{3})/
	)
	const statusCode = statusMatch
		? parseInt(statusMatch[1] || statusMatch[2] || statusMatch[3] || '')
		: undefined

	if (statusCode) {
		let message: string

		// Override with more specific messages first
		if (statusCode === 404) message = 'Not found'
		else if (statusCode === 403) message = 'Forbidden'
		else if (statusCode === 410) message = 'Feed removed'
		else if (statusCode === 429) message = 'Rate limited'
		else if (statusCode === 522) message = 'Server unavailable'
		else if (statusCode === 525) message = 'SSL handshake failed'
		else {
			try {
				message = getReasonPhrase(statusCode)
			} catch {
				message = `HTTP ${statusCode}`
			}
		}

		return { message, statusCode }
	}

	// Try to match known error patterns
	for (const { pattern, message } of ERROR_PATTERNS) {
		if (pattern.test(error)) {
			return { message }
		}
	}

	const firstLine = (error || '').split('\n')[0] || ''
	const cleanedError = firstLine
		.replace(/^Error: /i, '')
		.replace(/\(.+\)$/, '') // Remove trailing parenthetical info
		.trim()

	return { message: cleanedError || 'Unknown error' }
}

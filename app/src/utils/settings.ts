import { formatDistanceToNow } from 'date-fns'

export function safeFormatDistanceToNow(
	date: Date | string | null | undefined
) {
	if (!date) return 'Unknown'

	try {
		return formatDistanceToNow(new Date(date), { addSuffix: true })
	} catch {
		return 'Unknown'
	}
}

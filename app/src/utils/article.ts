import {
	differenceInDays,
	differenceInHours,
	differenceInMinutes,
	format,
	formatDistanceToNow,
	isToday,
	isYesterday
} from 'date-fns'

export const formatTime = (
	dateString: string,
	dateFormat: 'relative' | 'absolute',
	timeFormat: '12h' | '24h',
	compact: boolean = false
): string => {
	try {
		const date = new Date(dateString)
		const now = new Date()

		if (isNaN(date.getTime())) {
			return 'just now'
		}

		const diffMinutes = differenceInMinutes(now, date)

		if (compact) {
			const diffHours = differenceInHours(now, date)
			const diffDays = differenceInDays(now, date)

			if (diffMinutes < 1) {
				return 'just now'
			} else if (diffMinutes < 60) {
				return `${diffMinutes}m ago`
			} else if (diffHours < 24) {
				return `${diffHours}h ago`
			} else if (isToday(date)) {
				return format(date, timeFormat === '24h' ? 'HH:mm' : 'h:mm a')
			} else if (isYesterday(date)) {
				return 'yesterday'
			} else if (diffDays <= 7) {
				return `${diffDays}d ago`
			}

			if (diffDays > 365) {
				return format(
					date,
					timeFormat === '24h' ? 'MMM d, yyyy HH:mm' : 'MMM d, yyyy h:mm a'
				)
			}
			return format(date, timeFormat === '24h' ? 'MMM d HH:mm' : 'MMM d h:mm a')
		}

		if (diffMinutes < 2) {
			return 'just now'
		} else if (diffMinutes < 60) {
			return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`
		}

		if (isToday(date)) {
			if (dateFormat === 'relative') {
				return formatDistanceToNow(date, { addSuffix: true })
			} else {
				const timePattern = timeFormat === '12h' ? 'h:mm a' : 'HH:mm'
				return format(date, timePattern)
			}
		} else {
			return format(date, 'MMM d, yyyy')
		}
	} catch {
		return 'just now'
	}
}

export function formatArticleDate(
	dateString: string,
	preferences?: { date_format: string; time_format: string }
): string {
	const dateFormat =
		preferences?.date_format === 'absolute' ? 'absolute' : 'relative'
	const timeFormat = preferences?.time_format === '24h' ? '24h' : '12h'
	return formatTime(dateString, dateFormat, timeFormat, true)
}

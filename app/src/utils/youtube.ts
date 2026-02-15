export function formatDuration(seconds: number | undefined): string | null {
	if (seconds === undefined || seconds === null) return null

	const hours = Math.floor(seconds / 3600)
	const minutes = Math.floor((seconds % 3600) / 60)
	const secs = seconds % 60

	if (hours > 0) {
		return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
	}
	return `${minutes}:${secs.toString().padStart(2, '0')}`
}

export function formatViewCount(views: number | undefined): string | null {
	if (views === undefined || views === null) return null

	if (views >= 1000000) {
		return `${(views / 1000000).toFixed(1)}M`
	}
	if (views >= 1000) {
		return `${(views / 1000).toFixed(0)}K`
	}
	return views.toString()
}

export function formatRating(rating: number | undefined): string | null {
	if (rating === undefined || rating === null) return null
	return `${rating.toFixed(1)} ★`
}

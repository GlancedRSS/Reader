export function getDomain(url: string): string {
	if (!url) return ''
	try {
		const urlWithProtocol = url.startsWith('http') ? url : `https://${url}`
		const urlObj = new URL(urlWithProtocol)
		return urlObj.hostname
	} catch {
		const match = url.match(/(?:https?:\/\/)?(?:www\.)?([^\/]+)/)
		return match?.[1] || ''
	}
}

export interface LogoOptions {
	retina?: boolean
	size?: number
}

export function getLogoUrl(
	website: string | null | undefined,
	options?: LogoOptions
): string | null {
	if (!website) {
		return null
	}

	const { size = 128, retina = false } = options || {}

	const domain = website.startsWith('http')
		? new URL(website).hostname
		: website

	const cleanDomain = domain.replace(/^www\./, '')

	const actualSize = retina ? size * 2 : size

	return `https://www.google.com/s2/favicons?domain=${cleanDomain}&sz=${actualSize}`
}

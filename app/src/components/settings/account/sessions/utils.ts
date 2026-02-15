export const getBrowserLogo = (browserName: string) => {
	const name = browserName.toLowerCase()
	if (name.includes('android')) return '/browsers/android.svg'
	if (name.includes('chrome')) return '/browsers/chrome.svg'
	if (name.includes('firefox')) return '/browsers/firefox.svg'
	if (name.includes('safari')) return '/browsers/safari.svg'
	if (name.includes('edge')) return '/browsers/edge.svg'
	if (name.includes('opera')) return '/browsers/opera.svg'
	return '/browsers/generic.svg'
}

export const parseUserAgent = (userAgent: string) => {
	let browser = 'Unknown'
	if (userAgent.includes('Firefox') && !userAgent.includes('Seamonkey')) {
		browser = 'Firefox'
	} else if (userAgent.includes('Edg')) {
		browser = 'Edge'
	} else if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
		browser = 'Chrome'
	} else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
		browser = 'Safari'
	} else if (userAgent.includes('Opera') || userAgent.includes('OPR')) {
		browser = 'Opera'
	}

	let os = 'Unknown'
	if (userAgent.includes('Windows NT 10.0')) os = 'Windows'
	else if (userAgent.includes('Windows NT 6.1')) os = 'Windows'
	else if (userAgent.includes('Windows')) os = 'Windows'
	else if (userAgent.includes('Mac OS X')) os = 'macOS'
	else if (userAgent.includes('Android')) os = 'Android'
	else if (userAgent.includes('iPhone')) os = 'iOS'
	else if (userAgent.includes('iPad')) os = 'iPadOS'
	else if (userAgent.includes('Linux')) os = 'Linux'

	return { browser, os }
}

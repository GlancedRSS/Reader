export type QueryValue =
	| string
	| number
	| boolean
	| undefined
	| null
	| string[]
	| number[]
	| boolean[]

export function buildQueryParams(params: Record<string, QueryValue>): string {
	const searchParams = new URLSearchParams()
	for (const [key, value] of Object.entries(params)) {
		if (value === undefined || value === null) {
			continue
		}
		if (Array.isArray(value)) {
			for (const item of value) {
				if (item !== undefined && item !== null) {
					searchParams.append(key, String(item))
				}
			}
		} else {
			searchParams.set(key, String(value))
		}
	}
	return searchParams.toString()
}

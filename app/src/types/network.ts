export interface ApiResponse<T = unknown> {
	data: T
	message?: string
	status: number
}

export class ApiError extends Error {
	status?: number | undefined
	code?: string | undefined
	detail?: string | undefined

	constructor(
		message: string,
		options?: { status?: number; code?: string; detail?: string }
	) {
		super(message)
		this.name = 'ApiError'
		this.status = options?.status
		this.code = options?.code
		this.detail = options?.detail
	}
}

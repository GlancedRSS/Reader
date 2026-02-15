import axios, {
	AxiosError,
	AxiosInstance,
	AxiosRequestConfig,
	AxiosResponse
} from 'axios'

import { API_BASE_PATH, API_BASE_URL } from '@/constants/api'

import { ApiError } from '@/types/network'
import type { ApiResponse } from '@/types/network'

interface RequestConfig extends Omit<AxiosRequestConfig, 'url'> {
	skipAuth?: boolean
	token?: string
	url: string
}

class UnifiedApiClient {
	private client: AxiosInstance

	constructor() {
		const baseURL = `${API_BASE_URL}${API_BASE_PATH}`

		this.client = axios.create({
			baseURL,
			headers: {
				'Content-Type': 'application/json'
			},
			timeout: 30000,
			withCredentials: true
		})

		this.client.interceptors.request.use(
			(config) => {
				const method = config.method?.toUpperCase()

				if (method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
					const csrfToken = this.getCsrfToken()
					if (csrfToken) {
						config.headers.set('X-CSRF-Token', csrfToken)
					}
				}

				return config
			},
			(error) => Promise.reject(error)
		)

		this.client.interceptors.response.use(
			(response) => response,
			(error: AxiosError) => Promise.reject(this.formatError(error))
		)
	}

	private getCsrfToken(): string | null {
		const cookies = document.cookie
			.split(';')
			.reduce<Record<string, string>>((acc, cookie) => {
				const [key, ...valueParts] = cookie.trim().split('=')
				if (key && valueParts.length) {
					acc[key] = valueParts.join('=')
				}
				return acc
			}, {})

		return cookies['csrf_token'] || null
	}

	private formatError(error: unknown): ApiError {
		const axiosError = error as AxiosError

		if (axiosError.response) {
			const data = axiosError.response.data as {
				code?: string
				detail?: string
				message?: string
			} | null

			const message =
				data?.detail || data?.message || `HTTP ${axiosError.response.status}`

			return new ApiError(message, {
				...(data?.code ? { code: data.code } : {}),
				...(data?.detail ? { detail: data.detail } : {}),
				status: axiosError.response.status
			})
		}

		if (axiosError.request) {
			return new ApiError('Network error - no response received', {
				code: 'NETWORK_ERROR'
			})
		}

		return new ApiError(
			(error as { message?: string }).message || 'An unknown error occurred',
			{ code: 'UNKNOWN_ERROR' }
		)
	}

	async request<T = unknown>(config: RequestConfig): Promise<ApiResponse<T>> {
		try {
			const response: AxiosResponse<T> = await this.client.request(config)
			return {
				data: response.data,
				status: response.status
			}
		} catch (error) {
			throw this.formatError(error)
		}
	}

	async get<T = unknown>(
		url: string,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		return this.request<T>({ ...config, method: 'GET', url })
	}

	async post<T = unknown>(
		url: string,
		data?: unknown,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		return this.request<T>({ ...config, data, method: 'POST', url })
	}

	async put<T = unknown>(
		url: string,
		data?: unknown,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		return this.request<T>({ ...config, data, method: 'PUT', url })
	}

	async patch<T = unknown>(
		url: string,
		data?: unknown,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		return this.request<T>({ ...config, data, method: 'PATCH', url })
	}

	async delete<T = unknown>(
		url: string,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		return this.request<T>({ ...config, method: 'DELETE', url })
	}

	async upload<T = unknown>(
		url: string,
		file: File,
		additionalData?: Record<string, string | Blob>,
		config?: RequestConfig
	): Promise<ApiResponse<T>> {
		const formData = new FormData()
		formData.append('file', file)

		if (additionalData) {
			Object.entries(additionalData).forEach(([key, value]) => {
				formData.append(key, value)
			})
		}

		return this.request<T>({
			...config,
			data: formData,
			headers: {
				'Content-Type': 'multipart/form-data'
			},
			method: 'POST',
			url
		})
	}

	async download(
		url: string,
		config?: RequestConfig,
		includeHeaders = false
	): Promise<Blob | { blob: Blob; headers: Record<string, string> }> {
		const response = await this.client.request({
			...config,
			method: 'GET',
			responseType: 'blob',
			url
		})

		if (includeHeaders) {
			return {
				blob: response.data,
				headers: response.headers as Record<string, string>
			}
		}

		return response.data
	}
}

export const apiClient = new UnifiedApiClient()

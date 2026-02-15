import useSWR, { SWRConfiguration } from 'swr'

import { apiClient } from '@/lib/api'

import type { ApiResponse } from '@/types/network'

import {
	isAuthError,
	isNetworkError as isNetworkErrorUtil
} from '@/utils/error'

const swrFetcher = async <T = unknown>(url: string): Promise<T> => {
	const response = await apiClient.get<T>(url)
	return response.data
}

export const globalSWRConfig: SWRConfiguration = {
	dedupingInterval: 2000,
	errorRetryCount: 3,
	errorRetryInterval: 5000,
	fetcher: swrFetcher,
	focusThrottleInterval: 5000,
	keepPreviousData: false,
	loadingTimeout: 5000,
	onErrorRetry: (error, _key, _config, revalidate, { retryCount }) => {
		if (isAuthError(error) || isNetworkErrorUtil(error)) {
			return
		}
		if (
			error?.status &&
			error.status >= 400 &&
			error.status < 500 &&
			error.status !== 429
		) {
			return
		}
		if (retryCount >= 3) {
			return
		}
		setTimeout(() => revalidate({ retryCount: retryCount + 1 }), 5000)
	},
	refreshWhenHidden: false,
	refreshWhenOffline: false,
	revalidateOnFocus: false,
	revalidateOnReconnect: true,
	shouldRetryOnError: true,
	suspense: false
}

export const useRealtimeSWR = <T = unknown>(
	key: string | null,
	config?: SWRConfiguration<T>
) =>
	useSWR<T>(key, swrFetcher<T>, {
		...globalSWRConfig,
		revalidateOnFocus: true,
		...config
	})

export const useStaticSWR = <T = unknown>(
	key: string | null,
	config?: SWRConfiguration<T>
) =>
	useSWR<T>(key, swrFetcher<T>, {
		...globalSWRConfig,
		revalidateOnFocus: false,
		...config
	})

export function createMutation<TRequest = unknown, TResponse = unknown>(
	url: string,
	method: 'POST' | 'PUT' | 'DELETE' = 'POST'
) {
	return {
		async mutate(data?: TRequest): Promise<TResponse> {
			let response: ApiResponse<TResponse>

			switch (method) {
				case 'POST':
					response = await apiClient.post<TResponse>(url, data)
					break
				case 'PUT':
					response = await apiClient.put<TResponse>(url, data)
					break
				case 'DELETE':
					response = await apiClient.delete<TResponse>(url)
					break
				default:
					throw new Error(`Unsupported method: ${method}`)
			}

			return response.data
		}
	}
}

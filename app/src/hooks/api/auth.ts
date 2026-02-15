import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import { useRouter } from 'next/navigation'
import { useSWRConfig } from 'swr'

import { apiClient } from '@/lib/api'
import { useStaticSWR } from '@/lib/swr-config'

import type {
	ListResponse,
	LoginRequest,
	PasswordChangeRequest,
	RegistrationRequest,
	ResponseMessage,
	SessionResponse
} from '@/types/api'

export async function register(
	data: RegistrationRequest
): Promise<ResponseMessage> {
	const response = await apiClient.post<ResponseMessage>(
		'/auth/register',
		data,
		{
			url: '/auth/register'
		}
	)
	return response.data
}

export async function login(data: LoginRequest): Promise<ResponseMessage> {
	const response = await apiClient.post<ResponseMessage>('/auth/login', data, {
		url: '/auth/login',
		withCredentials: true
	})
	return response.data
}

export async function logout(): Promise<ResponseMessage> {
	const response = await apiClient.post<ResponseMessage>(
		'/auth/logout',
		{},
		{
			url: '/auth/logout',
			withCredentials: true
		}
	)
	return response.data
}

export async function changePassword(
	data: PasswordChangeRequest
): Promise<ResponseMessage> {
	const response = await apiClient.post<ResponseMessage>(
		'/auth/change-password',
		data,
		{
			url: '/auth/change-password'
		}
	)
	return response.data
}

export async function getSessions(): Promise<SessionResponse[]> {
	const response = await apiClient.get<{ data: SessionResponse[] }>(
		'/auth/sessions',
		{
			url: '/auth/sessions'
		}
	)
	return response.data.data
}

export async function revokeSession(
	sessionId: string
): Promise<ResponseMessage> {
	const response = await apiClient.delete<ResponseMessage>(
		`/auth/sessions/${sessionId}`,
		{
			url: `/auth/sessions/${sessionId}`
		}
	)
	return response.data
}

export function useSessions() {
	return useStaticSWR<ListResponse<SessionResponse>>('/auth/sessions')
}

export async function clearLocalData() {
	localStorage.clear()
	sessionStorage.clear()

	const databases = await indexedDB.databases()
	await Promise.all(
		databases
			.map((db) => db.name)
			.filter((name): name is string => name !== undefined)
			.map((name) => indexedDB.deleteDatabase(name))
	)

	useLayoutStore.getState().reset()
	useArticlesPaginationStore.getState().reset()
	useArticlesPaginationStore.getState().resetFilters()
}

export async function performLogout() {
	await logout()
}

export function useLogout() {
	const router = useRouter()
	const { cache, mutate } = useSWRConfig()

	return async () => {
		try {
			for (const key of cache.keys()) {
				mutate(key, undefined, { revalidate: false })
			}

			await performLogout()
			await clearLocalData()
			router.push('/sign-in')
		} catch {
			throw new Error('Failed to sign out')
		}
	}
}

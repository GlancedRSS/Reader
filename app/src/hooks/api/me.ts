import { createMutation, useStaticSWR } from '@/lib/swr-config'

import {
	PreferencesResponse,
	PreferencesUpdateRequest,
	ProfileUpdateRequest,
	ResponseMessage,
	UserResponse
} from '@/types/api'

export function useMe() {
	return useStaticSWR<UserResponse>('/me')
}

export function useUpdateProfile() {
	return createMutation<ProfileUpdateRequest, UserResponse>('/me', 'PUT')
}

export function useUserPreferences() {
	return useStaticSWR<PreferencesResponse>('/me/preferences')
}

export function useUpdateUserPreferences() {
	return createMutation<PreferencesUpdateRequest, ResponseMessage>(
		'/me/preferences',
		'PUT'
	)
}

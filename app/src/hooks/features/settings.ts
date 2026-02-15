import { useTheme } from 'next-themes'
import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { DEFAULT_USER_PREFERENCES } from '@/constants/settings'

import { useUpdateUserPreferences, useUserPreferences } from '@/hooks/api'

import type { PreferencesResponse } from '@/types/api'

interface UseSettingsFormOptions {
	onSuccess?: () => void
	onError?: (error: unknown) => void
}

export function useSettingsForm(options: UseSettingsFormOptions = {}) {
	const { onSuccess, onError } = options
	const { data: preferences, isLoading } = useUserPreferences()
	const [isSaving, setIsSaving] = useState(false)
	const [localPreferences, setLocalPreferences] = useState<PreferencesResponse>(
		DEFAULT_USER_PREFERENCES
	)
	const { setTheme } = useTheme()

	const updatePreferencesMutation = useUpdateUserPreferences()
	const { mutate: swrMutate } = useSWRConfig()

	useEffect(() => {
		if (preferences) {
			setLocalPreferences((prev) => ({ ...prev, ...preferences }))
		}
	}, [preferences])

	const handleUpdatePreference = useCallback(
		<K extends keyof PreferencesResponse>(
			key: K,
			value: PreferencesResponse[K]
		) => {
			setLocalPreferences((prev) => ({ ...prev, [key]: value }))
		},
		[]
	)

	const handleSavePreferences = useCallback(async () => {
		if (isSaving) return

		setIsSaving(true)
		try {
			await updatePreferencesMutation.mutate(localPreferences)
			await swrMutate('/preferences/')

			if (localPreferences.theme) {
				setTheme(localPreferences.theme)
			}

			toast.success('Preferences saved successfully')
			onSuccess?.()
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : 'Failed to save preferences'
			toast.error(errorMessage)
			onError?.(error)
		} finally {
			setIsSaving(false)
		}
	}, [
		isSaving,
		localPreferences,
		updatePreferencesMutation,
		swrMutate,
		onSuccess,
		onError,
		setTheme
	])

	const hasPreferencesChanges =
		JSON.stringify(preferences || {}) !== JSON.stringify(localPreferences)

	const resetPreferences = useCallback(() => {
		if (preferences) {
			setLocalPreferences({ ...preferences })
		}
	}, [preferences])

	return {
		handleSavePreferences,
		handleUpdatePreference,
		hasChanges: hasPreferencesChanges,
		isLoading,
		isSaving,
		localPreferences,
		preferences,
		resetPreferences,
		setLocalPreferences
	}
}

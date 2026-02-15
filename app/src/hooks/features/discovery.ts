import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'

import { useDiscoverFeeds } from '@/hooks/api/discovery'
import { useUploadAndImportOPML } from '@/hooks/api/opml'

export type DiscoveryState =
	| 'initial'
	| 'discovering'
	| 'selecting'
	| 'subscribing'

interface UseDiscoveryFlowOptions {
	onSuccess?: () => void
	folderId?: string
}

export function useDiscoveryFlow({
	onSuccess,
	folderId
}: UseDiscoveryFlowOptions = {}) {
	const discoverMutation = useDiscoverFeeds()
	const uploadAndImportOPML = useUploadAndImportOPML()

	const [state, setState] = useState<DiscoveryState>('initial')
	const [url, setUrl] = useState('')
	const [feeds, setFeeds] = useState<string[]>([])
	const [selectedFeedUrl, setSelectedFeedUrl] = useState<string>('')
	const [isImporting, setIsImporting] = useState(false)
	const fileInputRef = useRef<HTMLInputElement>(null)

	const resetToInitial = useCallback(() => {
		setState('initial')
		setFeeds([])
		setSelectedFeedUrl('')
	}, [])

	const handleDiscoverFeeds = useCallback(async () => {
		if (!url.trim()) {
			toast.error('Please enter a URL')
			return
		}

		let normalizedUrl = url.trim()
		if (
			!normalizedUrl.startsWith('http://') &&
			!normalizedUrl.startsWith('https://')
		) {
			normalizedUrl = 'https://' + normalizedUrl
		}

		setState('discovering')

		try {
			const result = (await discoverMutation.mutate({
				url: normalizedUrl,
				...(folderId ? { folder_id: folderId } : {})
			})) as {
				status: string
				message?: string
				feeds?: string[]
			}

			if (result.status === 'subscribed') {
				onSuccess?.()
			} else if (result.status === 'existing') {
				onSuccess?.()
			} else if (result.status === 'moved') {
				onSuccess?.()
			} else if (result.status === 'pending') {
				toast.info(
					result.message ||
						"We're adding your feed. You'll get a notification when it's ready."
				)
				onSuccess?.()
			}
		} catch (err: unknown) {
			toast.error(
				err instanceof Error ? err.message : 'Failed to discover feeds'
			)
			setState('initial')
		}
	}, [url, folderId, discoverMutation, onSuccess])

	const handleSubscribe = useCallback(async () => {
		if (!selectedFeedUrl) {
			toast.error('Please select a feed')
			return
		}

		setState('subscribing')

		try {
			const result = (await discoverMutation.mutate({
				url: selectedFeedUrl,
				...(folderId ? { folder_id: folderId } : {})
			})) as {
				status: string
				message?: string
			}

			if (
				result.status === 'subscribed' ||
				result.status === 'existing' ||
				result.status === 'moved'
			) {
				onSuccess?.()
			} else if (result.status === 'pending') {
				toast.info(
					result.message ||
						"We're adding your feed. You'll get a notification when it's ready."
				)
				onSuccess?.()
			} else {
				toast.error(result.message || 'Failed to subscribe to feed')
				setState('selecting')
			}
		} catch (err) {
			toast.error(err instanceof Error ? err.message : 'Failed to subscribe')
			setState('selecting')
		}
	}, [selectedFeedUrl, folderId, discoverMutation, onSuccess])

	const handleOpmlImport = useCallback(
		async (event: React.ChangeEvent<HTMLInputElement>) => {
			const file = event.target.files?.[0]
			if (!file) return

			if (!file.name.endsWith('.opml')) {
				toast.error('Please select a valid OPML file')
				return
			}

			setIsImporting(true)
			try {
				await uploadAndImportOPML.mutate({
					file,
					...(folderId ? { folderId } : {})
				})
				toast.success('OPML import started')
				setIsImporting(false)
				setUrl('')
				onSuccess?.()
				if (fileInputRef.current) {
					fileInputRef.current.value = ''
				}
			} catch (error) {
				toast.error(
					error instanceof Error ? error.message : 'Failed to import OPML'
				)
				setIsImporting(false)
				if (fileInputRef.current) {
					fileInputRef.current.value = ''
				}
			}
		},
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[folderId, uploadAndImportOPML]
	)

	useEffect(() => {
		resetToInitial()
	}, [folderId, resetToInitial])

	return {
		feeds,
		fileInputRef,
		handleDiscoverFeeds,
		handleOpmlImport,
		handleSubscribe,
		isDiscovering: state === 'discovering',
		isImporting,
		isSubscribing: state === 'subscribing',
		resetToInitial,
		selectedFeedUrl,
		setSelectedFeedUrl,
		setUrl,
		showSelect: state === 'selecting' || state === 'subscribing',
		state,
		url
	}
}

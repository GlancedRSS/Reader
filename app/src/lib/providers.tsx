'use client'

import { DiscoveryModal } from '@/components/discovery'
import { CreateFolderModal } from '@/components/folders'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { SWRConfig, useSWRConfig } from 'swr'

import { Toaster } from '@/components/ui/sonner'

import { useSSE } from '@/hooks/api'

import { apiClient } from '@/lib/api'
import { globalSWRConfig } from '@/lib/swr-config'

const TOAST_ACTION_BUTTON_CLASS =
	'!bg-primary/85 !text-primary-foreground !shadow-lg !shadow-black/5 dark:!shadow-white/10 hover:!bg-primary/95 hover:!shadow-xl hover:!shadow-black/10 dark:hover:!shadow-white/20 active:!scale-[0.98] active:!shadow-md !border !border-white/10 dark:!border-white/5'

function ClientFallback({ children }: { children: React.ReactNode }) {
	const [isMounted, setIsMounted] = useState(false)

	useEffect(() => {
		setIsMounted(true)
	}, [])

	if (!isMounted) {
		return null
	}

	return children
}

function SSENotifications({ children }: { children: React.ReactNode }) {
	const pathname = usePathname()
	const { mutate } = useSWRConfig()
	const router = useRouter()

	const isAuthRoute = pathname?.startsWith('/sign-')
	const enabled = !isAuthRoute

	useSSE({
		enabled,
		onEvents: {
			discovery_already_subscribed: (data) => {
				toast.info(data.message)
				mutate('/folders/tree')
			},

			discovery_folder_not_found: (data) => {
				toast.warning(data.message)
			},

			discovery_subscription_failed: (data) => {
				toast.error(data.message)
			},

			discovery_subscription_success: (data) => {
				toast.success(data.message)
				mutate('/folders/tree')
			},

			feed_resume_backfill_failed: (data) => {
				toast.warning(data.error)
			},

			new_articles: (data) => {
				const articleCount = Object.values(data).reduce(
					(sum, count) => sum + count,
					0
				)
				toast.success(
					`${articleCount} new article${articleCount === 1 ? '' : 's'} available`
				)
				mutate('/folders/tree')
			},

			opml_export_complete: async (data) => {
				toast.success(
					`Exported ${data.total_feeds} feed${data.total_feeds === 1 ? '' : 's'}`
				)

				try {
					const blob = (await apiClient.download(data.download_url)) as Blob
					const filename =
						data.filename ||
						`feeds-${new Date().toISOString().split('T')[0]}.opml`

					const url = window.URL.createObjectURL(blob)
					const a = document.createElement('a')
					a.style.display = 'none'
					a.href = url
					a.download = filename
					document.body.appendChild(a)
					a.click()

					setTimeout(() => {
						document.body.removeChild(a)
						window.URL.revokeObjectURL(url)
					}, 100)
				} catch (error) {
					console.error('Failed to download OPML:', error)
				}
			},

			opml_import_complete: (data) => {
				const parts = []
				if (data.imported_feeds > 0)
					parts.push(`${data.imported_feeds} imported`)
				if (data.duplicate_feeds > 0)
					parts.push(`${data.duplicate_feeds} duplicates`)
				if (data.failed_feeds > 0) parts.push(`${data.failed_feeds} failed`)

				toast.success(parts.join(', '), {
					action: {
						label: 'View',
						onClick: () => router.push(`/imports/${data.import_id}`)
					},
					classNames: { actionButton: TOAST_ACTION_BUTTON_CLASS }
				})
				mutate('/folders/tree')
			},

			opml_import_progress: () => {}
		}
	})

	return children
}

export function Providers({ children }: { children: React.ReactNode }) {
	return (
		<SWRConfig value={globalSWRConfig}>
			<ClientFallback>
				<SSENotifications>
					<NextThemesProvider
						attribute='class'
						defaultTheme='system'
						enableSystem
					>
						{children}
						<Toaster />
						<DiscoveryModal />
						<CreateFolderModal />
					</NextThemesProvider>
				</SSENotifications>
			</ClientFallback>
		</SWRConfig>
	)
}

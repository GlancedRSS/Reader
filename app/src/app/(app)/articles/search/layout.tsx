'use client'

import { Header } from '@/components'
import { Controls } from '@/components/articles/layout'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useRouter } from 'next/navigation'

import { Button } from '@/components/ui/button'
import { Tabs } from '@/components/ui/tabs'

import { ARTICLE_TAB_CONFIG } from '@/hooks/navigation/dynamic-tab-navigation'
import useMetadata from '@/hooks/navigation/metadata'
import { useSplitLayout } from '@/hooks/ui/layout'

export default function SearchLayout({
	children
}: {
	children: React.ReactNode
}) {
	useMetadata('Search Results | Glanced Reader')
	const router = useRouter()
	const { shouldShowSplitLayout } = useSplitLayout()

	const { is_read, setIsRead, resetFilters } = useArticlesPaginationStore()

	const handleClearFilters = () => {
		resetFilters()
		router.push('/articles')
	}

	const handleTabChange = (tabId: string) => {
		setIsRead(tabId as 'all' | 'read' | 'unread')
	}

	return (
		<div
			className={`max-w-[1440px] mx-auto ${shouldShowSplitLayout ? '' : 'md:px-4'}`}
		>
			<div className='flex'>
				<Header
					className='flex-1'
					feed={undefined}
					title='Search Results'
					website={undefined}
				/>
				<div className='p-4'>
					<Button
						onClick={handleClearFilters}
						size='sm'
						variant='ghost'
					>
						Clear
					</Button>
				</div>
			</div>
			<div className='px-4 pb-4 flex items-center justify-between gap-4'>
				<Tabs
					onChange={handleTabChange}
					options={ARTICLE_TAB_CONFIG}
					value={is_read}
				/>
				<Controls />
			</div>

			<div>{children}</div>
		</div>
	)
}

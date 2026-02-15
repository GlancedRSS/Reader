'use client'

import { Header } from '@/components'
import { Controls } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

import { Tabs } from '@/components/ui/tabs'

import { useTag, useUserPreferences } from '@/hooks/api'
import { useDynamicTabNavigation } from '@/hooks/navigation/dynamic-tab-navigation'
import useMetadata from '@/hooks/navigation/metadata'
import { useSplitLayout } from '@/hooks/ui/layout'

export default function ArticlesLayout({
	children
}: {
	children: React.ReactNode
}) {
	const params = useParams()

	const { data: preferences } = useUserPreferences()
	const { data: tagDetails } = useTag(params?.slug as string)
	const { shouldShowSplitLayout } = useSplitLayout()

	useMetadata(`${tagDetails?.name || 'Articles'} | Glanced Reader`)

	const {
		animationState,
		currentPath,
		currentSection,
		dynamicTabs,
		handleTabChange,
		setAnimationState
	} = useDynamicTabNavigation(`/tags/${params.slug}`)

	if (!preferences) {
		return null
	}

	return (
		<div
			className={`max-w-[1440px] mx-auto ${shouldShowSplitLayout ? '' : 'md:px-4'}`}
		>
			<Header
				tag={tagDetails}
				title={tagDetails?.name || 'Articles'}
				type='tag'
			/>
			<div className='px-4 pb-4'>
				<div className='flex items-center justify-between'>
					<Tabs
						animateContent={true}
						currentPath={currentPath}
						gap={2}
						onAnimationChange={setAnimationState}
						onChange={handleTabChange}
						options={dynamicTabs}
						tabSections={dynamicTabs}
						value={currentSection}
					/>

					<Controls />
				</div>
			</div>

			<div
				className={animationState.animationClass}
				key={animationState.key}
			>
				{children}
			</div>
		</div>
	)
}

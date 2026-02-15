'use client'

import { Header } from '@/components'
import { Controls } from '@/components/articles/layout'

import { Tabs } from '@/components/ui/tabs'

import { useUserPreferences } from '@/hooks/api'
import { useDynamicTabNavigation } from '@/hooks/navigation/dynamic-tab-navigation'
import useMetadata from '@/hooks/navigation/metadata'
import { useSplitLayout } from '@/hooks/ui/layout'

export default function ArticlesLayout({
	children
}: {
	children: React.ReactNode
}) {
	useMetadata('Articles | Glanced Reader')

	const { data: preferences } = useUserPreferences()
	const { shouldShowSplitLayout } = useSplitLayout()

	const {
		animationState,
		currentPath,
		currentSection,
		dynamicTabs,
		handleTabChange,
		setAnimationState
	} = useDynamicTabNavigation('/articles')

	if (!preferences) {
		return null
	}

	return (
		<div
			className={`max-w-[1440px] mx-auto ${shouldShowSplitLayout ? '' : 'md:px-4'}`}
		>
			<Header title='Articles' />
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

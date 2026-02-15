'use client'

import { Header } from '@/components'
import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'

import { Tabs } from '@/components/ui/tabs'

import { SETTINGS_TABS } from '@/constants/settings'

import type { SettingsTabs } from '@/types/settings'

export default function SettingsLayout({
	children
}: {
	children: React.ReactNode
}) {
	const pathname = usePathname()
	const router = useRouter()

	const [animationState, setAnimationState] = useState({
		animationClass: '',
		key: 0
	})

	const currentSection =
		(pathname.split('/').pop() as SettingsTabs) || 'account'

	return (
		<div className='max-w-xl mx-auto md:px-4'>
			<Header title='Settings' />
			<div className='px-4 pb-4'>
				<Tabs
					animateContent={true}
					currentPath={pathname}
					gap={2}
					onAnimationChange={setAnimationState}
					onChange={(sectionId) => {
						const section = SETTINGS_TABS.find((s) => s.id === sectionId)
						if (section) {
							router.push(section.route)
						}
					}}
					options={SETTINGS_TABS}
					tabSections={SETTINGS_TABS}
					value={currentSection}
				/>
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

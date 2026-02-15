'use client'

import { FocusLayout } from '@/components/layout/focus'
import { MobileBottomNav } from '@/components/layout/navbar'
import {
	CompactSidebar,
	DesktopSidebar,
	ResponsiveSidebar
} from '@/components/layout/sidebar/variants'
import { SplitLayout } from '@/components/layout/split'
import { CommandPalette } from '@/components/search'
import React, { useState } from 'react'

import {
	useArticleListCleanup,
	useKeyboardShortcuts,
	useLayoutState,
	useSplitLayout
} from '@/hooks/ui/layout'

interface UnifiedLayoutProps {
	children: React.ReactNode
}

export function UnifiedLayout({ children }: UnifiedLayoutProps) {
	const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

	const layoutState = useLayoutState()
	const { shouldShowSplitLayout, sidebarBreakpoints } = useSplitLayout()
	useKeyboardShortcuts(setCommandPaletteOpen)
	useArticleListCleanup()

	return (
		<>
			<div className='h-dvh flex flex-col bg-background w-full max-md:h-[calc(100dvh-3.5rem)]'>
				<div className='flex-1 flex overflow-hidden relative'>
					<div className={sidebarBreakpoints.desktop}>
						<DesktopSidebar />
					</div>

					<div className={`max-md:hidden ${sidebarBreakpoints.compact}`}>
						<CompactSidebar />
					</div>

					<div className={`max-md:hidden ${sidebarBreakpoints.compact}`}>
						<ResponsiveSidebar
							isOpen={layoutState.sidebarOverlay}
							onClose={layoutState.closeTabletSidebar}
							variant='tablet'
						/>
					</div>

					<div className='md:hidden'>
						<ResponsiveSidebar
							isOpen={layoutState.sidebarOverlay}
							onClose={layoutState.closeTabletSidebar}
							variant='mobile'
						/>
					</div>

					<main
						className={`flex-1 overflow-hidden ${sidebarBreakpoints.mainMargin}`}
					>
						{shouldShowSplitLayout ? (
							<SplitLayout>{children}</SplitLayout>
						) : (
							<FocusLayout>{children}</FocusLayout>
						)}
					</main>
				</div>
			</div>

			<div className='md:hidden'>
				<MobileBottomNav />
			</div>

			<CommandPalette
				isOpen={commandPaletteOpen}
				onClose={() => setCommandPaletteOpen(false)}
			/>
		</>
	)
}

import { useCallback } from 'react'

import { useLayoutState } from '@/hooks/ui/layout/layout-state'

export const useSidebarToggle = () => {
	const { sidebarOverlay, toggleTabletSidebar, closeTabletSidebar } =
		useLayoutState()

	const toggleSidebar = useCallback(() => {
		toggleTabletSidebar()
	}, [toggleTabletSidebar])

	const closeSidebar = useCallback(() => {
		closeTabletSidebar()
	}, [closeTabletSidebar])

	const openSidebar = useCallback(() => {
		if (!sidebarOverlay) {
			toggleTabletSidebar()
		}
	}, [sidebarOverlay, toggleTabletSidebar])

	const isSidebarOpen = sidebarOverlay

	return {
		closeSidebar,
		isSidebarOpen,
		openSidebar,
		toggleSidebar
	}
}

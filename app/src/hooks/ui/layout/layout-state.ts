import { useLayoutStore } from '@/stores/layout'

export const useLayoutState = () => {
	const {
		sidebarOverlay,
		setSidebarOverlay,
		toolbarOverlay,
		setToolbarOverlay
	} = useLayoutStore()

	const toggleTabletSidebar = () => {
		setSidebarOverlay(!sidebarOverlay)
		if (!sidebarOverlay) {
			setToolbarOverlay(false)
		}
	}

	const closeTabletSidebar = () => {
		setSidebarOverlay(false)
	}

	return {
		closeTabletSidebar,
		setSidebarOverlay,
		setToolbarOverlay,
		sidebarOverlay,
		toggleTabletSidebar,
		toolbarOverlay
	}
}

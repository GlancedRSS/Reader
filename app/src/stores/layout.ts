import { create } from 'zustand'

interface LayoutState {
	sidebarOverlay: boolean
	toolbarOverlay: boolean
	selectedArticleId: string | null
	discoveryModalOpen: boolean
	folderModalOpen: boolean
	defaultParentFolderId: string | undefined
	setSidebarOverlay: (overlay: boolean) => void
	setToolbarOverlay: (overlay: boolean) => void
	closeTabletSidebar: () => void
	setSelectedArticle: (id: string | null) => void
	openDiscoveryModal: () => void
	closeDiscoveryModal: () => void
	openFolderModal: (defaultParentId?: string) => void
	closeFolderModal: () => void
	reset: () => void
}

export const useLayoutStore = create<LayoutState>((set) => ({
	closeDiscoveryModal: () => set({ discoveryModalOpen: false }),
	closeFolderModal: () =>
		set({ defaultParentFolderId: undefined, folderModalOpen: false }),
	closeTabletSidebar: () => set({ sidebarOverlay: false }),
	defaultParentFolderId: undefined,
	discoveryModalOpen: false,
	folderModalOpen: false,
	openDiscoveryModal: () => set({ discoveryModalOpen: true }),
	openFolderModal: (defaultParentId) =>
		set({ defaultParentFolderId: defaultParentId, folderModalOpen: true }),
	reset: () =>
		set({
			defaultParentFolderId: undefined,
			discoveryModalOpen: false,
			folderModalOpen: false,
			selectedArticleId: null,
			sidebarOverlay: false,
			toolbarOverlay: false
		}),
	selectedArticleId: null,
	setSelectedArticle: (id) => set({ selectedArticleId: id }),
	setSidebarOverlay: (sidebarOverlay) => set({ sidebarOverlay }),
	setToolbarOverlay: (toolbarOverlay) => set({ toolbarOverlay }),
	sidebarOverlay: false,
	toolbarOverlay: false
}))

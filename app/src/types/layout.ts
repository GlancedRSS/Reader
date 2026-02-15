export interface Command {
	href: string
	name: string
	type: 'feed' | 'nav' | 'action'
	priority: 'high' | 'low'
}

export interface NavigationItem {
	href: string
	icon: React.ComponentType<{ className?: string }>
	icon_active: React.ComponentType<{ className?: string }>
	name: string
}

export interface CommandPaletteProps {
	isOpen: boolean
	onClose: () => void
}

export interface TabSection {
	id: string
	label: string
	route: string
}

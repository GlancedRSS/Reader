import Sidebar from '@/components/layout/sidebar'

import { SIDEBAR_WIDTH, SIDEBAR_WIDTH_CLASS, Z_INDEX } from '@/constants/layout'

export const DesktopSidebar = () => {
	return (
		<div
			className={`fixed left-0 top-0 bottom-0 ${SIDEBAR_WIDTH_CLASS} bg-background border-r border-border/40 flex flex-col`}
			style={{
				width: SIDEBAR_WIDTH,
				zIndex: Z_INDEX.sidebar
			}}
		>
			<Sidebar />
		</div>
	)
}

'use client'

import { UnifiedLayout } from '@/components/layout'

interface LayoutProps {
	children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
	return <UnifiedLayout>{children}</UnifiedLayout>
}

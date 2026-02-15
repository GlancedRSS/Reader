'use client'

import { useTheme } from 'next-themes'
import { Toaster as Sonner, ToasterProps } from 'sonner'

const Toaster = ({ ...props }: ToasterProps) => {
	const { resolvedTheme } = useTheme()
	const theme =
		resolvedTheme === 'dark' ||
		resolvedTheme === 'light' ||
		resolvedTheme === 'system'
			? resolvedTheme
			: 'system'

	return (
		<Sonner
			className='toaster group'
			theme={theme}
			toastOptions={{
				style: {
					backdropFilter: 'blur(8px)',
					backgroundImage:
						'radial-gradient(ellipse 60% 2px at 50% 0%, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 50%, transparent 80%)',
					backgroundPosition: 'top center',
					backgroundRepeat: 'no-repeat',
					border: '1px solid hsl(var(--border) / 0.5)',
					borderRadius: '12px',
					bottom: '48px'
				}
			}}
			{...props}
		/>
	)
}

export { Toaster }

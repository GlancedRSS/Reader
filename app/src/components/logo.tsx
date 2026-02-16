'use client'

import { useTheme } from 'next-themes'

interface LogoProps {
	size?: 'small' | 'large'
	variant?: 'icon' | 'logo' | 'wordmark'
}

export function Logo(props: LogoProps) {
	const { size = 'default', variant = 'logo' } = props
	const { resolvedTheme } = useTheme()

	const getSize = () => {
		switch (size) {
			case 'small':
				return 'h-8 w-auto'
			case 'large':
				return 'h-12 w-auto'
			default:
				return 'h-10 w-auto'
		}
	}

	const src = `/assets/${variant}-${resolvedTheme === 'dark' ? 'dark' : 'light'}.svg`

	return (
		// eslint-disable-next-line @next/next/no-img-element
		<img
			alt='Glanced'
			className={`${getSize()} rounded-bl-xl overflow-hidden`}
			src={src}
		/>
	)
}

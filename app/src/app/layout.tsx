import {
	Atkinson_Hyperlegible,
	Atkinson_Hyperlegible_Mono,
	Inter,
	Playfair_Display
} from 'next/font/google'

import { Providers } from '@/lib/providers'

import '@/styles/globals.css'

const inter = Inter({
	display: 'swap',
	subsets: ['latin'],
	variable: '--font-inter',
	weight: ['400', '500', '600', '700']
})

const playfairDisplay = Playfair_Display({
	display: 'swap',
	subsets: ['latin'],
	variable: '--font-playfair-display',
	weight: ['400', '700']
})

const atkinsonHyperlegible = Atkinson_Hyperlegible({
	display: 'swap',
	subsets: ['latin'],
	variable: '--font-atkinson-hyperlegible',
	weight: ['400', '700']
})

const atkinsonHyperlegibleMono = Atkinson_Hyperlegible_Mono({
	display: 'swap',
	subsets: ['latin'],
	variable: '--font-atkinson-hyperlegible-mono',
	weight: ['400', '700']
})

export const metadata = {
	robots: {
		follow: false,
		index: false
	}
}

export const viewport = {
	initialScale: 1,
	themeColor: [
		{ color: '#ffffff', media: '(prefers-color-scheme: light)' },
		{ color: '#000000', media: '(prefers-color-scheme: dark)' }
	],
	viewportFit: 'cover',
	width: 'device-width'
}

export default function RootLayout({
	children
}: {
	children: React.ReactNode
}) {
	return (
		<html
			className={`${inter.className} ${playfairDisplay.variable} ${atkinsonHyperlegible.variable} ${atkinsonHyperlegibleMono.variable}`}
			lang='en'
			suppressHydrationWarning
		>
			<head>
				<link
					href='/assets/favicon.png'
					rel='icon'
					type='image/png'
				/>
			</head>
			<body>
				<Providers>{children}</Providers>
			</body>
		</html>
	)
}

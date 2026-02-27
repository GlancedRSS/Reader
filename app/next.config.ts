import type { NextConfig } from 'next'
import packageJson from './package.json'

const nextConfig: NextConfig = {
	compress: true,
	env: {
		APP_VERSION: packageJson.version,
	},

	experimental: {
		optimizePackageImports: ['react-icons']
	},

	async headers() {
		return [
			{
				headers: [
					{
						key: 'X-Frame-Options',
						value: 'DENY'
					},
					{
						key: 'X-Content-Type-Options',
						value: 'nosniff'
					},
					{
						key: 'Referrer-Policy',
						value: 'origin-when-cross-origin'
					}
				],
				source: '/(.*)'
			}
		]
	},

	images: {
		dangerouslyAllowSVG: false,
		localPatterns: [
			{
				pathname: '/api/image-proxy/**'
			},
      {
				pathname: '/assets/icons/**'
			},
		],
		remotePatterns: [
			{
				hostname: 'www.google.com',
				protocol: 'https'
			}
		]
	},

	output: 'standalone',
	reactStrictMode: true,

	async rewrites() {
		const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2076'
		return [
			{
				destination: `${apiUrl}/api/:path*`,
				source: '/api/:path*'
			}
		]
	},

	turbopack: {
		rules: {
			'*.svg': {
				as: '*.js',
				loaders: ['@svgr/webpack']
			}
		}
	},
}

export default nextConfig

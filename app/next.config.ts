import type { NextConfig } from 'next'
import packageJson from './package.json'

const nextConfig: NextConfig = {
	env: {
		APP_VERSION: packageJson.version,
	},
	compress: true,

	experimental: {
		optimizePackageImports: ['@radix-ui/react-icons', 'react-icons']
	},

	async headers() {
		return [
			{
				headers: [
					{
						key: 'X-DNS-Prefetch-Control',
						value: 'on'
					},
					{
						key: 'X-XSS-Protection',
						value: '1; mode=block'
					},
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
			}
		],
		remotePatterns: [
			{
				hostname: 'img.logo.dev',
				protocol: 'https'
			},
			{
				hostname: 'www.google.com',
				protocol: 'https'
			}
		]
	},

	output: 'standalone',

	poweredByHeader: false,

	reactStrictMode: true,

	async redirects() {
		return []
	},

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

	webpack: (config, { dev, isServer }) => {
		if (!dev && !isServer && process.env.ANALYZE === 'true') {
			const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
			config.plugins.push(
				new BundleAnalyzerPlugin({
					analyzerMode: 'static',
					openAnalyzer: false
				})
			)
		}

		if (!dev && !isServer) {
			config.optimization = {
				...config.optimization,
				splitChunks: {
					cacheGroups: {
						common: {
							chunks: 'all',
							enforce: true,
							minChunks: 2,
							name: 'common'
						},
						vendor: {
							chunks: 'all',
							name: 'vendors',
							test: /[\\/]node_modules[\\/]/
						}
					},
					chunks: 'all'
				}
			}
		}

		return config
	}
}

export default nextConfig

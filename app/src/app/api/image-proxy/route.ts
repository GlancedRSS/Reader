import { NextResponse } from 'next/server'

const USER_AGENT = `Glanced-Reader/${process.env.APP_VERSION || '0.0.0'} (+https://github.com/glancedrss/reader)`

export async function GET(request: Request) {
	const { searchParams } = new URL(request.url)
	const imageUrl = searchParams.get('url')

	if (!imageUrl) {
		return NextResponse.json(
			{ error: 'Missing url parameter' },
			{ status: 400 }
		)
	}

	try {
		const response = await fetch(imageUrl, {
			headers: {
				'User-Agent': USER_AGENT
			}
		})

		if (!response.ok) {
			return NextResponse.json(
				{ error: `Failed to fetch image: ${response.statusText}` },
				{ status: response.status }
			)
		}

		const blob = await response.blob()
		const contentType = response.headers.get('Content-Type')

		return new NextResponse(blob, {
			headers: {
				'CDN-Cache-Control': 'public, max-age=31536000, immutable',
				'Content-Type': contentType || 'image/jpeg'
			},
			status: 200
		})
	} catch (err) {
		console.error('Image proxy error:', imageUrl, err)
		return NextResponse.json(
			{ error: 'Failed to fetch image' },
			{ status: 500 }
		)
	}
}

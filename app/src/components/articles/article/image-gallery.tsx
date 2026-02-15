'use client'

import Lightbox from 'yet-another-react-lightbox'

import 'yet-another-react-lightbox/styles.css'

import { Thumbnails, Zoom } from 'yet-another-react-lightbox/plugins'

import 'yet-another-react-lightbox/plugins/thumbnails.css'

export interface GalleryImage {
	src: string
	alt?: string
}

interface ImageGalleryProps {
	images: GalleryImage[]
	initialIndex?: number
	open: boolean
	onOpenChange: (open: boolean) => void
}

function extractImagesFromHtml(
	html: string,
	featuredImage?: string
): GalleryImage[] {
	const images: GalleryImage[] = []
	const imgRegex = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi
	let match

	while ((match = imgRegex.exec(html)) !== null) {
		const src = match[1]
		if (src) {
			images.push({
				alt: '',
				src
			})
		}
	}

	// Add featured image at the beginning if it exists and isn't already in the content
	if (
		featuredImage &&
		!images.some((img) =>
			img.src.includes(featuredImage.split('?', 1)[0] ?? '')
		)
	) {
		images.unshift({
			alt: 'Featured image',
			src: featuredImage
		})
	}

	return images
}

export function ImageGallery({
	images,
	initialIndex = 0,
	open,
	onOpenChange
}: ImageGalleryProps) {
	// Convert GalleryImage to LightboxSlide format
	const slides = images.map((img) => ({
		alt: img.alt ?? '',
		src: `/api/image-proxy?url=${encodeURIComponent(img.src)}`
	}))

	return (
		<Lightbox
			close={() => onOpenChange(false)}
			index={initialIndex}
			open={open}
			plugins={[Thumbnails, Zoom]}
			slides={slides}
			thumbnails={{
				border: 0,
				borderRadius: 8,
				gap: 8,
				height: 80,
				padding: 0,
				width: 80
			}}
			zoom={{
				maxZoomPixelRatio: 3,
				scrollToZoom: true,
				zoomInMultiplier: 2
			}}
		/>
	)
}

export { extractImagesFromHtml }

'use client'

import parse, { domToReact } from 'html-react-parser'
import Image from 'next/image'

import {
	Table,
	TableBody,
	TableCaption,
	TableCell,
	TableHead,
	TableHeader,
	TableRow
} from '@/components/ui/table'

import type {
	DOMNode,
	Element,
	HTMLReactParserOptions
} from 'html-react-parser'

import { cn } from '@/utils'

interface HtmlRendererProps {
	html: string
	className?: string
	onImageClick?: (src: string) => void
}

function CodeBlock({
	className,
	children
}: React.HTMLAttributes<HTMLPreElement>) {
	return (
		<pre
			className={cn(
				'my-4 overflow-x-auto rounded-lg bg-muted p-4 text-sm',
				className
			)}
		>
			{children}
		</pre>
	)
}

function createParserOptions(
	onImageClick?: (src: string) => void
): HTMLReactParserOptions {
	return {
		replace: (domNode: DOMNode) => {
			if (domNode.type !== 'tag') {
				return
			}

			const element = domNode as Element

			if (element.name === 'img') {
				const src = element.attribs.src
				const alt = element.attribs.alt || ''
				const width = element.attribs.width
				const height = element.attribs.height

				if (!src) return null

				const imgWidth = width ? parseInt(width) : 896
				const imgHeight = height ? parseInt(height) : 504

				return (
					<Image
						alt={alt}
						className={cn(
							'my-4 rounded-lg shadow-sm',
							onImageClick &&
								'cursor-pointer hover:opacity-80 transition-opacity'
						)}
						height={imgHeight}
						onClick={onImageClick ? () => onImageClick(src) : undefined}
						sizes='(max-width: 768px) 100vw, 896px'
						src={`/api/image-proxy?url=${encodeURIComponent(src)}`}
						style={{ height: 'auto', width: '100%' }}
						width={imgWidth}
					/>
				)
			}

			if (element.name === 'pre') {
				const children = domNode.children || []
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <CodeBlock>{domToReact(children as any, {})}</CodeBlock>
			}

			if (element.name === 'iframe') {
				const src = element.attribs.src
				const title = element.attribs.title || 'Embedded content'

				if (!src) return null

				return (
					<iframe
						allowFullScreen
						className={element.attribs.class || 'h-full w-full border-0'}
						src={src}
						title={title}
					/>
				)
			}

			if (element.name === 'table') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <Table>{domToReact(domNode as any, {})}</Table>
			}

			if (element.name === 'thead') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableHeader>{domToReact(domNode as any, {})}</TableHeader>
			}

			if (element.name === 'tbody') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableBody>{domToReact(domNode as any, {})}</TableBody>
			}

			if (element.name === 'tr') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableRow>{domToReact(domNode as any, {})}</TableRow>
			}

			if (element.name === 'th') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableHead>{domToReact(domNode as any, {})}</TableHead>
			}

			if (element.name === 'td') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableCell>{domToReact(domNode as any, {})}</TableCell>
			}

			if (element.name === 'caption') {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				return <TableCaption>{domToReact(domNode as any, {})}</TableCaption>
			}

			return
		}
	}
}

export default function HtmlRenderer({
	html,
	className,
	onImageClick
}: HtmlRendererProps) {
	if (!html) return null

	const parserOptions = createParserOptions(onImageClick)
	const parsedContent = parse(html, parserOptions)

	return <div className={className}>{parsedContent}</div>
}

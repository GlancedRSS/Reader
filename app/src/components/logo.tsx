interface LogoProps {
	size?: 'small' | 'large'
	variant?: 'icon' | 'logo' | 'wordmark'
}

export function Logo(props: LogoProps) {
	const { size = 'default', variant = 'logo' } = props

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

	const src = `/${variant}`

	return (
		<picture className='rounded-bl-2xl overflow-hidden'>
			<source
				media='(prefers-color-scheme: dark)'
				srcSet={`/assets/${src}-dark.svg`}
			/>
			<img
				alt='Glanced'
				className={getSize()}
				src={`/assets/${src}-light.svg`}
			/>
		</picture>
	)
}

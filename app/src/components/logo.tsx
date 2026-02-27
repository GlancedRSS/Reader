import Image from 'next/image'

type Size = 'small' | 'large' | 'default'

interface LogoProps {
	size?: Size
	variant?: 'icon' | 'logo' | 'wordmark'
}

const generateIcon = (size: Size) => {
	switch (size) {
		case 'small':
			return (
				<>
					<Image
						alt='Glanced'
						className='h-8 w-auto dark:hidden'
						height={32}
						src='/assets/icons/light.png'
						width={32}
					/>
					<Image
						alt='Glanced'
						className='h-8 w-auto hidden dark:block'
						height={32}
						src='/assets/icons/dark.png'
						width={32}
					/>
				</>
			)
		case 'large':
			return (
				<>
					<Image
						alt='Glanced'
						className='h-12 w-auto dark:hidden'
						height={48}
						src='/assets/icons/light.png'
						width={48}
					/>
					<Image
						alt='Glanced'
						className='h-12 w-auto hidden dark:block'
						height={48}
						src='/assets/icons/dark.png'
						width={48}
					/>
				</>
			)
		default:
			return (
				<>
					<Image
						alt='Glanced'
						className='h-10 w-auto dark:hidden'
						height={40}
						src='/assets/icons/light.png'
						width={40}
					/>
					<Image
						alt='Glanced'
						className='h-10 w-auto hidden dark:block'
						height={40}
						src='/assets/icons/dark.png'
						width={40}
					/>
				</>
			)
	}
}

const generateWordmark = (size: Size) => {
	switch (size) {
		case 'small':
			return (
				<div className='text-3xl leading-8 font-branding font-semibold tracking-tight'>
					Glanced
				</div>
			)
		case 'large':
			return (
				<div className='text-5xl leading-12 font-branding font-semibold tracking-tight'>
					Glanced
				</div>
			)
		default:
			return (
				<div className='text-4xl leading-10 font-branding font-semibold tracking-tight'>
					Glanced
				</div>
			)
	}
}

const generateLogo = (size: Size) => (
	<div className='flex items-center gap-1'>
		{generateIcon(size)}
		{generateWordmark(size)}
	</div>
)

export function Logo(props: LogoProps) {
	const { size = 'default', variant = 'logo' } = props

	switch (variant) {
		case 'icon':
			return generateIcon(size)
		case 'wordmark':
			return generateWordmark(size)
		default:
			return generateLogo(size)
	}
}

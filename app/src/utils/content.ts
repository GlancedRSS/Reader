export function mapFontSizeToTailwind(
	fontSize?: 'xs' | 's' | 'm' | 'l' | 'xl'
): string {
	switch (fontSize) {
		case 'xs':
			return 'text-sm'
		case 's':
			return 'text-base'
		case 'm':
			return 'text-lg'
		case 'l':
			return 'text-xl'
		case 'xl':
			return 'text-2xl'
		default:
			return 'text-base'
	}
}

export function mapLineHeightToTailwind(
	lineHeight?: 'compact' | 'normal' | 'comfortable'
): string {
	switch (lineHeight) {
		case 'compact':
			return 'leading-tight'
		case 'normal':
			return 'leading-normal'
		case 'comfortable':
			return 'leading-relaxed'
		default:
			return 'leading-normal'
	}
}

import { Button } from '@/components/ui/button'
import { Loader } from '@/components/ui/loader'

interface AuthSubmitButtonProps {
	text: string
	loadingText: string
	isLoading: boolean
	disabled: boolean
}

export function AuthSubmitButton({
	text,
	loadingText,
	isLoading,
	disabled
}: AuthSubmitButtonProps) {
	return (
		<Button
			aria-busy={isLoading}
			className='w-full flex items-center justify-center gap-2'
			disabled={disabled || isLoading}
			type='submit'
		>
			{isLoading ? <Loader /> : null}
			<span>{isLoading ? loadingText : text}</span>
		</Button>
	)
}

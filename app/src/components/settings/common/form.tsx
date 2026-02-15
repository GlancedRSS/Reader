import { ReactNode } from 'react'

import { Button } from '@/components/ui/button'

interface FormProps {
	isSaving?: boolean
	hasChanges?: boolean
	onSave?: () => void
	children: ReactNode
	disabled?: boolean
	saveText?: string
	savingText?: string
}

export function Form({
	isSaving = false,
	hasChanges = false,
	onSave,
	children,
	disabled = false,
	saveText = 'Save',
	savingText = 'Saving...'
}: FormProps) {
	return (
		<>
			{children}
			<div className='pt-2 flex justify-end'>
				<Button
					disabled={disabled || isSaving || !hasChanges}
					onClick={onSave}
				>
					{isSaving ? savingText : saveText}
				</Button>
			</div>
		</>
	)
}

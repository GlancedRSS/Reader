import { NameChangeModal } from '@/components/settings/account/name/modal'
import { useState } from 'react'

import { Button } from '@/components/ui/button'

export function NameChange({
	isLoading = false
}: {
	isLoading?: boolean | undefined
}) {
	const [isNameModalOpen, setIsNameModalOpen] = useState(false)

	const handleChangeName = () => {
		setIsNameModalOpen(true)
	}

	return (
		<div className='space-y-4'>
			<div className='flex items-center justify-between'>
				<div>
					<div className='text-sm font-medium'>Name</div>
					<div className='text-sm text-muted-foreground/80'>
						Shown on your profile
					</div>
				</div>
				<div className='flex items-center gap-4'>
					<Button
						disabled={isLoading}
						onClick={handleChangeName}
						size='sm'
						variant='ghost'
					>
						Edit
					</Button>
				</div>
			</div>

			<NameChangeModal
				isOpen={isNameModalOpen}
				onOpenChange={setIsNameModalOpen}
			/>
		</div>
	)
}

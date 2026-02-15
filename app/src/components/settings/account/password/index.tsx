import { PasswordChangeModal } from '@/components/settings/account/password/modal'
import { useState } from 'react'

import { Button } from '@/components/ui/button'

export function PasswordChange() {
	const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)

	const handleChangePassword = () => {
		setIsPasswordModalOpen(true)
	}

	return (
		<div className='space-y-4'>
			<div className='flex items-center justify-between'>
				<div>
					<div className='text-sm font-medium'>Password</div>
					<div className='text-sm text-muted-foreground/80'>
						Keep your account secure
					</div>
				</div>
				<div className='flex items-center gap-4'>
					<Button
						onClick={handleChangePassword}
						size='sm'
						variant='ghost'
					>
						Edit
					</Button>
				</div>
			</div>

			<PasswordChangeModal
				isOpen={isPasswordModalOpen}
				onOpenChange={setIsPasswordModalOpen}
			/>
		</div>
	)
}

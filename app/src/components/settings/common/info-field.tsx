import { useMe } from '@/hooks/api/me'

import { safeFormatDistanceToNow } from '@/utils/settings'

interface InfoFieldProps {
	label: string
	description: string
	field: 'created_at' | 'last_login'
}

export function InfoField({ label, description, field }: InfoFieldProps) {
	const { data: user } = useMe()

	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>{label}</div>
				<div className='text-sm text-muted-foreground/80'>{description}</div>
			</div>
			<span className='text-sm text-muted-foreground'>
				{safeFormatDistanceToNow(user?.[field])}
			</span>
		</div>
	)
}

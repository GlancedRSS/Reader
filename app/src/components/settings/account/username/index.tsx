import { useMe } from '@/hooks/api/me'

export function Username({
	isLoading = false
}: {
	isLoading?: boolean | undefined
}) {
	const { data: user } = useMe()

	return (
		<div className='space-y-4'>
			<div className='flex items-center justify-between'>
				<div>
					<div className='text-sm font-medium'>Username</div>
					<div className='text-sm text-muted-foreground/80'>
						Your login identifier
					</div>
				</div>
				<div className='flex items-center gap-4'>
					<div className='text-sm text-muted-foreground'>
						{isLoading ? '—' : user?.username || ''}
					</div>
				</div>
			</div>
		</div>
	)
}

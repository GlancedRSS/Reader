import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'

interface ReadingTimeProps {
	checked: boolean
	onChange: (checked: boolean) => void
	disabled?: boolean
}

export function ReadingTime({
	checked,
	onChange,
	disabled = false
}: ReadingTimeProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Reading Time</div>
				<div className='text-sm text-muted-foreground/80'>
					Estimated completion time
				</div>
			</div>
			<Switch
				checked={checked}
				disabled={disabled}
				onCheckedChange={onChange}
			/>
		</div>
	)
}

export function ReadingTimeSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Reading Time</div>
				<div className='text-sm text-muted-foreground/80'>
					Estimated completion time
				</div>
			</div>
			<Skeleton className='w-11 h-6 rounded-md' />
		</div>
	)
}

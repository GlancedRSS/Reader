import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'

interface ToggleSettingProps {
	label: string
	description: string
	checked: boolean
	onChange: (checked: boolean) => void
	disabled?: boolean
}

export function ToggleSetting({
	label,
	description,
	checked,
	onChange,
	disabled = false
}: ToggleSettingProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>{label}</div>
				<div className='text-sm text-muted-foreground/80'>{description}</div>
			</div>
			<Switch
				checked={checked}
				disabled={disabled}
				onCheckedChange={onChange}
			/>
		</div>
	)
}

interface ToggleSettingSkeletonProps {
	label: string
	description: string
}

export function ToggleSettingSkeleton({
	label,
	description
}: ToggleSettingSkeletonProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>{label}</div>
				<div className='text-sm text-muted-foreground/80'>{description}</div>
			</div>
			<Skeleton className='w-11 h-6 rounded-md' />
		</div>
	)
}

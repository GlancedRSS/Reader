import { Button } from '@/components/ui/button'

interface EmptyStateProps {
	onCreateTag: () => void
}

export function EmptyState({ onCreateTag }: EmptyStateProps) {
	return (
		<div className='py-12 text-center'>
			<h3 className='text-xl font-semibold text-foreground mb-3'>
				No tags yet
			</h3>
			<p className='text-sm text-muted-foreground leading-relaxed mb-6'>
				Create tags to organize your articles and feeds
			</p>
			<Button onClick={onCreateTag}>Create your first tag</Button>
		</div>
	)
}

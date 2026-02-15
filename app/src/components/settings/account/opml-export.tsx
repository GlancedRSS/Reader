import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'

import { useExportOPML } from '@/hooks/api/opml'

export function OpmlExport() {
	const [isExporting, setIsExporting] = useState(false)

	const exportOPML = useExportOPML()

	const handleOPMLExport = async () => {
		if (isExporting) return

		setIsExporting(true)

		try {
			await exportOPML.mutate({})
			toast.success(
				'Export started. You will be notified when ready to download.'
			)
		} catch (error) {
			toast.error(
				error instanceof Error ? error.message : 'Failed to start export'
			)
		} finally {
			setIsExporting(false)
		}
	}

	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Export Feeds</div>
				<div className='text-sm text-muted-foreground/80'>
					Download feeds as OPML
				</div>
			</div>
			<Button
				disabled={isExporting}
				onClick={handleOPMLExport}
				size='sm'
				variant='ghost'
			>
				{isExporting ? 'Starting Export' : 'Export OPML'}
			</Button>
		</div>
	)
}

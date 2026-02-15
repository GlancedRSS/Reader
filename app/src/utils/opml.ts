import {
	IoAlertCircle,
	IoArrowUpCircle,
	IoCheckmarkCircle,
	IoCloseCircle,
	IoSyncCircle,
	IoTime
} from 'react-icons/io5'
import { IconType } from 'react-icons/lib'

import type { OpmlStatus } from '@/types/opml'

export interface OpmlStatusInfo {
	label: string
	color: string
	icon: IconType
}

const STATUS_CONFIG: Record<OpmlStatus, OpmlStatusInfo> = {
	completed: {
		color: 'text-green-600',
		icon: IoCheckmarkCircle,
		label: 'Completed'
	},
	completed_with_errors: {
		color: 'text-yellow-600',
		icon: IoAlertCircle,
		label: 'Completed with errors'
	},
	failed: { color: 'text-red-600', icon: IoCloseCircle, label: 'Failed' },
	pending: { color: 'text-yellow-600', icon: IoTime, label: 'Pending' },
	processing: {
		color: 'text-blue-600',
		icon: IoSyncCircle,
		label: 'Processing'
	},
	uploaded: { color: 'text-blue-600', icon: IoArrowUpCircle, label: 'Uploaded' }
}

export function getOpmlStatus(status: OpmlStatus): OpmlStatusInfo {
	return (
		STATUS_CONFIG[status] || {
			color: 'text-muted-foreground',
			icon: IoAlertCircle,
			label: 'Unknown'
		}
	)
}

'use client'

import { ImportInfo, ImportRecords } from '@/components/imports'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useRef } from 'react'
import { toast } from 'sonner'

import { useOPMLStatusDetails } from '@/hooks/api'

export default function ImportDetailsPage() {
	const router = useRouter()

	const params = useParams()
	const jobId = params.jobId as string

	const { data, isLoading, error } = useOPMLStatusDetails(jobId)
	const hasShownError = useRef(false)

	useEffect(() => {
		if (error && !hasShownError.current) {
			toast.error('Access denied')
			console.error(error)
			hasShownError.current = true
			router.replace('/')
		}
	}, [error, router])

	return (
		<div className='max-w-3xl mx-auto'>
			<ImportInfo
				data={data}
				loading={isLoading}
			/>
			{data?.type === 'import' && data?.completed_at ? (
				<ImportRecords data={data} />
			) : null}
		</div>
	)
}

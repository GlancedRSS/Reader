'use client'

import { Header } from '@/components'
import { Tags } from '@/components/tags'

import useMetadata from '@/hooks/navigation/metadata'

export default function TagsPage() {
	useMetadata('Tags | Glanced Reader')

	return (
		<div className='max-w-xl mx-auto md:px-4'>
			<Header title='Tags' />
			<Tags />
		</div>
	)
}

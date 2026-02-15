import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

const useMetadata = (title: string) => {
	const router = useRouter()

	useEffect(() => {
		document.title = title
	}, [title, router])
}

export default useMetadata

import { SOURCE_LIST_PATH_KEY } from '@/components/articles/layout/virtualized-list'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import { usePathname } from 'next/navigation'
import { useEffect, useRef } from 'react'

const ARTICLE_LIST_ROUTES = [
	'/articles',
	'/articles/read',
	'/articles/unread',
	'/articles/search'
]

const ARTICLE_LIST_PREFIXES = ['/feeds/', '/folders/', '/read-later', '/tags/']

const ARTICLE_DETAIL_EXCLUSIONS = [
	'/articles/read',
	'/articles/unread',
	'/articles/search'
]

function isArticleListRoute(pathname: string): boolean {
	if (ARTICLE_LIST_ROUTES.includes(pathname)) {
		return true
	}

	return ARTICLE_LIST_PREFIXES.some((prefix) => pathname.startsWith(prefix))
}

function isArticleDetailRoute(pathname: string): boolean {
	if (!pathname.startsWith('/articles/')) {
		return false
	}

	if (ARTICLE_DETAIL_EXCLUSIONS.some((exclusion) => pathname === exclusion)) {
		return false
	}

	return true
}

export function useArticleListCleanup() {
	const pathname = usePathname()
	const prevPathnameRef = useRef(pathname)

	const resetArticles = useArticlesPaginationStore((state) => state.reset)
	const resetLayout = useLayoutStore((state) => state.reset)

	useEffect(() => {
		const prevPathname = prevPathnameRef.current
		prevPathnameRef.current = pathname

		if (prevPathname === pathname) {
			return
		}

		const wasArticleList = isArticleListRoute(prevPathname)
		const wasArticleDetail = isArticleDetailRoute(prevPathname)
		const isNowArticleList = isArticleListRoute(pathname)
		const isNowArticleDetail = isArticleDetailRoute(pathname)

		if (wasArticleList && !isNowArticleDetail) {
			resetArticles()
			resetLayout()
			sessionStorage.removeItem('scroll-to-article-id')
			sessionStorage.removeItem(SOURCE_LIST_PATH_KEY)
			return
		}

		if (wasArticleDetail && isNowArticleList) {
			const sourceListPath = sessionStorage.getItem(SOURCE_LIST_PATH_KEY)
			if (sourceListPath === pathname) {
				return
			}
			resetArticles()
			resetLayout()
			sessionStorage.removeItem('scroll-to-article-id')
			sessionStorage.removeItem(SOURCE_LIST_PATH_KEY)
			return
		}

		if (wasArticleDetail && !isNowArticleList) {
			resetArticles()
			resetLayout()
			sessionStorage.removeItem('scroll-to-article-id')
			sessionStorage.removeItem(SOURCE_LIST_PATH_KEY)
			return
		}
	}, [pathname, resetArticles, resetLayout])
}

import {
	IoAdd,
	IoAddOutline,
	IoBookmarks,
	IoBookmarksOutline,
	IoMenu,
	IoMenuOutline,
	IoNewspaper,
	IoNewspaperOutline,
	IoPricetags,
	IoPricetagsOutline,
	IoSearch,
	IoSearchOutline
} from 'react-icons/io5'

import type { NavigationItem } from '@/types/layout'

export const NAVIGATION_LINKS: NavigationItem[] = [
	{
		href: '/articles',
		icon: IoNewspaperOutline,
		icon_active: IoNewspaper,
		name: 'Articles'
	},
	{
		href: '/read-later',
		icon: IoBookmarksOutline,
		icon_active: IoBookmarks,
		name: 'Read Later'
	},
	{
		href: '/tags',
		icon: IoPricetagsOutline,
		icon_active: IoPricetags,
		name: 'Tags'
	}
]

export const MOBILE_NAVIGATION_LINKS: NavigationItem[] = [
	{
		href: '/articles',
		icon: IoNewspaperOutline,
		icon_active: IoNewspaper,
		name: 'Articles'
	},
	{
		href: '/read-later',
		icon: IoBookmarksOutline,
		icon_active: IoBookmarks,
		name: 'Saved'
	},
	{
		href: '#discover',
		icon: IoAddOutline,
		icon_active: IoAdd,
		name: 'Discover'
	},
	{
		href: '/search',
		icon: IoSearchOutline,
		icon_active: IoSearch,
		name: 'Search'
	},
	{
		href: '#menu',
		icon: IoMenuOutline,
		icon_active: IoMenu,
		name: 'Menu'
	}
]

import { useMemo } from 'react'

import { FolderTreeResponse } from '@/types/api'

export interface FlattenedTreeItem {
	id: string | null
	name: string
	depth: number
	type: 'folder' | 'feed'
	isExpanded: boolean
	hasChildren: boolean
	parentId: string | null
	unread_count: number
	is_pinned: boolean
	feed_count?: number
	website?: string | null | undefined
	is_active?: boolean
}

export function useFlattenedTree(
	folderTree: FolderTreeResponse[] | undefined,
	expandedFolders: Set<string>,
	maxDepth: number = 3
): FlattenedTreeItem[] {
	return useMemo(() => {
		if (!folderTree || folderTree.length === 0) {
			return []
		}

		const flattened: FlattenedTreeItem[] = []

		function traverse(
			node: FolderTreeResponse,
			depth: number,
			parentId: string | null = null
		) {
			const folderKey = node.id ?? '__uncategorized__'
			const isExpanded = expandedFolders.has(folderKey)

			flattened.push({
				depth,
				feed_count: node.feed_count,
				hasChildren: node.subfolders.length > 0 || node.feeds.length > 0,
				id: node.id ?? null,
				isExpanded,
				is_pinned: node.is_pinned,
				name: node.name,
				parentId,
				type: 'folder',
				unread_count: node.unread_count
			})

			if (isExpanded && depth < maxDepth) {
				for (const subfolder of node.subfolders) {
					traverse(subfolder, depth + 1, node.id ?? null)
				}

				for (const feed of node.feeds) {
					flattened.push({
						depth: depth + 1,
						hasChildren: false,
						id: feed.id,
						isExpanded: false,
						is_active: feed.is_active,
						is_pinned: feed.is_pinned,
						name: feed.title,
						parentId: node.id ?? null,
						type: 'feed',
						unread_count: feed.unread_count,
						website: feed.website
					})
				}
			}
		}

		for (const node of folderTree) {
			traverse(node, 0, null)
		}

		return flattened
	}, [folderTree, expandedFolders, maxDepth])
}

export function findItemIndex(
	flattened: FlattenedTreeItem[],
	folderId: string
): number {
	return flattened.findIndex(
		(item) => item.id === folderId && item.type === 'folder'
	)
}

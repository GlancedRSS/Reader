import Link from 'next/link'
import { IoEllipsisHorizontal, IoPencil, IoTrashOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow
} from '@/components/ui/table'

import type { TagListResponse } from '@/types/api'

interface TagsTableProps {
	tags: TagListResponse[]
	onEditTag: (tag: TagListResponse) => void
	onDeleteClick: (tag: TagListResponse) => void
}

export function TagsTable({ tags, onEditTag, onDeleteClick }: TagsTableProps) {
	if (tags.length === 0) {
		return (
			<div className='flex items-center justify-center h-64'>
				<p className='text-sm text-muted-foreground'>No tags found</p>
			</div>
		)
	}

	return (
		<div className='border rounded-xl max-h-[calc(100dvh-3.5rem-4.25rem-2.5rem-0.75rem-3.5rem)] md:max-h-[calc(100dvh-4.25rem-2.5rem-0.75rem-3rem)] overflow-scroll mt-3'>
			<Table>
				<TableHeader className='bg-sidebar-background'>
					<TableRow>
						<TableHead>Name</TableHead>
						<TableHead>Articles</TableHead>
						<TableHead className='text-right'>Actions</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{tags.map((tag) => (
						<TableRow key={tag.id}>
							<TableCell className='p-3'>
								<Link
									className='hover:underline'
									href={`/tags/${tag.id}`}
								>
									{tag.name}
								</Link>
							</TableCell>
							<TableCell className='p-3'>
								<span className='text-sm text-muted-foreground'>
									{tag.article_count ?? 0}
								</span>
							</TableCell>
							<TableCell className='py-0 text-right'>
								<DropdownMenu>
									<DropdownMenuTrigger asChild>
										<Button
											className='h-8 w-8'
											size='icon'
											variant='ghost'
										>
											<IoEllipsisHorizontal size={16} />
										</Button>
									</DropdownMenuTrigger>
									<DropdownMenuContent align='end'>
										<DropdownMenuItem onClick={() => onEditTag(tag)}>
											<IoPencil className='w-4 h-4 mr-2' />
											Edit
										</DropdownMenuItem>
										<DropdownMenuItem
											onClick={() => onDeleteClick(tag)}
											variant='destructive'
										>
											<IoTrashOutline className='w-4 h-4 mr-2' />
											Delete
										</DropdownMenuItem>
									</DropdownMenuContent>
								</DropdownMenu>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</div>
	)
}

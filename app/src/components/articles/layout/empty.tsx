export type EmptyTypes =
	| 'all'
	| 'read'
	| 'unread'
	| 'read-later'
	| 'read-later-read'
	| 'read-later-unread'
	| 'search'

const emptyContent = {
	all: {
		subtitle:
			"Articles from your feeds will appear here as soon as they're published",
		title: 'No new articles yet'
	},
	read: {
		subtitle: "Articles you've read will be saved here for future reference",
		title: 'Start reading to see'
	},
	'read-later': {
		subtitle: 'Save articles to enjoy them when you have time',
		title: 'Nothing saved for later'
	},
	'read-later-read': {
		subtitle: 'Revisit your favorite reads from this list',
		title: 'All caught up here'
	},
	'read-later-unread': {
		subtitle: "Dive into articles you've been meaning to read",
		title: 'Ready when you are'
	},
	search: {
		subtitle: "Try adjusting your filters to find what you're looking for",
		title: 'No articles match your filters'
	},
	unread: {
		subtitle: "You're all caught up! Check back later for new articles",
		title: "You're all caught up!"
	}
}

export default function Empty({
	type
}: {
	type:
		| 'all'
		| 'read'
		| 'unread'
		| 'read-later'
		| 'read-later-read'
		| 'read-later-unread'
		| 'search'
}) {
	const { title, subtitle } = emptyContent[type]

	return (
		<div className='h-[calc(100dvh-9rem-2.25rem-0.75rem)] md:h-[calc(100dvh-9rem-1.5rem)] max-w-md mx-auto text-center flex flex-col justify-center'>
			<h3 className='text-xl font-semibold text-foreground mb-3'>{title}</h3>
			<p className='text-sm text-muted-foreground leading-relaxed'>
				{subtitle}
			</p>
		</div>
	)
}

import { Filters } from '@/components/articles/layout/controls/filters'
import { MarkReadDropdown } from '@/components/articles/layout/controls/mark-read'
import { Refresh } from '@/components/articles/layout/controls/refresh'

import { ButtonGroup } from '@/components/ui/button-group'

export function Controls() {
	return (
		<ButtonGroup>
			<MarkReadDropdown />
			<Filters />
			<Refresh />
		</ButtonGroup>
	)
}

'use client'

import { ScrollWrapper } from '@/components'
import {
	NameChange,
	OpmlExport,
	PasswordChange,
	SessionList,
	Username
} from '@/components/settings/account'
import { InfoField, Section } from '@/components/settings/common'

import { useSettingsForm } from '@/hooks/features/settings'
import useMetadata from '@/hooks/navigation/metadata'

export default function AccountSettings() {
	useMetadata('Account | Glanced Reader')
	const { isLoading } = useSettingsForm()

	return (
		<ScrollWrapper>
			<Section title='Basics'>
				<Username isLoading={isLoading} />
				<NameChange isLoading={isLoading} />
				<InfoField
					description='Account creation date'
					field='created_at'
					label='Joined'
				/>
			</Section>

			<Section title='Security'>
				<InfoField
					description='Your most recent activity'
					field='last_login'
					label='Last Login'
				/>
				<PasswordChange />
			</Section>

			<SessionList />

			<Section title='Advanced'>
				<OpmlExport />
			</Section>
		</ScrollWrapper>
	)
}

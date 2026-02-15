'use client'

import { ScrollWrapper } from '@/components'
import {
	Form,
	Section,
	ToggleSetting,
	ToggleSettingSkeleton
} from '@/components/settings/common'
import {
	AppLayout,
	AppLayoutSkeleton,
	ArticleLayout,
	ArticleLayoutSkeleton,
	AutoRead,
	AutoReadSkeleton,
	DateFormatSelector,
	DateFormatSelectorSkeleton,
	FeedSort,
	FeedSortSkeleton,
	FontSize,
	FontSizeSkeleton,
	FontSpacing,
	FontSpacingSkeleton,
	LanguageSelector,
	LanguageSelectorSkeleton,
	ReadingTime,
	ReadingTimeSkeleton,
	ThemeSelector,
	ThemeSelectorSkeleton,
	TimeFormatSelector,
	TimeFormatSelectorSkeleton
} from '@/components/settings/preferences'

import { useSettingsForm } from '@/hooks/features/settings'
import useMetadata from '@/hooks/navigation/metadata'

export default function PreferencesSettings() {
	useMetadata('Preferences | Glanced Reader')
	const {
		localPreferences,
		isLoading,
		isSaving,
		hasChanges,
		handleUpdatePreference,
		handleSavePreferences
	} = useSettingsForm()

	if (isLoading) {
		return (
			<ScrollWrapper>
				<Section title='General'>
					<ThemeSelectorSkeleton />
					<LanguageSelectorSkeleton />
					<DateFormatSelectorSkeleton />
					<TimeFormatSelectorSkeleton />
				</Section>

				<Section title='Appearance'>
					<ToggleSettingSkeleton
						description='Article preview images'
						label='Thumbnails'
					/>
					<ToggleSettingSkeleton
						description='Show website icons'
						label='Feed Icons'
					/>
					<ToggleSettingSkeleton
						description='Feed content previews'
						label='Summaries'
					/>
				</Section>

				<Section title='Layout'>
					<AppLayoutSkeleton />
					<ArticleLayoutSkeleton />
					<FeedSortSkeleton />
				</Section>

				<Section title='Text & Reading'>
					<FontSizeSkeleton />
					<FontSpacingSkeleton />
				</Section>

				<Section title='Reading Experience'>
					<AutoReadSkeleton />
					<ReadingTimeSkeleton />
				</Section>
			</ScrollWrapper>
		)
	}

	return (
		<ScrollWrapper>
			<Section title='General'>
				<ThemeSelector
					onChange={(value) => handleUpdatePreference('theme', value)}
					value={localPreferences.theme}
				/>

				<LanguageSelector
					disabled
					onChange={(value) => handleUpdatePreference('language', value)}
					value={localPreferences.language}
				/>

				<DateFormatSelector
					onChange={(value) => handleUpdatePreference('date_format', value)}
					value={localPreferences.date_format}
				/>

				<TimeFormatSelector
					onChange={(value) => handleUpdatePreference('time_format', value)}
					value={localPreferences.time_format}
				/>
			</Section>

			<Section title='Appearance'>
				<ToggleSetting
					checked={localPreferences.show_article_thumbnails}
					description='Article preview images'
					label='Thumbnails'
					onChange={(checked) =>
						handleUpdatePreference('show_article_thumbnails', checked)
					}
				/>

				<ToggleSetting
					checked={localPreferences.show_feed_favicons}
					description='Show website icons'
					label='Feed Icons'
					onChange={(checked) =>
						handleUpdatePreference('show_feed_favicons', checked)
					}
				/>

				<ToggleSetting
					checked={localPreferences.show_summaries}
					description='Feed content previews'
					label='Summaries'
					onChange={(checked) =>
						handleUpdatePreference('show_summaries', checked)
					}
				/>
			</Section>

			<Section title='Layout'>
				<AppLayout
					onChange={(value) => handleUpdatePreference('app_layout', value)}
					value={localPreferences.app_layout}
				/>

				<ArticleLayout
					onChange={(value) => handleUpdatePreference('article_layout', value)}
					value={localPreferences.article_layout}
				/>

				<FeedSort
					onChange={(value) => handleUpdatePreference('feed_sort_order', value)}
					value={localPreferences.feed_sort_order}
				/>
			</Section>

			<Section title='Text & Reading'>
				<FontSize
					onChange={(value) => handleUpdatePreference('font_size', value)}
					value={localPreferences.font_size}
				/>

				<FontSpacing
					onChange={(value) => handleUpdatePreference('font_spacing', value)}
					value={localPreferences.font_spacing}
				/>
			</Section>

			<Section title='Reading Experience'>
				<Form
					hasChanges={hasChanges}
					isSaving={isSaving}
					onSave={handleSavePreferences}
					saveText='Save Preferences'
					savingText='Saving...'
				>
					<AutoRead
						onChange={(value) =>
							handleUpdatePreference('auto_mark_as_read', value)
						}
						value={localPreferences.auto_mark_as_read}
					/>

					<ReadingTime
						checked={localPreferences.estimated_reading_time}
						onChange={(checked) =>
							handleUpdatePreference('estimated_reading_time', checked)
						}
					/>
				</Form>
			</Section>
		</ScrollWrapper>
	)
}

'use client'

import AsyncSelect from 'react-select/async'

import { useIsMobile } from '@/hooks/ui/media-query'

import type {
	ActionMeta,
	GroupBase,
	MultiValue,
	OptionsOrGroups,
	SingleValue
} from 'react-select'

import { cn } from '@/utils'

export interface SelectOption {
	label: string
	value: string
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ReactSelectComponent = React.ComponentType<any>

interface AsyncSelectProps {
	cacheOptions?: boolean
	classNames?: {
		container?: () => string
		control?: () => string
	}
	components?: {
		MultiValueLabel?: ReactSelectComponent
		MultiValueRemove?: ReactSelectComponent
		Option?: ReactSelectComponent
	}
	defaultOptions?:
		| OptionsOrGroups<SelectOption, GroupBase<SelectOption>>
		| boolean
	debounceTimeout?: number
	inputId?: string
	isDisabled?: boolean
	isMulti?: boolean
	loadOptions: (
		inputValue: string
	) => Promise<OptionsOrGroups<SelectOption, GroupBase<SelectOption>>>
	loadingMessage?: () => string
	menuPlacement?: 'top' | 'auto' | 'bottom'
	noOptionsMessage?: ({ inputValue }: { inputValue: string }) => string
	onChange: (
		newValue: MultiValue<SelectOption> | null,
		actionMeta: ActionMeta<SelectOption>
	) => void
	placeholder?: string
	value: SelectOption[]
}

const defaultClassNames = {
	clearIndicator: () => 'hidden!',
	dropdownIndicator: () => 'hidden!',
	indicatorContainer: () => 'hidden',
	indicatorSeparator: () => 'hidden',
	input: () => 'text-foreground! py-1',
	loadingIndicator: () => 'p-2 text-muted-foreground',
	menu: () =>
		'z-50! min-w-[8rem]! p-0.5! overflow-auto! text-popover-foreground! rounded-xl! border! border-border/50! bg-background/90! backdrop-blur-xs! shadow-2xl! shadow-black/5! px-1.5!',
	multiValue: () =>
		'bg-transparent! border! rounded-md! max-w-[calc(100%-2rem)]!',
	multiValueLabel: () =>
		'text-foreground! truncate! max-w-[120px] sm:max-w-[150px]!',
	multiValueRemove: () =>
		'bg-transparent text-muted-foreground hover:text-destructive-accent-foreground! hover:bg-destructive-accent! rounded-l-none! rounded-r-md! transition-colors duration-200 cursor-pointer',
	option: ({
		isFocused,
		isSelected
	}: {
		isFocused: boolean
		isSelected: boolean
	}) =>
		cn(
			'relative flex w-full select-none items-center rounded-lg border border-transparent! cursor-pointer transition-all duration-200 ease-out py-1.5 my-0.5 first-of-type:mt-0 last-of-type:mb-0 pl-3 pr-2 text-sm outline-none',
			isFocused && 'border-primary/20! bg-accent! text-accent-foreground!',
			isSelected && 'bg-accent! text-accent-foreground!'
		),
	placeholder: () => 'text-muted-foreground sm:text-sm',
	singleValue: () => 'text-foreground!',
	valueContainer: () => 'flex! flex-wrap! gap-1.5! p-1!'
}

export function GenericAsyncSelect({
	cacheOptions = true,
	classNames,
	components,
	defaultOptions,
	debounceTimeout = 300,
	inputId,
	isDisabled = false,
	isMulti = true,
	loadOptions,
	loadingMessage,
	menuPlacement,
	noOptionsMessage,
	onChange,
	placeholder = 'Type to search...',
	value
}: AsyncSelectProps) {
	const isMobile = useIsMobile()
	const effectiveMenuPlacement = menuPlacement || (isMobile ? 'top' : 'bottom')
	const handleChange = (
		newValue: MultiValue<SelectOption> | SingleValue<SelectOption>,
		actionMeta: ActionMeta<SelectOption>
	) => {
		if (isMulti) {
			onChange((newValue as MultiValue<SelectOption>) || [], actionMeta)
		} else {
			onChange(
				(newValue as SingleValue<SelectOption>)
					? [(newValue as SingleValue<SelectOption>)!]
					: [],
				actionMeta
			)
		}
	}

	const asyncSelectProps: Record<string, unknown> = {
		cacheOptions,
		classNames: {
			...defaultClassNames,
			control: () =>
				`bg-transparent! rounded-lg! border-border! shadow-xs! transition-[color,box-shadow]! text-base sm:text-sm ${isMulti ? 'py-1.5 overflow-x-auto!' : 'h-11 sm:h-10'}`,
			...classNames
		},
		components,
		defaultOptions,
		inputId,
		isDisabled,
		isMulti,
		loadOptions,
		loadingMessage: loadingMessage || (() => 'Loading...'),
		menuPlacement: effectiveMenuPlacement,
		noOptionsMessage:
			noOptionsMessage ||
			(({ inputValue }: { inputValue: string }) =>
				inputValue ? 'No results found' : 'Type to search...'),
		onChange: handleChange,
		placeholder,
		value
	}

	if (debounceTimeout !== undefined) {
		asyncSelectProps.debounceTimeout = debounceTimeout
	}

	return (
		<AsyncSelect
			{...(asyncSelectProps as React.ComponentProps<typeof AsyncSelect>)}
		/>
	)
}

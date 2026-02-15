import { useEffect } from 'react'

type HotkeyMap = Record<string, () => void>

export const useKeyboardShortcuts = (
	setCommandPaletteOpen: (open: boolean) => void
) => {
	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
				event.preventDefault()
				setCommandPaletteOpen(true)
			}
		}

		document.addEventListener('keydown', handleKeyDown)
		return () => document.removeEventListener('keydown', handleKeyDown)
	}, [setCommandPaletteOpen])
}

export const useArticleHotkeys = (hotkeyMap: HotkeyMap, enabled = true) => {
	useEffect(() => {
		if (!enabled) return

		const handleKeyUp = (event: KeyboardEvent) => {
			const target = event.target as HTMLElement
			if (
				target.tagName === 'INPUT' ||
				target.tagName === 'TEXTAREA' ||
				target.isContentEditable
			) {
				return
			}

			const key = event.key.toLowerCase()
			const callback = hotkeyMap[key]

			if (callback) {
				event.preventDefault()
				callback()
			}
		}

		document.addEventListener('keyup', handleKeyUp)
		return () => document.removeEventListener('keyup', handleKeyUp)
	}, [hotkeyMap, enabled])
}

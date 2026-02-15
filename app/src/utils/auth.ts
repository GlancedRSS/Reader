import zxcvbn from 'zxcvbn'

export interface PasswordStrength {
	feedback: {
		suggestions: string[]
		warning: string
	}
}

export const getPasswordStrength = (password: string): PasswordStrength => {
	if (!password) {
		return {
			feedback: { suggestions: [], warning: '' }
		}
	}

	const result = zxcvbn(password)

	return {
		feedback: result.feedback
	}
}

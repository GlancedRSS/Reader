// POST '/api/v1/auth/register'
export interface RegistrationRequest {
	username: string
	password: string
}

// POST '/api/v1/auth/login'
export interface LoginRequest {
	username: string
	password: string
}

// POST '/api/v1/auth/change-password'
export interface PasswordChangeRequest {
	current_password: string
	new_password: string
}

// GET '/api/v1/auth/sessions'
export interface SessionResponse {
	session_id: string
	created_at: string
	last_used: string
	expires_at: string
	user_agent?: string
	ip_address?: string
	current: boolean
}

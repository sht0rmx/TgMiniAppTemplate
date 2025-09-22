export const getAccessToken = () => localStorage.getItem('access_token')
export const getRefreshToken = () => localStorage.getItem('refresh_token')
export const setTokens = ({ access_token, refresh_token }) => {
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)
}
export const clearTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const refreshAccessToken = async () => {
  const refresh_token = getRefreshToken()
  if (!refresh_token) return null

  try {
    const resp = await fetch(`${import.meta.env.VITE_API_URL}/token/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token }),
    })

    if (!resp.ok) return null

    const data = await resp.json()
    if (data.access_token && data.refresh_token) {
      setTokens(data)
      return data.access_token
    }
    return null
  } catch (err) {
    console.error('Failed to refresh token:', err)
    return null
  }
}

export const authFetch = async (url, options = {}) => {
  let token = getAccessToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    let resp = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
      ...options,
      headers,
    })

    if (resp.status === 401) {
      token = await refreshAccessToken()
      if (!token) throw new Error('Unauthorized and failed to refresh token')

      headers['Authorization'] = `Bearer ${token}`
      resp = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
        ...options,
        headers,
      })
    }

    if (!resp.ok) {
      const errorData = await resp.json().catch(() => ({}))
      console.error(`HTTP error! Status: ${resp.status}`, errorData)
      return errorData
    }

    return await resp.json()
  } catch (error) {
    console.error('Network or server error:', error)
    throw error
  }
}

export const send_auth = async (initData) => {
  const data = await authFetch('/telegram/auth/webapp', {
    method: 'POST',
    body: JSON.stringify({ initData }),
  })

  if (data?.tokens?.access_token) {
    setTokens(data.tokens)
  }

  return data
}

export const ping = async () => {
  const success = await authFetch('/ping')
  return !!success
}

export const logout = async () => {
  const refresh_token = getRefreshToken()
  if (!refresh_token) {
    clearTokens()
    return
  }

  try {
    const resp = await fetch(`${import.meta.env.VITE_API_URL}/token/revoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getAccessToken()}`,
      },
      body: JSON.stringify({ refresh_token }),
    })

    if (!resp.ok) {
      const errorData = await resp.json().catch(() => ({}))
      console.warn('Failed to revoke token:', resp.status, errorData)
    }
  } catch (err) {
    console.error('Network error while revoking token:', err)
  } finally {
    clearTokens()
  }
}

export const fetchUserProfile = async () => {
  return await authFetch('/user/profile')
}

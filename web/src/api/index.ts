const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// Token storage
const TOKEN_KEY = 'auth_token'
const USER_ID_KEY = 'user_id'
const USER_ROLE_KEY = 'user_role'

export const auth = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  getUserId: () => localStorage.getItem(USER_ID_KEY),
  setUserId: (id: string) => localStorage.setItem(USER_ID_KEY, id),
  getUserRole: () => localStorage.getItem(USER_ROLE_KEY) || 'anonymous',
  setUserRole: (role: string) => localStorage.setItem(USER_ROLE_KEY, role),
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_ID_KEY)
    localStorage.removeItem(USER_ROLE_KEY)
  },
  isLoggedIn: () => !!localStorage.getItem(TOKEN_KEY),
  isAdmin: () => localStorage.getItem(USER_ROLE_KEY) === 'admin',
  isAnonymous: () => !localStorage.getItem(TOKEN_KEY)
}

// Auth-aware fetch
async function authFetch(url: string, options: RequestInit = {}, requireAuth: boolean = true) {
  const token = auth.getToken()
  const headers = {
    ...(options.headers || {}),
  }
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(url, { ...options, headers })

  if (res.status === 401) {
    auth.clear()
    if (requireAuth) {
      window.location.href = '/admin/login'
    }
    throw new Error('Unauthorized')
  }

  if (res.status === 403) {
    throw new Error('Forbidden')
  }

  return res
}

export const authApi = {
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Login failed')
    }
    const data = await res.json()
    auth.setToken(data.token)
    auth.setUserId(data.user_id)
    auth.setUserRole(data.role)
    return data
  },

  register: async (username: string, password: string, role: string = 'internal') => {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role })
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Register failed')
    }
    const data = await res.json()
    auth.setToken(data.token)
    auth.setUserId(data.user_id)
    auth.setUserRole(data.role)
    return data
  },

  verify: async () => {
    const token = auth.getToken()
    if (!token) return { valid: false, role: 'anonymous' }
    const res = await fetch(`${API_BASE}/api/auth/verify`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) {
      auth.clear()
      return { valid: false, role: 'anonymous' }
    }
    const data = await res.json()
    auth.setUserRole(data.role)
    return data
  },

  logout: async () => {
    auth.clear()
  }
}

export const userApi = {
  getMe: () => authFetch(`${API_BASE}/api/users/me`, {}, false).then(r => r.json()),
  getAvailableBots: () => authFetch(`${API_BASE}/api/users/available-bots`, {}, false).then(r => r.json())
}

export const teamApi = {
  getTeams: () => authFetch(`${API_BASE}/api/teams`).then(r => r.json()),
  createTeam: (name: string) =>
    authFetch(`${API_BASE}/api/teams`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    }).then(r => r.json()),
  updateTeam: (id: string, name: string) =>
    authFetch(`${API_BASE}/api/teams/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    }).then(r => r.json()),
  deleteTeam: (id: string) =>
    authFetch(`${API_BASE}/api/teams/${id}`, { method: 'DELETE' }).then(r => r.json()),
  getTeamMembers: (teamId: string) =>
    authFetch(`${API_BASE}/api/teams/${teamId}/members`).then(r => r.json()),
  addTeamMember: (teamId: string, userId: string) =>
    authFetch(`${API_BASE}/api/teams/${teamId}/members`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    }).then(r => r.json()),
  removeTeamMember: (teamId: string, userId: string) =>
    authFetch(`${API_BASE}/api/teams/${teamId}/members/${userId}`, { method: 'DELETE' }).then(r => r.json())
}

interface ChatRequest {
  bot_id?: string
  session_id: string
  message: string
  user_id?: string
}

interface ChatResponse {
  response: string
  source: string
  intent: string
  confidence: number
  reference_doc_id?: string
  reference_qa_id?: string
  conversation_id: string
}

interface Message {
  id: string
  content: string
  is_from_user: boolean
  source: string
  timestamp: string
}

interface HistoryResponse {
  session_id: string
  messages: Message[]
}

export const chatApi = {
  send: async (req: ChatRequest): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req)
    })
    if (!res.ok) throw new Error('Chat API error')
    return res.json()
  },

  history: async (sessionId: string, botId: string): Promise<HistoryResponse> => {
    const res = await fetch(`${API_BASE}/api/history/${sessionId}?bot_id=${botId}`)
    if (!res.ok) throw new Error('History API error')
    return res.json()
  },

  rate: async (conversationId: string, rating: number, feedback?: string) => {
    const res = await fetch(`${API_BASE}/api/rate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId, rating, feedback })
    })
    if (!res.ok) throw new Error('Rate API error')
    return res.json()
  }
}

export const adminApi = {
  // Bots
  getBots: () => authFetch(`${API_BASE}/api/admin/bots`).then(r => r.json()),
  createBot: (data: { name: string; industry_type: string; description?: string }) =>
    authFetch(`${API_BASE}/api/admin/bots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
  updateBot: (botId: string, data: { name?: string; industry_type?: string; description?: string }) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
  getDefaultBot: () => authFetch(`${API_BASE}/api/admin/bots/default`).then(r => r.json()),
  setDefaultBot: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/bots/default/${botId}`, { method: 'PUT' }).then(r => r.json()),
  deleteBot: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}`, { method: 'DELETE' }).then(r => r.json()),

  getBotConfig: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}/config`).then(r => r.json()),

  updateBotConfig: (botId: string, config: Record<string, unknown>) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    }).then(r => r.json()),

  // Documents
  getDocuments: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/documents?bot_id=${botId}`).then(r => r.json()),

  uploadDocument: async (botId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await authFetch(`${API_BASE}/api/admin/documents?bot_id=${botId}`, {
      method: 'POST',
      body: formData
    })
    return res.json()
  },

  deleteDocument: (docId: string) =>
    authFetch(`${API_BASE}/api/admin/documents/${docId}`, { method: 'DELETE' }).then(r => r.json()),

  reindexDocument: (docId: string) =>
    authFetch(`${API_BASE}/api/admin/documents/${docId}/reindex?chunker_type=title_aware`, { method: 'POST' }).then(r => r.json()),

  // QA
  getQA: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/qa?bot_id=${botId}`).then(r => r.json()),

  createQA: (data: { bot_id: string; question: string; answer: string; keywords?: string; category?: string }) =>
    authFetch(`${API_BASE}/api/admin/qa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  updateQA: (qaId: string, data: Record<string, unknown>) =>
    authFetch(`${API_BASE}/api/admin/qa/${qaId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  deleteQA: (qaId: string) =>
    authFetch(`${API_BASE}/api/admin/qa/${qaId}`, { method: 'DELETE' }).then(r => r.json()),

  // Analytics
  getAnalytics: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/analytics/${botId}`).then(r => r.json()),

  // Bot Access Control
  getBotAccess: (botId: string) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}/access`).then(r => r.json()),
  updateBotAccess: (botId: string, accessType: string, allowedUsers: string[], allowedTeams: string[]) =>
    authFetch(`${API_BASE}/api/admin/bots/${botId}/access`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        access_type: accessType,
        allowed_users: allowedUsers,
        allowed_teams: allowedTeams
      })
    }).then(r => r.json()),

  // Users (for admin)
  getUsers: () => authFetch(`${API_BASE}/api/admin/users`).then(r => r.json())
}

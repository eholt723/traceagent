const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${text}`)
  }
  return res.json()
}

export const api = {
  upsertUser: (uuid, name) =>
    request('/users/upsert', { method: 'POST', body: JSON.stringify({ uuid, name }) }),

  listRuns: (limit = 20, offset = 0) =>
    request(`/runs?limit=${limit}&offset=${offset}`),

  getRun: (runId) =>
    request(`/runs/${runId}`),

  createRun: (query, userId = null) =>
    request('/runs', { method: 'POST', body: JSON.stringify({ query, user_id: userId, is_public: true }) }),

  forkRun: (runId, query, userId = null) =>
    request(`/runs/${runId}/fork`, { method: 'POST', body: JSON.stringify({ query, user_id: userId, is_public: true }) }),
}

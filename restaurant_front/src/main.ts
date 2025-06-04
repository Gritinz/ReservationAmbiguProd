// main.ts

import App from './App.vue'
import { createApp } from 'vue'
import router from './router'
import axios from 'axios'
import Cookies from 'js-cookie'

// Import de la fonction utilitaire
import { clearExpiredTokens } from './utils/authUtils'

const app = createApp(App)

// Base URL pour tes requêtes API Django
const API_BASE_URL = import.meta.env.VITE_API_URL

// Configure Axios global
axios.defaults.baseURL = API_BASE_URL
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true // Important pour envoyer les cookies

// Rend Axios accessible globalement si nécessaire
app.config.globalProperties.$axios = axios

// --- Intercepteur de requêtes pour ajouter le jeton CSRF ---
axios.interceptors.request.use(
  (config) => {
    // Nettoie les tokens expirés avant chaque requête (optionnel)
    clearExpiredTokens()

    // Ajoute le token JWT si disponible
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    // Récupère le token CSRF du cookie et l'ajoute aux méthodes non-GET
    const csrfToken = Cookies.get('csrftoken')
    if (
      csrfToken &&
      config.method &&
      ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())
    ) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)
// --- FIN Intercepteur de requêtes ---

// --- Intercepteur de réponses pour gérer les erreurs (401, 403, etc.) ---
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Rafraîchissement du token JWT si expiré
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const response = await axios.post('/backoffice/api/token/refresh/', {
            refresh: refreshToken,
          })
          const newAccessToken = response.data.access
          localStorage.setItem('access_token', newAccessToken)
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return axios(originalRequest)
        } catch (refreshError) {
          console.error('Erreur lors du rafraîchissement du token:', refreshError)
          // Nettoie tous les tokens
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('is_admin')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // Aucun refresh token disponible
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('is_admin')
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    // Gestion spécifique des erreurs 403 (CSRF ou permissions)
    if (error.response?.status === 403) {
      console.error('Erreur 403 Forbidden. Possible problème de CSRF ou de permissions.', error.response.data)
    }

    return Promise.reject(error)
  }
)
// --- FIN Intercepteur de réponses ---

// Nettoie les tokens expirés dès le lancement de l'app
clearExpiredTokens()

// Montage de l'app
app.use(router).mount('#app')
// src/utils/authUtils.ts

/**
 * Vérifie si un token JWT est expiré.
 *
 * @param token - Le token JWT à vérifier
 * @returns true si le token est expiré, false sinon
 */
export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // Convertir en millisecondes
    return Date.now() >= exp
  } catch (error) {
    console.error("Erreur lors de la lecture du token :", error)
    return true // Si le token est malformé, on le considère comme expiré
  }
}

/**
 * Nettoie les tokens expirés du localStorage.
 */
export function clearExpiredTokens(): void {
  const accessToken = localStorage.getItem('access_token')
  const refreshToken = localStorage.getItem('refresh_token')

  if (accessToken && isTokenExpired(accessToken)) {
    console.log('Access token expiré, suppression...')
    localStorage.removeItem('access_token')
  }

  if (refreshToken && isTokenExpired(refreshToken)) {
    console.log('Refresh token expiré, suppression...')
    localStorage.removeItem('refresh_token')
  }

  // Optionnel : supprime aussi l'info admin si plus authentifié
  if (!accessToken || isTokenExpired(accessToken)) {
    localStorage.removeItem('is_admin')
  }
}
// router/index.ts

import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../views/LoginPage.vue';
import BackofficePage from '../views/BackofficePage.vue';
import ForgotPasswordPage from '../views/ForgotPasswordPage.vue';
import ResetPasswordPage from '../views/ResetPasswordPage.vue';
import axios from 'axios';

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/backoffice',
    name: 'Backoffice',
    component: BackofficePage,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordPage,
  },
  {
    path: '/reset-password/:uidb64/:token',
    name: 'ResetPassword',
    component: ResetPasswordPage,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Middleware de protection de route
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  const is_admin = localStorage.getItem('is_admin') === 'true';
  const { requiresAuth, requiresAdmin } = to.meta;

  // Si la route requiert une authentification
  if (requiresAuth && !isAuthenticated) {
    localStorage.removeItem('is_admin');
    return next('/login');
  }

  // Si la route requiert d'être admin ET l'utilisateur est connecté mais pas admin
  if (requiresAdmin && isAuthenticated && !is_admin) {
    try {
      const response = await axios.get('/backoffice/api/check-admin/');
      if (response.data.is_admin) {
        localStorage.setItem('is_admin', 'true');
        return next();
      } else {
        localStorage.removeItem('is_admin');
        return next('/login');
      }
    } catch (error) {
      console.error("Erreur lors de la vérification de l'admin :", error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('is_admin');
      return next('/login');
    }
  }

  // Si la route requiert d'être admin ET l'utilisateur n'est pas authentifié
  if (requiresAdmin && !isAuthenticated) {
    return next('/login');
  }

  // Redirection automatique si déjà connecté
  if (
    to.path === '/login' &&
    isAuthenticated &&
    localStorage.getItem('is_admin') === 'true'
  ) {
    return next('/backoffice');
  }

  // Tout va bien, on continue
  return next();
});

export default router;
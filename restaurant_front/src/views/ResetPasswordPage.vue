<template>
  <div class="container">
    <h1>Réinitialiser votre mot de passe</h1>
    <p v-if="!isValidLink" class="error">Le lien de réinitialisation est invalide ou a expiré.</p>
    <form @submit.prevent="resetPassword" v-if="isValidLink">
      <div>
        <label for="new_password1">Nouveau mot de passe :</label>
        <input type="password" id="new_password1" v-model="newPassword1" required />
      </div>
      <div>
        <label for="new_password2">Confirmer nouveau mot de passe :</label>
        <input type="password" id="new_password2" v-model="newPassword2" required />
      </div>
      <button type="submit">Réinitialiser le mot de passe</button>
      <p v-if="message" :class="{ 'success': isSuccess, 'error': !isSuccess }">{{ message }}</p>
    </form>
    <router-link to="/login" class="back-to-login">Retour à la connexion</router-link>
  </div>
</template>

<script>
export default {
  props: ['uidb64', 'token'],
  data() {
    return {
      newPassword1: '',
      newPassword2: '',
      message: '',
      isSuccess: false,
      isValidLink: true,
    };
  },
  async created() {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://restaurant-back-h79s.onrender.com'; 

    if (!this.uidb64 || !this.token) {
      this.isValidLink = false;
      this.message = 'Lien incomplet ou invalide.';
      return;
    }

    try {
      // Optionnel : vérifie si le token est valide dès le début
      const response = await this.$axios.head(`${BACKEND_URL}/api/check-token/${this.uidb64}/${this.token}/`);
      this.isValidLink = response.data.valid ?? true;
    } catch (error) {
      this.isValidLink = false;
      this.message = 'Le lien est invalide ou a expiré.';
    }
  },
  methods: {
    async resetPassword() {
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://restaurant-back-h79s.onrender.com'; 

      this.message = '';
      this.isSuccess = false;

      if (this.newPassword1 !== this.newPassword2) {
        this.message = 'Les mots de passe ne correspondent pas.';
        this.isSuccess = false;
        return;
      }

      try {
        const response = await this.$axios.post(
          `${BACKEND_URL}/api/password-reset-confirm/${this.uidb64}/${this.token}/`,
          { new_password: this.newPassword1 }
        );

        this.message = 'Votre mot de passe a été réinitialisé avec succès ! Vous pouvez maintenant vous connecter.';
        this.isSuccess = true;

        setTimeout(() => {
          this.$router.push('/login');
        }, 3000);

      } catch (error) {
        console.error('Erreur lors de la réinitialisation du mot de passe :', error);
        this.isSuccess = false;

        if (error.response?.status === 400) {
          this.message = 'Le lien est invalide ou a expiré.';
          this.isValidLink = false;
        } else if (error.response?.data?.error) {
          this.message = error.response.data.error;
        } else {
          this.message = 'Une erreur est survenue. Veuillez réessayer.';
        }
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  text-align: center;
}

h1 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 1rem;
}

p.error {
  color: #c62828;
  font-size: 0.95rem;
  text-align: left;
  margin-top: -0.5rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  font-weight: 600;
  text-align: left;
  font-size: 0.95rem;
  color: #555;
}

input[type="password"] {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #42b983;
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

button[type="submit"] {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 0.75rem;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #3aa876;
}

.success,
.error {
  font-size: 0.95rem;
  text-align: left;
  margin-top: 0.5rem;
}

.success {
  color: #2e7d32;
}

.error {
  color: #c62828;
}

.back-to-login {
  display: block;
  margin-top: 1.5rem;
  color: #42b983;
  text-decoration: none;
  font-size: 0.95rem;
}

.back-to-login:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 500px) {
  .container {
    margin: 1rem;
    padding: 1.5rem;
  }

  input,
  button[type="submit"] {
    font-size: 1rem;
  }
}
</style>
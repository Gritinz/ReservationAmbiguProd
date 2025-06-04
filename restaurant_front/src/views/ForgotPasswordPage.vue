<template>
  <div class="container">
    <h1>Mot de passe oublié ?</h1>
    <p>Veuillez entrer votre adresse e-mail pour réinitialiser votre mot de passe.</p>
    <form @submit.prevent="sendResetEmail">
      <div>
        <label for="email">E-mail :</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <button type="submit">Envoyer le lien de réinitialisation</button>
      <p v-if="message" :class="{ 'success': isSuccess, 'error': !isSuccess }">{{ message }}</p>
    </form>
    <router-link to="/login" class="back-to-login">Retour à la connexion</router-link>
  </div>
</template>

<script>
// import Cookies from 'js-cookie'; // Pas nécessaire de l'importer ici si l'intercepteur le gère
export default {
  data() {
    return {
      email: '',
      message: '',
      isSuccess: false,
    };
  },
  async created() {
    // Assurez-vous d'avoir le cookie CSRF au chargement de la page
    try {
      await this.$axios.get('/backoffice/api/get-csrf-token/');
    } catch (e) {
      console.error("Erreur lors de la récupération du token CSRF:", e);
    }
  },
  methods: {
    async sendResetEmail() {
  try {
    this.message = '';
    this.isSuccess = false;

    // Envoie la demande à l'URL correcte
    await this.$axios.post('/api/password-reset/', { email: this.email });

    this.message = 'Un lien de réinitialisation a été envoyé à votre adresse e-mail.';
    this.isSuccess = true;
    this.email = '';
  } catch (error) {
    console.error("Erreur lors de l'envoi de l'e-mail :", error);

    if (error.response && error.response.status === 403) {
      this.message = 'Accès refusé. Problème de sécurité (CSRF).';
      this.isSuccess = false;
    } else {
      // On affiche quand même un message neutre
      this.message = 'Un lien de réinitialisation a été envoyé à votre adresse e-mail.';
      this.isSuccess = true;
    }
  }
}   
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

p {
  font-size: 0.95rem;
  color: #666;
  margin-bottom: 1.5rem;
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

input[type="email"] {
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

.success {
  color: #2e7d32;
  font-size: 0.95rem;
  text-align: left;
  margin-top: -0.5rem;
}

.error {
  color: #c62828;
  font-size: 0.95rem;
  text-align: left;
  margin-top: -0.5rem;
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
<template>
  <div class="container">
    <h1>Connexion au Backoffice</h1>
    <form @submit.prevent="login">
      <div>
        <label>Nom d'utilisateur :</label>
        <input v-model="credentials.username" type="text" required />
      </div>
      <div>
        <label>Mot de passe :</label>
        <input v-model="credentials.password" type="password" required />
      </div>
      <button type="submit">Se connecter</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <router-link to="/forgot-password" class="forgot-password-link">Mot de passe oublié ?</router-link>
  </div>
</template>

<script>
// import Cookies from 'js-cookie'; // Pas nécessaire de l'importer ici si l'intercepteur le gère
export default {
  data() {
    return {
      credentials: {
        username: '',
        password: '',
      },
      error: '',
    };
  },
  async created() {
    // Optionnel: Assurez-vous d'avoir le cookie CSRF au chargement de la page
    // Cela ne fait pas de mal de le demander au cas où.
    // L'intercepteur Axios le gérera pour les requêtes POST,
    // mais cette requête GET force le serveur à définir le cookie.
    try {
      await this.$axios.get('/backoffice/api/get-csrf-token/');
    } catch (e) {
      console.error("Erreur lors de la récupération du token CSRF:", e);
      // Pas bloquant, le 403 sera géré par l'intercepteur si le cookie est manquant.
    }
  },
  methods: {
    async login() {
  try {
    this.error = '';
    console.log("Envoi des identifiants à l'API...");
    const response = await this.$axios.post('/backoffice/api/login/', this.credentials);
    
    console.log("Réponse reçue :", response.data);

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    this.$router.push('/backoffice');
  } catch (error) {
    console.error("Erreur de connexion :", error);

    if (error.response) {
      console.log("Status code:", error.response.status);
      console.log("Données de réponse:", error.response.data);
    }

    if (error.response && error.response.status === 403) {
      this.error = 'Accès refusé. Problème de sécurité (CSRF).';
    } else if (error.response && error.response.status === 401) {
      this.error = 'Identifiants invalides.';
    } else {
      this.error = 'Échec de la connexion. Vérifiez vos identifiants ou contactez l’administrateur.';
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

input {
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

.error {
  color: #c62828;
  font-size: 0.95rem;
  text-align: left;
  margin-top: -0.5rem;
}

.forgot-password-link {
  display: inline-block;
  margin-top: 1rem;
  color: #42b983;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-password-link:hover {
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
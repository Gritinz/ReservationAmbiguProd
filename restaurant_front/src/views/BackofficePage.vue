<template>
  <div class="container">
    <h1>Backoffice</h1>
    <button @click="logout">Déconnexion</button>

    <!-- Section Schedules -->
    <h2>Gérer les ouvertures/fermetures exceptionnelles</h2>
    <form @submit.prevent="createSchedule" v-if="canAccessSchedules">
      <!-- Formulaire inchangé -->
      <div>
        <label>Type :</label>
        <select v-model="newSchedule.type" required>
          <option value="open">Ouverture exceptionnelle (dimanche ou lundi)</option>
          <option value="closed">Fermeture exceptionnelle (mardi à samedi)</option>
        </select>
      </div>
      <div>
        <label>Mode :</label>
        <select v-model="mode" required>
          <option value="single">Date précise</option>
          <option value="range">Période</option>
        </select>
      </div>
      <div>
        <label>Date précise ou début de période :</label>
        <VueDatePicker
          v-model="newSchedule.start_date"
          :enable-time-picker="false"
          :disabled-week-days="disabledWeekDays"
          :disabled-dates="disabledExistingDates"
          locale="fr"
          select-text="Sélectionner"
          cancel-text="Annuler"
          placeholder="Sélectionnez une date"
          :min-date="new Date()"
          format="dd/MM/yyyy"
          required
        />
      </div>
      <div v-if="mode === 'range'">
        <label>Fin de période :</label>
        <VueDatePicker
          v-model="newSchedule.end_date"
          :enable-time-picker="false"
          :disabled-week-days="disabledWeekDays"
          :disabled-dates="disabledExistingDates"
          locale="fr"
          select-text="Sélectionner"
          cancel-text="Annuler"
          placeholder="Sélectionnez une date"
          :min-date="newSchedule.start_date || new Date()"
          format="dd/MM/yyyy"
          :required="mode === 'range'"
        />
      </div>
      <div v-if="mode === 'single'">
        <label>Moment :</label>
        <select v-model="newSchedule.moment" required>
          <option value="full_day">Toute la journée</option>
          <option value="lunch">Midi</option>
          <option value="dinner">Soir</option>
        </select>
      </div>
      <button type="submit">Ajouter</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p v-if="!canAccessSchedules && !loadingSchedules" class="error">
      Impossible de charger les horaires. Vérifiez votre connexion ou contactez l'administrateur.
    </p>

    <h3>Horaires exceptionnels</h3>
    <ul v-if="schedules.length > 0">
      <li v-for="schedule in schedules" :key="schedule.id">
        {{ schedule.type === 'open' ? 'Ouverture' : 'Fermeture' }} -
        {{ formatDate(schedule.start_date) }}
        <span v-if="schedule.end_date">au {{ formatDate(schedule.end_date) }}</span>
        <span v-if="schedule.moment">
          ({{ schedule.moment === 'full_day' ? 'Toute la journée' : schedule.moment === 'lunch' ? 'Midi' : 'Soir' }})
        </span>
        <button @click="deleteSchedule(schedule.id)">Supprimer</button>
      </li>
    </ul>
    <p v-else-if="canAccessSchedules && !loadingSchedules">Aucun changement d'horaire trouvé.</p>

    <!-- Section Réservations -->
    <h2>Gérer les réservations</h2>
    <ul v-if="reservations.length > 0">
      <li v-for="reservation in reservations" :key="reservation.id">
        {{ reservation.name }} - {{ formatDate(reservation.date) }} {{ reservation.time }}
        ({{ reservation.party_size }} personnes) - Statut: {{ reservation.status }}
        <button v-if="reservation.status === 'pending'" @click="updateReservation(reservation.id, 'accepted')">Accepter</button>
        <button v-if="reservation.status === 'pending'" @click="updateReservation(reservation.id, 'rejected')">Refuser</button>
      </li>
    </ul>
    <p v-else-if="canAccessReservations && !loadingReservations">Aucune réservation trouvée.</p>
    <p v-else-if="!canAccessReservations && !loadingReservations" class="error">
      Impossible de charger les réservations. Vérifiez votre connexion ou contactez l'administrateur.
    </p>
  </div>
</template>

<script>
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

export default {
  components: { VueDatePicker },
  data() {
    return {
      schedules: [],
      reservations: [],
      newSchedule: {
        type: 'open',
        start_date: null,
        end_date: null,
        moment: 'full_day',
      },
      mode: 'single',
      error: '',
      canAccessSchedules: true,
      canAccessReservations: true,
      loadingSchedules: false,
      loadingReservations: false,
    };
  },
  computed: {
    disabledWeekDays() {
      return this.newSchedule.type === 'open' ? [2, 3, 4, 5, 6] : [0, 1];
    },
    disabledExistingDates() {
      const disabled = new Set();
      this.schedules.forEach(schedule => {
        const start = new Date(schedule.start_date);
        const end = schedule.end_date ? new Date(schedule.end_date) : start;
        let current = new Date(start);
        while (current <= end) {
          disabled.add(current.toISOString().split('T')[0]);
          current.setDate(current.getDate() + 1);
        }
      });
      return Array.from(disabled).map(dateStr => new Date(dateStr));
    }
  },
  async created() {
    await this.fetchSchedules();
    await this.fetchReservations();
  },
  methods: {
    async fetchSchedules() {
      this.loadingSchedules = true;
      try {
        const res = await this.$axios.get('/backoffice/api/schedules/');
        this.schedules = res.data;
      } catch (error) {
        console.error("Erreur lors du chargement des schedules :", error);
        this.canAccessSchedules = false;
      } finally {
        this.loadingSchedules = false;
      }
    },
    async fetchReservations() {
      this.loadingReservations = true;
      try {
        const res = await this.$axios.get('/backoffice/api/reservations/');
        this.reservations = res.data;
      } catch (error) {
        console.error("Erreur lors du chargement des réservations :", error);
        this.canAccessReservations = false;
      } finally {
        this.loadingReservations = false;
      }
    },
    async createSchedule() {
      try {
        this.error = '';

        const payload = {
          type: this.newSchedule.type,
          start_date: this.newSchedule.start_date
            ? this.newSchedule.start_date.toISOString().split('T')[0]
            : null,
          end_date: this.mode === 'range' && this.newSchedule.end_date
            ? this.newSchedule.end_date.toISOString().split('T')[0]
            : null,
          moment: this.mode === 'range'
            ? 'full_day'
            : this.newSchedule.moment,
          mode: this.mode,
        };

        await this.$axios.post('/backoffice/api/schedules/', payload);

        await this.fetchSchedules(); // Recharger les schedules pour mettre à jour les dates désactivées
        this.newSchedule = { type: 'open', start_date: null, end_date: null, moment: 'full_day' };
        this.mode = 'single';
      } catch (error) {
        if (error.response && error.response.data) {
          // Afficher le premier message d'erreur de Django
          this.error = Object.values(error.response.data)[0][0] || 'Erreur lors de la création du schedule.';
          console.error('Erreur détaillée de la création du schedule:', error.response.data);
        } else {
          this.error = 'Erreur lors de la création du schedule.';
          console.error('Erreur Axios:', error);
        }
      }
    },
    async deleteSchedule(id) {
      try {
        await this.$axios.delete(`/backoffice/api/schedules/${id}/`);
        await this.fetchSchedules(); // Recharger les schedules pour mettre à jour les dates désactivées
      } catch (error) {
        console.error('Erreur lors de la suppression du schedule:', error);
        this.error = 'Erreur lors de la suppression du schedule.';
      }
    },
    async updateReservation(id, status) {
      try {
        await this.$axios.patch(`/backoffice/api/reservations/${id}/`, { status });
        await this.fetchReservations();
      } catch (error) {
        console.error('Erreur lors de la mise à jour de la réservation:', error);
        this.error = 'Erreur lors de la mise à jour de la réservation.';
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('fr-FR');
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('is_admin');
      this.$router.push('/login');
    }
  },
};
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
}

button {
  background-color: #42b983;
  border: none;
  padding: 0.75rem 1.2rem;
  color: white;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #3aa876;
}

/* Section formulaire */
form {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

form div {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #555;
}

input,
select {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

input:focus,
select:focus {
  border-color: #42b983;
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

/* Liste des horaires exceptionnels */
h3 {
  margin-top: 2rem;
  color: #444;
}

ul {
  list-style: none;
  padding-left: 0;
}

li {
  background-color: #fff;
  border: 1px solid #eee;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease;
}

li:hover {
  background-color: #f0fbf7;
}

button[type="submit"] {
  margin-top: 1rem;
}

/* Messages d'erreur/succès */
.success,
.error {
  margin-top: 1rem;
  font-weight: bold;
}
.success {
  color: #2e7d32;
}
.error {
  color: #c62828;
}

/* Lien de retour connexion */
.back-to-login {
  display: block;
  margin-top: 1.5rem;
  text-align: center;
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
}
.back-to-login:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 600px) {
  h1 {
    font-size: 1.5rem;
  }

  form {
    padding: 1rem;
  }

  input,
  select {
    font-size: 0.95rem;
  }
}
</style>
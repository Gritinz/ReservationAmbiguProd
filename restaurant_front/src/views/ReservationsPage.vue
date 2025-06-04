<template>
  <div class="container">
    <h1>Réservations de restaurant</h1>
    <h2>Réservations confirmées</h2>
    <ul>
      <li v-for="reservation in confirmedReservations" :key="reservation.id">
        {{ reservation.name }} - {{ reservation.date }} {{ reservation.time }} ({{ reservation.party_size }} personnes)
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      confirmedReservations: [],
    };
  },
  async created() {
    await this.fetchConfirmedReservations();
  },
  methods: {
    async fetchConfirmedReservations() {
      try {
        const response = await this.$axios.get('http://localhost:8000/backoffice/api/reservations/', {
          params: { status: 'accepted' },
        });
        this.confirmedReservations = response.data;
      } catch (error) {
        console.error('Erreur lors du chargement des réservations:', error);
      }
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}
</style>
<script setup>
import welcome from "./components/Welcome.vue"
import register from "./components/Register.vue"
import login from "./components/Login.vue"
import {store} from "./state/user"
</script>

<script>
export default {
   data(){
      return {
         selectedComponent: "welcome",
         store
      }
   },
   methods: {
   changeStep(step){
      this.selectedComponent = step;
   }
  },
  components: {
    welcome,
    register,
    login
  },
  mounted() {
    this.store.user = this.$cookies.isKey("username") ? this.$cookies.get("username") : null;
  }
}
</script>

<template>
  <header>
    <h2>Какой-то аукционный сайт</h2>
  </header>

  <main>
    <component @nextStep="changeStep" :is="selectedComponent"></component>
  </main>
</template>

<style>

</style>

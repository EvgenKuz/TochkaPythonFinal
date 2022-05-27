<script setup>
import Welcome from "./components/Welcome.vue"
import register from "./components/Register.vue"
</script>

<script>
export default {
   data(){
      return {
         selectedComponent: "Welcome"
      }
   },
   methods: {
   changeStep(step){
      this.selectedComponent = step;
   }
  },
  components: {
    Welcome,
    register
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

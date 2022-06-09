<script setup>
import welcome from "./components/Welcome.vue"
import register from "./components/Register.vue"
import login from "./components/Login.vue"
import add_item from "./components/AddItem.vue"
import auction from "./components/Auction.vue"
import personal_page from "./components/PersonalPage.vue"
import {store} from "./state/user"
import { current } from "./state/auction"
</script>

<script>
export default {
   data(){
      return {
         selectedComponent: "welcome",
         store,
         current
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
    login,
    add_item,
    auction,
    personal_page
  },
  mounted() {
    this.store.user = this.$cookies.isKey("username") ? this.$cookies.get("username") : null;
    this.store.is_admin = this.$cookies.isKey("is_admin") ? this.$cookies.get("is_admin") : false;
  }
}
</script>

<template>
  <header>
    <h2>Какой-то аукционный сайт</h2>
  </header>

  <main>
    <component v-if="!current.auctionId" @nextStep="changeStep" :is="selectedComponent"></component>
    <auction v-else></auction>
  </main>
</template>

<style>

</style>

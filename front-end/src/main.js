import { createApp } from "vue";
import VueCookies from 'vue-cookies';
import App from "./App.vue";

const app = createApp(App);
app.use(VueCookies);

app.mount("#app");

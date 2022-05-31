<script>
import {store} from "../state/user"
import { call_method } from "../utils/JsonRpc";
import ServerError from "./errors/ServerError.vue"

export default {
    emits: ["nextStep"],
    data() {
        return {
            store,
            hasError: false,
            error: ""
        }
    },
    methods: {
        changeStep(step) {
            this.$emit("nextStep", step);
        },
        async logout() {
            const resp = await call_method("logout", {});
            
            if ("error" in resp && resp["error"]["code"] !== -32003) {
                this.hasError = true;
                this.error = resp["error"]["message"];
                return;
            }

            this.store.user = null;
            this.$cookies.remove("username");
        }
    },
    components: {ServerError}
}
</script>

<template>
    <div v-if="!store.user">
        <h3>Добро пожаловать!</h3>
        <button @click="changeStep('register')">Зарегистрироваться</button>
        <button @click="changeStep('login')">Войти</button>
    </div>
    <div v-else>
        <h3>Привет, {{store.user}}!</h3>
        <ServerError v-if="hasError">{{error}}</ServerError>
        <button @click="logout">Выйти</button>
    </div>
</template>

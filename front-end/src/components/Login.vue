<script>
import {store} from "../state/user"
import FormError from "./errors/FormError.vue"
import ServerError from "./errors/ServerError.vue"
import { call_method } from "../utils/JsonRpc"

export default {
    emits: ["nextStep"],
    data() {
        return {
            store,
            username: "",
            password: "",
            hasErrors: false,
            errorCode: 0,
            error: ""
        }
    },
    methods: {
        changeStep() {
            this.$emit("nextStep", "welcome");
        },
        async login() {
            if (!this.username || !this.password) {
                this.hasErrors = true;
                return;
            }

            const response = await call_method("login", {
                username: this.username,
                password: this.password,
            });

            if ("error" in response) {
                this.hasErrors = true;
                this.errorCode = response["error"]["code"];
                this.error = response["error"]["message"];
                return;
            }

            this.store.user = this.username;
            this.$cookies.set("username", this.username);
            this.changeStep()
        }
    },
    components: { FormError, ServerError }
}
</script>

<template>
    <h3>Вход:</h3>
    <FormError v-if="hasErrors && errorCode === -32001">{{error}}</FormError>
    <ServerError v-else-if="hasErrors">{{error}}</ServerError>
    <input v-model="username" type="text" placeholder="Имя пользователя">
    <input v-model="password" type="password" placeholder="Пароль">
    <button @click="login">Войти</button>
</template>

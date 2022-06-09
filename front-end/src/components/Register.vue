<script>
import FormError from "./errors/FormError.vue"
import ServerError from "./errors/ServerError.vue"
import {call_method} from "../utils/JsonRpc"
import {store} from "../state/user"

export default {
    emits: ["nextStep"],
    data() {
        return {
            username: "",
            password: "",
            email: "",
            hasErrors: false,
            error: "",
            errorCode: 0,
            store
        };
    },
    methods: {
        changeStep() {
            this.$emit("nextStep", "welcome");
        },
        async send() {
            if (!this.username || !this.password || !this.email) {
                this.hasErrors = true;
                return;
            }

            const response = await call_method("register", {
                username: this.username,
                password: this.password,
                email: this.email
            });

            if ("error" in response) {
                this.hasErrors = true;
                this.error = response["error"]["message"];
                this.errorCode = response["error"]["code"];
                return;
            }

            this.store.user = this.username;
            this.$cookies.set("username", this.username);
            this.changeStep();
        }
    },
    components: { FormError, ServerError }
}
</script>

<template>
    <FormError v-if="hasErrors && errorCode <= -32000 && errorCode >= -32002">{{error}}</FormError>
    <ServerError v-else-if="hasErrors">{{error}}</ServerError>
    <input v-model="username" type="text" placeholder="Имя пользователя">
    <input v-model="password" type="password" placeholder="Пароль">
    <input v-model="email" type="email" placeholder="Почта">
    <button @click="send">Зарегистрироваться</button><br>
    <button @click="changeStep">Назад</button>
</template>
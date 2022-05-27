<script>
import FormError from "./errors/FormError.vue"
import {call_method} from "../utils/JsonRpc"
import {store} from "../state/user"

export default {
    data() {
        return {
            username: "",
            password: "",
            email: "",
            hasErrors: false,
            error: "",
            store
        };
    },
    methods: {
        async send() {
            if (!this.username || !this.password || !this.email) {
                this.hasErrors = true;
                return;
            }

            let response = await call_method("register", {
                username: this.username,
                password: this.password,
                email: this.email
            });

            if ("error" in response) {
                this.hasErrors = true;
                this.error = response["error"]["message"];
                return;
            }
            this.store.user = this.username;
        }
    },
    components: { FormError }
}
</script>

<template>
    <FormError v-if="hasErrors">{{error}}</FormError>
    <input v-model="username" type="text" placeholder="Username">
    <input v-model="password" type="password" placeholder="Password">
    <input v-model="email" type="email" placeholder="Email">
    <button @click="send">Зарегистрироваться</button>
</template>
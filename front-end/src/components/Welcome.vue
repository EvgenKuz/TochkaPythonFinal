<script>
import {store} from "../state/user"

export default {
    data() {
        return {
            store
        }
    },
    methods: {
        changeStep(step) {
            this.$emit("nextStep", step);
        }
    }
}
</script>

<template>
    <div v-if="!store.user">
        <h3>Добро пожаловать!</h3>
        <button @click="changeStep('register')">Зарегистрироваться</button>
        <button @click="changeStep(Login)">Войти</button>
    </div>
    <div v-else>
        <h3>Привет, {{store.user}}!</h3>
    </div>
</template>

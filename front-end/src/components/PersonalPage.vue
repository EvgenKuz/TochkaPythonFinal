<script>
import ServerError from "./errors/ServerError.vue"
import { store, forgetUser } from "../state/user";
import { current } from "../state/auction";
import { call_method } from "../utils/JsonRpc";

export default {
    emits: ["nextStep"],
    data() {
        return {
            store,
            current,
            bets: [],
            hasErrors: false,
            error: "",
            email: "",
        }
    },
    methods: {
        selectAuction(auctionId) {
            this.current.auctionId = auctionId;
        },
        changeStep() {
            this.$emit("nextStep", "welcome");
        },
        async getBets() {
            const resp = await call_method("get_user_bets", {});

            if ("error" in resp) {
                this.hasErros = true;
                this.error = resp.error.message;
                return;
            }
            
            this.hasErrors = false;
            this.bets = resp.result;
        },
        async getUserInfo() {
            const resp = await call_method("get_user_info", {})

            if ("error" in resp) {
                this.hasErrors = true;
                this.error = resp.error.message
                if (resp.error.code == -32003)
                    forgetUser(this);
                return;
            }

            this.email = resp.result.email;
            this.store.is_admin = resp.result.is_admin;
            this.$cookies.set("is_admin", resp.result.is_admin);
        }
    },
    components: { ServerError },
    async created() {
        await this.getBets();
        await this.getUserInfo();
    }
}
</script>

<template>
<button @click="changeStep">Назад</button>
<p>Вы: {{store.user}}</p>
<p>Ваш email: {{email}}</p>
<p>Админ: <span v-if="store.is_admin">Да</span><span v-else>Нет</span></p>
<ServerError v-if="hasErrors">{{error}}</ServerError>
<h3>Ваши аукционы:</h3>
<p>
    <ul>
        <li v-for="bet in bets" @click="selectAuction(bet.auction)">
            <span>Аукцион: {{bet.name}}</span>
            <span>Ставка: {{bet.price}}</span>
        </li>
    </ul>
</p>
</template>

<style>
</style>
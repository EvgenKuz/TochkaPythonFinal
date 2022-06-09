<script>
import ServerError from "./errors/ServerError.vue"
import { store } from "../state/user";
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
            error: ""
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
        }
    },
    components: { ServerError },
    async created() {
        await this.getBets()
    }
}
</script>

<template>
<button @click="changeStep">Назад</button>
<p>Вы: {{store.user}}</p>
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
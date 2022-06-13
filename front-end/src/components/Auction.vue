<script>
import AuctionError from "./errors/AuctionError.vue"
import BetError from "./errors/BetError.vue"
import { current } from "../state/auction"
import { call_method } from "../utils/JsonRpc"
import { store } from "../state/user"

export default {
    data() {
        return {
            store,
            current,
            name: "",
            starting_price: 0,
            picture: "",
            description: "",
            end_of_auction: "",
            allowed: true,
            hasErrors: false,
            hasErrorsBet: false,
            error: "",
            bets: [],
            bet: null,
            canMakeBets: true,
            winner: null
        }
    },
    methods: {
        changeStep() {
            this.current.auctionId = null;
        },
        checkIfCanMakeBet() {
            this.canMakeBets = (new Date() < new Date(this.end_of_auction)) && this.allowed;
            return this.canMakeBets;
        },
        async getBets() {
            await this.getWinner()
            this.checkIfCanMakeBet();
            const resp = await call_method("get_auction_bets", { id: this.current.auctionId });

            if ("error" in resp) {
                this.hasErrors = true;
                this.error = resp["error"]["message"];
                return;
            }

            this.bets = resp.result;
        },
        async makeBet() {
            if (!this.checkIfCanMakeBet()) 
                return;
            if (!this.bet || this.bet <= this.starting_price) {
                this.hasErrorsBet = true;
                this.error = "Ставка ниже начальной цены";
                return;
            }

            const resp = await call_method("bet", {
                id: this.current.auctionId,
                price: this.bet
            });

            if ("error" in resp) {
                this.hasErrorsBet = true;
                this.error = resp.error.message;
                return;
            }

            this.hasErrors = false;
            await this.getBets();
        },
        async getWinner() {
            const resp = await call_method("get_auction_winner", {id: this.current.auctionId})

            if ("error" in resp && resp.error.code === -32007)
                return;
            if ("error" in resp && resp.error.code === -32009) {
                this.winner = "Никто не победил";
                this.allowed = false;
                return;
            }
            if ("error" in resp) {
                this.hasErrorsBet = true;
                this.error = resp.error.message;
                return;
            }

            this.winner = resp.result;
            this.allowed = false;
        },
        async stopAuction() {
            const resp = await call_method("change_item_status", {id: this.current.auctionId})

            if ("error" in resp) {
                this.hasErrorsBet = true;
                this.error = resp.error.message;
                return;
            }

            this.canMakeBets = false;
            await this.getWinner();
        }
    },
    components: {AuctionError, BetError},
    async created() {
        const resp = await call_method("get_item", { id: this.current.auctionId });

        if ("error" in resp) {
            this.hasErrors = true;
            this.error = resp["error"]["message"];
            return;
        }
        const result = resp["result"];

        this.name = result["name"];
        this.starting_price = result["starting_price"];
        this.picture = result["picture"];
        this.description = result["description"];
        this.end_of_auction = result["end_of_auction"];
        this.allowed = result["allowed"];

        this.checkIfCanMakeBet();
        await this.getBets();
    },
}
</script>

<template>
<button @click="changeStep">Назад</button>
<AuctionError v-if="hasErrors">{{error}}</AuctionError>
<div v-else>
    <img :src="picture" width="500"><br>
    <span>Аукцион: {{name}}</span><br>
    <span>Начальная цена: {{starting_price}} руб.</span><br>
    <span v-if="canMakeBets">Заканчивается: {{new Date(end_of_auction).toLocaleString("ru-RU")}}</span>
    <span v-else>Победитель: {{winner}}</span><br>
    <span>Описание: <p>{{description}}</p></span><br>
    <BetError v-if="hasErrorsBet">{{error}}</BetError><br>
    <div v-if="canMakeBets">
        <input v-model="bet" placeholder="Ваша ставка">
        <button @click="makeBet">Сделать ставку</button>
    </div><br>
    <h3>Ставки:</h3>
    <button v-if="canMakeBets" @click="getBets">Обновить ставки</button>
    <button v-if="canMakeBets && store.is_admin" @click="stopAuction">Закончить аукцион</button>
    <ul>
        <li v-for="b in bets">
            <span>Сделавший ставку: {{b.username}}</span>
            <span>Ставка: {{b.price}}</span>
        </li>
    </ul>
</div>

</template>

<style>
</style>
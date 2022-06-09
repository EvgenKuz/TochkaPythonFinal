<script>
import { store } from "../state/user"
import { current } from "../state/auction"
import ServerError from "./errors/ServerError.vue"
import { call_method } from "../utils/JsonRpc"

export default {
    data() {
        return {
            current,
            store,
            hasErrors: false,
            error: "",
            errorCode: 0,
            auctions: []
        }
    },
    methods: {
        async getAuctions() {
            const resp = await call_method("get_items", {});

            if ("error" in resp) {
                this.hasErrors = true;
                this.errorCode = resp["error"]["code"];
                this.error = resp["error"]["message"];

                if (this.errorCode == -32004) {
                    this.store.is_admin = false;
                    this.store.user = null;
                    this.$cookies.remove("username");
                    this.$cookies.remove("is_admin");
                }
            }
            else {
                this.auctions = resp["result"];
            }
        },
        selectAuction(auctionId) {
            this.current.auctionId = auctionId;
        }
    },
    components: {ServerError},
    async mounted() {
        await this.getAuctions();
    }
}
</script>

<template>
<ServerError v-if="hasErrors">{{error}}</ServerError>
<ul>
    <li v-for="auction in auctions" @click="selectAuction(auction.id)">
        <img :src="auction.picture" width="100">
        <span>{{auction.name}}</span>
        <span>Начальная цена: {{auction.starting_price}} руб.</span>
        <span>Заканчивается: {{new Date(auction.end_of_auction).toLocaleString("ru-RU")}}</span>
    </li>
</ul>
</template>

<style>
ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
}
li {
    border: 1px solid black;
    margin-top: 10px;
    padding: 5px;
}
li:hover {
    background-color: grey;
}
li > span {
    margin-left: 10px;

}
</style>
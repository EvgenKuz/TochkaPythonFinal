<script>
import { call_method } from "../utils/JsonRpc";
import ServerError from "./errors/ServerError.vue"
import SimplePicker from "simplepicker";

export default {
    emits: ["nextStep"],
    data() {
        return {
            name: null,
            starting_price: 0.0,
            picture: "",
            description: "",
            hasErrors: false,
            error: null,
            datetime: null,
            isoStr: ""
        }
    },
    methods: {
        changeStep() {
            this.$emit("nextStep", "welcome");
        },
        async send(){
            if (!this.name || !typeof(this.starting_price) == Number || 
            !this.picture || !this.picture) {
                this.hasErrors = true;
                return;
            }

            const resp = await call_method("add_item", {
                name: this.name,
                starting_price: this.starting_price,
                picture: this.picture,
                description: this.description,
                end_of_auction: this.isoStr
            })

            if ("error" in resp) {
                this.hasErrors = true;
                this.error = resp["error"]["message"];
                return;
            }

            this.changeStep()
        },
        dtHandler(date, readableDate) {
            const offset = new Date().getTimezoneOffset();
            date.setTime(date.getTime() - offset * 60 * 1000)
            this.isoStr = date.toISOString().slice(0, -1);
        },
        openDateSelector() {
            this.datetime.open();
        }
    },
    components: {ServerError},
    mounted() {
        this.datetime = new SimplePicker('#datetime', {zIndex: 10})
        this.datetime.on("submit", this.dtHandler);
    }
}
</script>

<template>
<h3>Добавить аукцион</h3>
<ServerError v-if="hasErrors">{{error}}</ServerError>
<input v-model="name" type="text" placeholder="Название лота">
<input v-model="starting_price" type="number" placeholder="Начальная цена">
<input v-model="picture" type="url" placeholder="URL картинки">
<textarea v-model="description" placeholder="Описание лота"></textarea>
<button id="datetime" @click="openDateSelector">Выбрать время завершения аукциона</button>
<button @click="send">Отправить</button><br>

<button @click="changeStep">Назад</button>
</template>

<style>
@import url("simplepicker/dist/simplepicker.css");
</style>
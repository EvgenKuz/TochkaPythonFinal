<script>
export default {
    methods: {
        changeStep(step) {
            this.$emit("nextStep", step);
        }
    }
}
</script>

<template>
    <h3>Добро пожаловать!</h3>
</template>

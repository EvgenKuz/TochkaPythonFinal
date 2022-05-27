<script>
</script>

<template>
<div class="error">
    <span>Вы не правильно заполнили поля!</span>
    <span><slot></slot></span>
</div>
</template>

<style>
.error {
    background-color: darkred;
}
</style>
<script>
</script>

<template>
<div class="error">
    <span>Перепроверьте заполненые поля!</span>
    <span><slot></slot></span>
</div>
</template>

<style>
.error {
    color: white;
    background-color: darkred;
}
</style>
<template>
  <IndexPage/>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import IndexPage from './components/IndexPage.vue';

export default defineComponent({
  name: 'App',
  components: {
    IndexPage
  }
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

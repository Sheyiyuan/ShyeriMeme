<template>
  <div class="app">
    <main class="main">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>ShyeriMeme - 橘雪莉表情包生成器</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
// App组件逻辑
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  color: #333;
  line-height: 1.6;
  background-color: #f5f5f5;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main {
  flex: 1;
  padding: 20px 0;
}

.footer {
  background-color: #ecf0f1;
  text-align: center;
  padding: 15px 0;
  color: #7f8c8d;
}
</style>
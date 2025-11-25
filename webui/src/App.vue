<template>
  <div class="app">
    <header class="header">
      <div class="header-right">
        <a href="https://github.com/Sheyiyuan/ShyeriMeme" target="_blank" class="github-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
        </a>
      </div>
    </header>
    
    <main class="main">
      <router-view />
    </main>
    
    <footer class="footer">
      <p><a href="https://github.com/Sheyiyuan/ShyeriMeme">Sheyiyuan - 橘雪莉表情包生成器</a></p>
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

.header {
  position: relative;
  padding: 10px 20px;
}

.header-right {
  position: absolute;
  top: 10px;
  right: 20px;
}

.github-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #333;
  text-decoration: none;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.github-link:hover {
  background-color: rgba(0, 0, 0, 0.1);
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
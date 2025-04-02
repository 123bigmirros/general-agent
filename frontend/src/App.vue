<template>
  <header class="app-header">
    <div class="container">
      <h1>Agent游戏系统</h1>
    </div>
  </header>
  
  <main class="container">
    <router-view />
  </main>
  
  <footer class="app-footer">
    <div class="container">
      <p>© 2025 Agent游戏系统</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.app-footer {
  background-color: #34495e;
  color: #ecf0f1;
  padding: 1rem 0;
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
}
</style> 
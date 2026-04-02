<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">📊 AI套定额系统</div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/quotas">定额库</router-link>
        <router-link to="/history">历史记录</router-link>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F3F4F6; color: #1F2937; }
#app { min-height: 100vh; }
.navbar { background: #1F2937; color: #fff; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.nav-brand { font-size: 20px; font-weight: 700; }
.nav-links { display: flex; gap: 24px; }
.nav-links a { color: #D1D5DB; text-decoration: none; font-weight: 500; transition: color 0.2s; }
.nav-links a:hover, .nav-links a.router-link-active { color: #fff; }
main { padding: 0; }
</style>

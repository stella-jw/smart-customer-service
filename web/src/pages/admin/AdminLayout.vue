<template>
  <div class="admin-layout">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>管理后台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/bots" class="nav-item" :class="{ active: $route.path === '/admin/bots' }">
          <span class="nav-icon">🤖</span>
          <span>智能体管理</span>
        </router-link>
        <router-link to="/admin/knowledge" class="nav-item" :class="{ active: $route.path === '/admin/knowledge' }">
          <span class="nav-icon">📚</span>
          <span>知识库管理</span>
        </router-link>
        <router-link to="/admin/qa" class="nav-item" :class="{ active: $route.path === '/admin/qa' }">
          <span class="nav-icon">❓</span>
          <span>Q&A管理</span>
        </router-link>
        <router-link to="/admin/config" class="nav-item" :class="{ active: $route.path === '/admin/config' }">
          <span class="nav-icon">⚙️</span>
          <span>智能体配置</span>
        </router-link>
        <router-link to="/admin/teams" class="nav-item" :class="{ active: $route.path === '/admin/teams' }">
          <span class="nav-icon">👥</span>
          <span>团队管理</span>
        </router-link>
        <router-link to="/admin/bot-access" class="nav-item" :class="{ active: $route.path === '/admin/bot-access' }">
          <span class="nav-icon">🔐</span>
          <span>机器人权限</span>
        </router-link>
      </nav>
    </aside>

    <!-- 右侧内容 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="top-bar-left">
          <BotSwitcher v-if="$route.path === '/admin/config'" />
        </div>
        <div class="top-bar-right">
          <span class="admin-name">管理员</span>
          <button @click="logout" class="logout-btn">退出</button>
        </div>
      </header>

      <!-- 内容区 -->
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { auth } from '@/api'
import BotSwitcher from '@/components/BotSwitcher.vue'

const router = useRouter()

function logout() {
  auth.clear()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

/* 左侧导航 - 固定定位 */
.sidebar {
  width: 220px;
  background: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-nav {
  padding: 16px 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.2s;
  gap: 12px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left: 3px solid #4a90d9;
}

.nav-icon {
  font-size: 18px;
}

/* 右侧主内容 - 留出左侧导航宽度 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  min-height: 100vh;
  position: fixed;
  left: 220px;
  right: 0;
  top: 0;
  bottom: 0;
}

/* 顶部栏 */
.top-bar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.top-bar-left {
  display: flex;
  align-items: center;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-name {
  color: #666;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #e0e0e0;
}

/* 内容区 */
.content-area {
  flex: 1;
  padding: 10px 36px;
  overflow-y: auto;
}
</style>

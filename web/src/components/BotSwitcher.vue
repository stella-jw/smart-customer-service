<template>
  <div class="bot-switcher" v-if="hasBots">
    <div class="switcher-trigger" @click="toggleDropdown">
      <span class="bot-name">{{ currentBot?.name || '选择机器人' }}</span>
      <span class="arrow" :class="{ open: isOpen }">▼</span>
    </div>
    <div class="dropdown" v-if="isOpen">
      <div
        v-for="bot in botList"
        :key="bot.id"
        class="dropdown-item"
        :class="{ active: bot.id === currentBotId }"
        @click="selectBot(bot.id)"
      >
        <span class="bot-name">{{ bot.name }}</span>
        <span class="bot-industry">{{ industryText[bot.industry_type] || bot.industry_type }}</span>
      </div>
    </div>
  </div>
  <div v-else class="no-bot">暂无机器人</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useBotStore } from '@/stores/botStore'

const { currentBotId, currentBot, botList, hasBots, fetchBots, switchBot } = useBotStore()

const isOpen = ref(false)

const industryText: Record<string, string> = {
  ecommerce: '电商',
  medical: '医疗',
  saas: 'SaaS',
  it: 'IT服务',
  general: '通用'
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function selectBot(botId: string) {
  switchBot(botId)
  isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.bot-switcher')) {
    isOpen.value = false
  }
}

onMounted(() => {
  fetchBots()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.bot-switcher {
  position: relative;
}

.switcher-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.switcher-trigger:hover {
  background: #e8e8e8;
}

.bot-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.arrow {
  font-size: 10px;
  color: #999;
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  z-index: 100;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-item.active {
  background: #e8f4fd;
}

.dropdown-item .bot-name {
  font-weight: 500;
}

.dropdown-item .bot-industry {
  font-size: 12px;
  color: #999;
}

.no-bot {
  color: #999;
  font-size: 14px;
}
</style>

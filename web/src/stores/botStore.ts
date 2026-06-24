import { ref, computed, watch } from 'vue'
import { adminApi } from '@/api'

const BOT_LIMIT = 5

// 状态
const currentBotId = ref<string>(localStorage.getItem('current_bot_id') || '')
const botList = ref<any[]>([])
const loading = ref(false)

// 持久化 currentBotId
watch(currentBotId, (newId) => {
  if (newId) {
    localStorage.setItem('current_bot_id', newId)
  } else {
    localStorage.removeItem('current_bot_id')
  }
})

export function useBotStore() {
  const currentBot = computed(() => {
    return botList.value.find(bot => bot.id === currentBotId.value) || null
  })

  const isAtLimit = computed(() => botList.value.length >= BOT_LIMIT)

  const hasBots = computed(() => botList.value.length > 0)

  async function fetchBots() {
    loading.value = true
    try {
      const bots = await adminApi.getBots()
      botList.value = bots

      // 如果没有当前选中且有机器人，选择第一个
      if (!currentBotId.value && bots.length > 0) {
        currentBotId.value = bots[0].id
      }

      // 如果当前选中的被删了，重置
      if (currentBotId.value && !bots.find(b => b.id === currentBotId.value)) {
        currentBotId.value = bots[0]?.id || ''
      }
    } catch (e) {
      console.error('Failed to fetch bots:', e)
    } finally {
      loading.value = false
    }
  }

  function switchBot(botId: string) {
    currentBotId.value = botId
  }

  async function createBot(data: { name: string; industry_type: string; description?: string }) {
    const newBot = await adminApi.createBot(data)
    await fetchBots()
    return newBot
  }

  async function deleteBot(botId: string) {
    const res = await fetch(`/api/admin/bots/${botId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` }
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '删除失败')
    }
    await fetchBots()
  }

  return {
    // 状态
    currentBotId,
    currentBot,
    botList,
    loading,
    // 计算属性
    isAtLimit,
    hasBots,
    BOT_LIMIT,
    // 方法
    fetchBots,
    switchBot,
    createBot,
    deleteBot
  }
}

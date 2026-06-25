import { ref, computed, watch } from 'vue'
import { adminApi, userApi, auth } from '@/api'

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

  // 判断是否为匿名用户
  const isAnonymous = computed(() => auth.isAnonymous())

  async function fetchBots() {
    loading.value = true
    try {
      let bots

      // 匿名用户和已登录用户使用不同的 API
      if (auth.isAnonymous()) {
        // 匿名用户通过 /api/bots 获取（后端会返回默认机器人）
        const res = await fetch(`/api/bots`)
        bots = await res.json()
      } else {
        // 已登录用户通过 /api/users/available-bots 获取
        bots = await userApi.getAvailableBots()
      }

      botList.value = bots || []

      // 如果没有当前选中，优先选择默认机器人，否则选择第一个
      if (!currentBotId.value && bots && bots.length > 0) {
        const defaultBot = bots.find((bot: any) => bot.is_default)
        currentBotId.value = defaultBot?.id || bots[0].id
      }

      // 如果当前选中的被删了，优先选择默认机器人，否则选择第一个
      if (currentBotId.value && !bots?.find((b: any) => b.id === currentBotId.value)) {
        const defaultBot = bots?.find((bot: any) => bot.is_default)
        currentBotId.value = defaultBot?.id || bots?.[0]?.id || ''
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
    await adminApi.deleteBot(botId)
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
    isAnonymous,
    BOT_LIMIT,
    // 方法
    fetchBots,
    switchBot,
    createBot,
    deleteBot
  }
}

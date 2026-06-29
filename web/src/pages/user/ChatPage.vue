<template>
  <div class="chat-page">
    <div class="chat-window">
      <div class="chat-header">
        <span class="bot-name">{{ botName }}</span>
        <BotSwitcher />
        <span class="session-info">{{ sessionId }}</span>
      </div>

      <div class="messages" ref="messagesRef">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', msg.isFromUser ? 'user' : 'bot']"
        >
          <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
          <div class="message-meta">
            <span v-if="msg.source && !msg.isFromUser" class="source-tag">
              {{ getSourceLabel(msg.source) }}
            </span>
            <span class="time">{{ formatTime(msg.timestamp) }}</span>
          </div>
        </div>

        <div v-if="loading" class="message bot">
          <div class="message-content loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          :disabled="loading"
        />
        <button @click="sendMessage" :disabled="loading || !inputMessage.trim()">
          发送
        </button>
      </div>
    </div>

    <!-- Rating Modal -->
    <div v-if="showRating" class="modal-overlay" @click.self="showRating = false">
      <div class="rating-modal">
        <h3>评价回答</h3>
        <p class="question">您对我的回答满意吗？</p>

        <div class="rating-stars">
          <span
            v-for="star in 5"
            :key="star"
            :class="['star', { active: star <= rating }]"
            @click="rating = star"
          >
            ★
          </span>
        </div>

        <div class="rating-actions">
          <button class="skip-btn" @click="skipRating">跳过</button>
          <button class="submit-btn" @click="submitRating" :disabled="rating === 0">
            提交
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, onUnmounted, computed, watch } from 'vue'
import { marked } from 'marked'
import { chatApi, auth } from '@/api'
import BotSwitcher from '@/components/BotSwitcher.vue'
import { useBotStore } from '@/stores/botStore'

// 配置 marked 选项
marked.setOptions({
  breaks: true,  // 允许 GFM 换行符 (\n) 转换为 <br>
  gfm: true      // 启用 GitHub  flavored markdown
})

// 渲染 Markdown 内容的函数
function renderMarkdown(content: string): string {
  return marked.parse(content) as string
}

const botStore = useBotStore()
const botId = computed(() => botStore.currentBotId.value || null)
const botName = computed(() => {
  // Would need to fetch bot name - for now use default
  return '智能客服'
})
const sessionId = ref(generateSessionId())
const isLoggedIn = computed(() => auth.isLoggedIn())

function generateSessionId() {
  const id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  localStorage.setItem('session_id', id)
  return id
}

function resetConversation() {
  messages.splice(0, messages.length)
  sessionId.value = generateSessionId()
  currentConversationId.value = ''
  ratingCompleted.value = false
  hideRating()
}

// 监听机器人切换，清空对话开始新的会话
watch(() => botStore.currentBotId, (newBotId, oldBotId) => {
  if (newBotId && newBotId !== oldBotId && messages.length > 0) {
    resetConversation()
  }
})

interface Message {
  id: string
  content: string
  isFromUser: boolean
  source: string
  timestamp: Date
}

const messages = reactive<Message[]>([])
const inputMessage = ref('')
const loading = ref(false)
const showRating = ref(false)
const currentConversationId = ref('')
const rating = ref(0)
const messagesRef = ref<HTMLElement | null>(null)
const lastUserActivity = ref<number>(Date.now())
const ratingCompleted = ref(false) // 当前会话是否已完成评价
let ratingCheckTimer: number | null = null

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || loading.value) return

  // Reset activity timer when user sends message
  lastUserActivity.value = Date.now()
  ratingCompleted.value = false // 用户发送新消息，重置评价状态
  hideRating()

  messages.push({
    id: `user_${Date.now()}`,
    content: text,
    isFromUser: true,
    source: 'user',
    timestamp: new Date()
  })

  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const data = await chatApi.send({
      bot_id: botId.value || undefined,
      session_id: sessionId.value,
      message: text
    })

    messages.push({
      id: data.conversation_id,
      content: data.response,
      isFromUser: false,
      source: data.source,
      timestamp: new Date()
    })

    currentConversationId.value = data.conversation_id
  } catch (error) {
    console.error('Chat error:', error)
    messages.push({
      id: `error_${Date.now()}`,
      content: '抱歉，发生了错误，请稍后重试。',
      isFromUser: false,
      source: 'error',
      timestamp: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

async function submitRating() {
  if (rating.value === 0) return
  try {
    await chatApi.rate(currentConversationId.value, rating.value)
  } catch { /* ignore */ }
  showRating.value = false
  ratingCompleted.value = true
  rating.value = 0
}

function skipRating() {
  showRating.value = false
  ratingCompleted.value = true
  rating.value = 0
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function getSourceLabel(source: string) {
  const labels: Record<string, string> = {
    'qa': 'QA匹配',
    'rag': '知识库',
    'llm': 'AI生成',
    'fallback': '兜底回复'
  }
  return labels[source] || ''
}

function formatTime(date: Date) {
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function checkInactivity() {
  const INACTIVITY_TIMEOUT = 5 * 60 * 1000 // 5 minutes
  if (Date.now() - lastUserActivity.value >= INACTIVITY_TIMEOUT) {
    if (!showRating.value && currentConversationId.value && !ratingCompleted.value) {
      showRating.value = true
    }
  }
}

function hideRating() {
  showRating.value = false
}

async function loadHistory() {
  try {
    const data = await chatApi.history(sessionId.value, botId.value || '')
    messages.splice(0, messages.length)
    data.messages.forEach((msg: Message) => {
      messages.push({
        ...msg,
        isFromUser: msg.is_from_user,
        timestamp: new Date(msg.timestamp)
      })
    })
  } catch { /* ignore */ }
}

onMounted(async () => {
  // Initialize bot selection (botStore handles anonymous vs logged-in)
  await botStore.fetchBots()
  loadHistory()
  // Check inactivity every 30 seconds
  ratingCheckTimer = window.setInterval(checkInactivity, 30000)
})

onUnmounted(() => {
  if (ratingCheckTimer) {
    clearInterval(ratingCheckTimer)
  }
})
</script>

<style scoped>
.chat-page {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
}

.chat-window {
  width: 800px;
  max-width: 90vw;
  height: 90vh;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 20px;
  background: #4a90d9;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-info {
  font-size: 12px;
  opacity: 0.8;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  text-align: left;
}

.message.user {
  align-self: flex-end;
  background: #4a90d9;
  color: white;
  border-bottom-right-radius: 4px;
}

/* 用户消息中的 Markdown 样式 */
.message.user :deep(h1),
.message.user :deep(h2),
.message.user :deep(h3),
.message.user :deep(h4) {
  color: white;
}
.message.user :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}
.message.user :deep(pre) {
  background: rgba(255, 255, 255, 0.2);
}
.message.user :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.5);
  color: rgba(12, 111, 41, 0.9);
}

.message.bot {
  align-self: flex-start;
  background: #f0f0f0;
  color: #333;
  border-bottom-left-radius: 4px;
}

/* Markdown 内容样式 */
.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3),
.message-content :deep(h4) {
  margin: 0.5em 0;
  font-weight: 600;
}
.message-content :deep(h1) { font-size: 1.3em; }
.message-content :deep(h2) { font-size: 1.1em; }
.message-content :deep(h3) { font-size: 1em; }

.message-content :deep(p) {
  margin: 0.5em 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.message-content :deep(li) {
  margin: 0.25em 0;
}

.message-content :deep(code) {
  background: rgba(128, 128, 128, 0.2);
  color: #2e7d32;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.message-content :deep(pre) {
  background: rgba(128, 128, 128, 0.2);
  color: #2e7d32;
  padding: 0.5em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(em) {
  font-style: italic;
}

.message-content :deep(blockquote) {
  border-left: 3px solid #0c561e;
  margin: 0.5em 0;
  padding-left: 1em;
  color: #666;
}

.message-meta {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  font-size: 12px;
  opacity: 0.7;
}

.source-tag {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.loading { display: flex; gap: 4px; padding: 16px 20px; }
.dot {
  width: 8px; height: 8px; background: #999; border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}
.dot:nth-child(1) { animation-delay: 0s; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input {
  display: flex;
  padding: 16px;
  border-top: 1px solid #eee;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.chat-input input:focus { border-color: #4a90d9; }

.chat-input button {
  padding: 12px 24px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.chat-input button:disabled { background: #ccc; cursor: not-allowed; }

/* Rating Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.rating-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  width: 320px;
}

.rating-modal h3 { margin: 0 0 12px 0; }
.question { color: #666; margin-bottom: 16px; }

.rating-stars { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; }
.star { font-size: 32px; color: #ddd; cursor: pointer; }
.star.active { color: #ffc107; }

.rating-actions { display: flex; gap: 12px; justify-content: center; }

.skip-btn, .submit-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.skip-btn { background: none; border: 1px solid #ddd; color: #666; }
.submit-btn { background: #4a90d9; border: none; color: white; }
.submit-btn:disabled { background: #ccc; }
</style>

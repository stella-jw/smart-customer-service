<template>
  <div class="history-page">
    <div class="history-header">
      <h2>对话历史</h2>
      <button @click="clearHistory" class="clear-btn">清空历史</button>
    </div>

    <div class="sessions-list">
      <div v-if="sessions.length === 0" class="empty-state">
        <p>暂无对话历史</p>
      </div>

      <div v-for="session in sessions" :key="session.sessionId" class="session-card">
        <div class="session-info">
          <span class="session-id">{{ session.sessionId }}</span>
          <span class="session-time">{{ formatDate(session.updatedAt) }}</span>
        </div>
        <div class="session-preview">{{ session.lastMessage }}</div>
        <button @click="viewSession(session.sessionId)" class="view-btn">查看详情</button>
      </div>
    </div>

    <!-- Session Detail Modal -->
    <div v-if="selectedSession" class="modal-overlay" @click.self="selectedSession = null">
      <div class="session-modal">
        <div class="modal-header">
          <h3>会话详情</h3>
          <button @click="selectedSession = null" class="close-btn">×</button>
        </div>
        <div class="messages-list">
          <div
            v-for="msg in sessionMessages"
            :key="msg.id"
            :class="['message', msg.isFromUser ? 'user' : 'bot']"
          >
            <div class="message-content">{{ msg.content }}</div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { chatApi } from '@/api'

interface Session {
  sessionId: string
  lastMessage: string
  updatedAt: Date
}

interface Message {
  id: string
  content: string
  isFromUser: boolean
  timestamp: Date
}

const botId = ref<string | null>(localStorage.getItem('current_bot_id') || null)
const sessions = ref<Session[]>([])
const selectedSession = ref<string | null>(null)
const sessionMessages = ref<Message[]>([])

async function loadSessions() {
  // 简化实现：从 localStorage 获取历史 session IDs
  const sessionIds = JSON.parse(localStorage.getItem('chat_sessions') || '[]')
  sessions.value = sessionIds.map((id: string) => ({
    sessionId: id,
    lastMessage: '查看详情...',
    updatedAt: new Date()
  }))
}

async function viewSession(sessionId: string) {
  selectedSession.value = sessionId
  try {
    const data = await chatApi.history(sessionId, botId.value || '')
    sessionMessages.value = data.messages.map((m: Message) => ({
      ...m,
      isFromUser: m.is_from_user,
      timestamp: new Date(m.timestamp)
    }))
  } catch {
    sessionMessages.value = []
  }
}

function clearHistory() {
  if (confirm('确定要清空所有对话历史吗？')) {
    localStorage.removeItem('chat_sessions')
    localStorage.removeItem('session_id')
    sessions.value = []
  }
}

function formatDate(date: Date) {
  return new Date(date).toLocaleDateString('zh-CN')
}

function formatTime(date: Date) {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => { loadSessions() })
</script>

<style scoped>
.history-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.history-header h2 { margin: 0; }

.clear-btn {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.sessions-list { display: flex; flex-direction: column; gap: 16px; }

.session-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.session-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.session-id { font-weight: 500; color: #333; }
.session-time { color: #999; font-size: 12px; }
.session-preview { color: #666; margin-bottom: 12px; }

.view-btn {
  padding: 6px 12px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
  background: white;
  border-radius: 12px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.session-modal {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 { margin: 0; }

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 10px;
}

.message.user {
  align-self: flex-end;
  background: #4a90d9;
  color: white;
}

.message.bot {
  align-self: flex-start;
  background: #f0f0f0;
  color: #333;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}
</style>

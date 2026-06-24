<template>
  <div class="qa-page">
    <div class="header">
      <h1>QA对管理</h1>
      <button @click="openAddModal()" class="add-btn">+ 添加QA</button>
    </div>

    <div class="filters">
      <select v-model="filterBotId" @change="loadQA" class="filter-select">
        <option value="">全部机器人</option>
        <option v-for="bot in botList" :key="bot.id" :value="bot.id">
          {{ bot.name }}
        </option>
      </select>
      <input v-model="searchQuery" type="text" placeholder="搜索问题或答案..." class="search-input" />
    </div>

    <div class="qa-list">
      <div v-for="qa in filteredQA" :key="qa.id" class="qa-card">
        <div class="qa-content">
          <div class="qa-question"><span class="label">Q:</span> {{ qa.question }}</div>
          <div class="qa-answer"><span class="label">A:</span> {{ qa.answer }}</div>
        </div>
        <div class="qa-meta">
          <span v-if="qa.category" class="tag">{{ qa.category }}</span>
          <span class="bot-tag" v-if="filterBotId === ''">{{ getBotName(qa.bot_id) }}</span>
          <span class="stats">使用 {{ qa.usage_count }} 次</span>
        </div>
        <div class="qa-actions">
          <button @click="openEditModal(qa)" class="edit-btn">编辑</button>
          <button @click="confirmDelete(qa)" class="delete-btn">删除</button>
        </div>
      </div>

      <div v-if="filteredQA.length === 0" class="empty-state">
        <p>暂无QA对，请添加开始构建问答库</p>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingQA ? '编辑QA' : '添加QA' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group" v-if="!editingQA">
            <label>选择机器人</label>
            <select v-model="formData.bot_id" required>
              <option value="">请选择机器人</option>
              <option v-for="bot in botList" :key="bot.id" :value="bot.id">
                {{ bot.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>问题 *</label>
            <textarea v-model="formData.question" rows="3" placeholder="请输入常见问题"></textarea>
          </div>
          <div class="form-group">
            <label>答案 *</label>
            <textarea v-model="formData.answer" rows="5" placeholder="请输入标准回答"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <input v-model="formData.category" type="text" placeholder="如：产品咨询" />
            </div>
            <div class="form-group">
              <label>关键词</label>
              <input v-model="formData.keywords" type="text" placeholder="逗号分隔" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button class="submit-btn" @click="submitQA" :disabled="!formData.question || !formData.answer || (!editingQA && !formData.bot_id)">
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-content confirm">
        <h3>确认删除</h3>
        <p>确定要删除这条QA吗？</p>
        <div class="confirm-actions">
          <button class="cancel-btn" @click="deleteTarget = null">取消</button>
          <button class="delete-btn" @click="deleteQA">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useBotStore } from '@/stores/botStore'

const { botList, fetchBots, currentBotId } = useBotStore()

interface QA {
  id: string
  bot_id: string
  question: string
  answer: string
  keywords?: string
  category?: string
  usage_count: number
  satisfaction_rate?: number
}

const qaPairs = ref<QA[]>([])
const searchQuery = ref('')
const filterBotId = ref('')
const showModal = ref(false)
const editingQA = ref<QA | null>(null)
const deleteTarget = ref<QA | null>(null)

const formData = ref({ bot_id: '', question: '', answer: '', category: '', keywords: '' })

const filteredQA = computed(() => {
  let result = qaPairs.value
  if (filterBotId.value) {
    result = result.filter(qa => qa.bot_id === filterBotId.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(qa =>
      qa.question.toLowerCase().includes(q) ||
      qa.answer.toLowerCase().includes(q)
    )
  }
  return result
})

function getBotName(botId: string) {
  const bot = botList.value.find(b => b.id === botId)
  return bot?.name || '未知'
}

async function loadQA() {
  try {
    const allQA: QA[] = []
    for (const bot of botList.value) {
      try {
        const data = await adminApi.getQA(bot.id)
        if (Array.isArray(data)) {
          allQA.push(...data.map(qa => ({ ...qa, bot_id: bot.id })))
        }
      } catch (e) {
        console.error(`Failed to load QA for bot ${bot.id}:`, e)
      }
    }
    qaPairs.value = allQA
  } catch (e) {
    console.error('Failed to load QA:', e)
  }
}

function openAddModal() {
  editingQA.value = null
  formData.value = { bot_id: '', question: '', answer: '', category: '', keywords: '' }
  showModal.value = true
}

function openEditModal(qa: QA) {
  editingQA.value = qa
  formData.value = {
    bot_id: qa.bot_id,
    question: qa.question,
    answer: qa.answer,
    category: qa.category || '',
    keywords: qa.keywords || ''
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingQA.value = null
}

async function submitQA() {
  if (!formData.value.question || !formData.value.answer) return
  if (!editingQA.value && !formData.value.bot_id) return
  try {
    if (editingQA.value) {
      await adminApi.updateQA(editingQA.value.id, {
        question: formData.value.question,
        answer: formData.value.answer,
        category: formData.value.category,
        keywords: formData.value.keywords
      })
    } else {
      await adminApi.createQA({
        bot_id: formData.value.bot_id,
        question: formData.value.question,
        answer: formData.value.answer,
        category: formData.value.category,
        keywords: formData.value.keywords
      })
    }
    closeModal()
    loadQA()
  } catch (e) {
    console.error('Failed to save QA:', e)
    alert('保存失败')
  }
}

function confirmDelete(qa: QA) {
  deleteTarget.value = qa
}

async function deleteQA() {
  if (!deleteTarget.value) return
  await adminApi.deleteQA(deleteTarget.value.id)
  deleteTarget.value = null
  loadQA()
}

onMounted(async () => {
  await fetchBots()
  await loadQA()
})
</script>

<style scoped>
.qa-page { max-width: 1000px; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { margin: 0; font-size: 24px; color: #333; }

.add-btn {
  padding: 10px 20px; background: #4a90d9; color: white; border: none;
  border-radius: 8px; cursor: pointer;
}

.filters { display: flex; gap: 12px; margin-bottom: 20px; }
.filter-select {
  padding: 10px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
}
.search-input {
  flex: 1; max-width: 300px; padding: 10px 16px; border: 1px solid #ddd;
  border-radius: 8px; font-size: 14px; outline: none;
}

.qa-list { display: flex; flex-direction: column; gap: 16px; }

.qa-card {
  background: white; border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.qa-content { margin-bottom: 12px; }
.qa-question, .qa-answer { margin-bottom: 8px; }
.label { font-weight: 600; color: #4a90d9; }

.qa-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; font-size: 12px; color: #999; }
.tag { background: #ecf5ff; color: #409eff; padding: 2px 8px; border-radius: 4px; }
.bot-tag { background: #f0f9eb; color: #67c23a; padding: 2px 8px; border-radius: 4px; }

.qa-actions { display: flex; gap: 8px; }
.edit-btn, .delete-btn {
  padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
}
.edit-btn { background: #f5f5f5; border: 1px solid #ddd; color: #666; }
.delete-btn { background: #fef0f0; border: 1px solid #f56c6c; color: #f56c6c; }

.empty-state { text-align: center; padding: 60px; color: #999; background: white; border-radius: 12px; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;
}

.modal-content { background: white; border-radius: 12px; width: 560px; max-width: 90vw; }

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid #eee;
}

.modal-header h3 { margin: 0; font-size: 18px; }
.close-btn { background: none; border: none; font-size: 24px; color: #999; cursor: pointer; }

.modal-body { padding: 20px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: #666; }
.form-group select,
.form-group textarea, .form-group input {
  width: 100%; padding: 10px 12px; border: 1px solid #ddd;
  border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box;
}

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.modal-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 16px 20px; border-top: 1px solid #eee;
}

.cancel-btn, .submit-btn, .delete-btn {
  padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer;
}

.cancel-btn { background: none; border: 1px solid #ddd; color: #666; }
.submit-btn { background: #4a90d9; border: none; color: white; }
.delete-btn { background: #f56c6c; border: none; color: white; }
.submit-btn:disabled { background: #ccc; }

/* Confirm */
.confirm { padding: 24px; text-align: center; }
.confirm h3 { margin: 0 0 12px 0; }
.confirm p { color: #666; margin: 0 0 20px 0; }
.confirm-actions { display: flex; justify-content: center; gap: 12px; }
</style>

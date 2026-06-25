<template>
  <div class="bots-page">
    <div class="page-header">
      <h1>智能体管理</h1>
      <button @click="showCreateModal = true" :disabled="isAtLimit" class="btn-primary">
        {{ isAtLimit ? '已达上限 (5/5)' : '添加智能体' }}
      </button>
    </div>

    <div v-if="sortedBotList.length === 0" class="empty-state">
      <p>暂无智能体，请点击上方按钮创建</p>
    </div>

    <div v-else class="bots-grid">
      <div v-for="bot in sortedBotList" :key="bot.id" class="bot-card" :class="{ 'is-default': bot.is_default }">
        <div v-if="bot.is_default" class="default-badge">默认</div>
        <div class="bot-header">
          <h3>{{ bot.name }}</h3>
          <span :class="['status-badge', bot.status]">{{ statusText[bot.status] }}</span>
        </div>
        <div class="bot-info">
          <div class="info-row"><span class="info-label">行业:</span> {{ industryText[bot.industry_type] || bot.industry_type }}</div>
          <div class="info-row description-row">
            <span class="info-label">描述:</span>
            <span class="description-text">{{ bot.description ? (bot.description.length > 80 ? bot.description.slice(0, 80) + '...' : bot.description) : '-' }}</span>
          </div>
        </div>
        <div class="bot-stats">
          <div class="stat">
            <span class="stat-value">{{ getBotStats(bot.id).total_conversations || 0 }}</span>
            <span class="stat-label">对话总数</span>
          </div>
          <div class="stat">
            <span class="stat-value" :class="getSatisfactionClass(getBotStats(bot.id).avg_satisfaction)">{{ getBotStats(bot.id).avg_satisfaction || 0 }}%</span>
            <span class="stat-label">满意度</span>
          </div>
        </div>

        <!-- 功能按钮 -->
        <div class="feature-buttons">
          <button @click="openKnowledgeBase(bot)" class="feature-btn" title="知识库">
            📚 知识库
          </button>
          <button @click="openQAManagement(bot)" class="feature-btn" title="QA管理">
            ❓ QA管理
          </button>
        </div>

        <div class="bot-actions">
          <button @click="editBot(bot)" class="btn-small btn-primary">编辑</button>
          <button v-if="!bot.is_default" @click="confirmDelete(bot)" class="btn-small btn-danger">删除</button>
          <button v-else class="btn-small btn-disabled" :title="'无法删除默认智能体'" disabled>删除</button>
          <button v-if="!bot.is_default" @click="setAsDefault(bot)" class="btn-small btn-default">设为默认</button>
        </div>
      </div>
    </div>

    <!-- 创建智能体弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>创建智能体</h2>
        <form @submit.prevent="createBot">
          <div class="form-row">
            <div class="form-group">
              <label>名称</label>
              <input v-model="newBot.name" type="text" placeholder="智能体名称" required />
            </div>
            <div class="form-group">
              <label>行业类型</label>
              <select v-model="newBot.industry_type" required>
                <option value="ecommerce">电商</option>
                <option value="medical">医疗</option>
                <option value="saas">SaaS</option>
                <option value="it">IT服务</option>
                <option value="general">通用</option>
              </select>
            </div>
          </div>
          <div class="form-group form-group-full">
            <label>系统提示词</label>
            <textarea
              v-model="newBot.system_prompt"
              rows="4"
              maxlength="1200"
              placeholder="定义智能体的角色设定和行为规则..."
            ></textarea>
            <div class="char-count">{{ (newBot.system_prompt || '').length }} / 1200</div>
          </div>
          <div class="form-group form-group-full">
            <label>描述</label>
            <textarea v-model="newBot.description" placeholder="智能体描述（可选）"></textarea>
          </div>
          <div class="default-checkbox-row">
            <label class="default-checkbox-label">
              <input v-model="newBot.set_as_default" type="checkbox" />
              <span>设为默认智能体</span>
            </label>
            <span class="tooltip-icon" title="默认智能体将自动接待未指定智能体的客户">ⓘ</span>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑智能体弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <h2>编辑智能体</h2>
        <form @submit.prevent="updateBot">
          <div class="form-row">
            <div class="form-group">
              <label>名称</label>
              <input v-model="editBotForm.name" type="text" placeholder="智能体名称" required />
            </div>
            <div class="form-group">
              <label>行业类型</label>
              <select v-model="editBotForm.industry_type" required>
                <option value="ecommerce">电商</option>
                <option value="medical">医疗</option>
                <option value="saas">SaaS</option>
                <option value="it">IT服务</option>
                <option value="general">通用</option>
              </select>
            </div>
          </div>
          <div class="form-group form-group-full">
            <label>系统提示词</label>
            <textarea
              v-model="editBotForm.system_prompt"
              rows="4"
              maxlength="1200"
              placeholder="定义智能体的角色设定和行为规则..."
            ></textarea>
            <div class="char-count">{{ (editBotForm.system_prompt || '').length }} / 1200</div>
          </div>
          <div class="form-group form-group-full">
            <label>描述</label>
            <textarea v-model="editBotForm.description" placeholder="智能体描述（可选）"></textarea>
          </div>
          <div class="default-checkbox-row">
            <label class="default-checkbox-label">
              <input v-model="editBotForm.set_as_default" type="checkbox" />
              <span>设为默认智能体</span>
            </label>
            <span class="tooltip-icon" title="默认智能体将自动接待未指定智能体的客户">ⓘ</span>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <h2>确认删除</h2>
        <p>确定要删除智能体 "{{ botToDelete?.name }}" 吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn-secondary">取消</button>
          <button @click="deleteBot" class="btn-danger">删除</button>
        </div>
      </div>
    </div>

    <!-- 首个智能体默认智能体确认弹窗 -->
    <div v-if="showFirstBotDialog" class="modal-overlay">
      <div class="modal">
        <h2>设置默认智能体</h2>
        <p>您还没有设置默认智能体。客户在聊天窗口时，如果没有设置默认智能体，将会看到报错信息。</p>
        <div class="modal-actions">
          <button @click="cancelSetFirstBotDefault" class="btn-secondary">取消</button>
          <button @click="confirmSetFirstBotDefault" class="btn-primary">确认</button>
        </div>
      </div>
    </div>

    <!-- 知识库弹窗 -->
    <div v-if="showKnowledgeModal" class="modal-overlay" @click.self="closeKnowledgeModal">
      <div class="modal modal-large">
        <h2>知识库 - {{ currentBotForModal?.name }}</h2>

        <div class="upload-area" @click="triggerFileInput">
          <input type="file" ref="fileInput" @change="handleFileChange" accept=".pdf,.docx,.txt,.md,.html" hidden />
          <span class="upload-icon">📁</span>
          <p>点击选择文件或拖拽到此处上传</p>
          <p class="formats">支持 PDF, DOCX, TXT, MD, HTML</p>
        </div>

        <div v-if="selectedFile" class="selected-file">
          <span>已选择: {{ selectedFile.name }}</span>
          <button @click="uploadDocument" class="btn-primary" :disabled="uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>

        <div class="documents-list">
          <h3>已上传文档</h3>
          <div v-if="botDocuments.length === 0" class="no-docs">暂无文档</div>
          <div v-for="doc in botDocuments" :key="doc.id" class="doc-item">
            <div class="doc-info">
              <span class="doc-name">{{ doc.title }}</span>
              <span :class="['status-badge', doc.status]">{{ statusText[doc.status] }}</span>
            </div>
            <button @click="deleteDocument(doc)" class="btn-small btn-danger">删除</button>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeKnowledgeModal" class="btn-secondary">关闭</button>
        </div>
      </div>
    </div>

    <!-- QA管理弹窗 -->
    <div v-if="showQAModal" class="modal-overlay" @click.self="closeQAModal">
      <div class="modal modal-large">
        <h2>QA管理 - {{ currentBotForModal?.name }}</h2>

        <div class="qa-header">
          <input v-model="qaSearchQuery" type="text" placeholder="搜索问题或答案..." class="search-input" />
          <button @click="openAddQA" class="btn-primary">+ 添加QA</button>
        </div>

        <div class="qa-list">
          <div v-if="filteredBotQA.length === 0" class="no-qa">暂无QA对</div>
          <div v-for="qa in filteredBotQA" :key="qa.id" class="qa-item">
            <div class="qa-content">
              <div class="qa-question"><span class="label">Q:</span> {{ qa.question }}</div>
              <div class="qa-answer"><span class="label">A:</span> {{ qa.answer }}</div>
            </div>
            <div class="qa-actions">
              <button @click="openEditQA(qa)" class="btn-small btn-primary">编辑</button>
              <button @click="deleteQA(qa)" class="btn-small btn-danger">删除</button>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeQAModal" class="btn-secondary">关闭</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑QA弹窗 -->
    <div v-if="showQAEditModal" class="modal-overlay" @click.self="closeQAEditModal">
      <div class="modal">
        <h2>{{ editingQA ? '编辑QA' : '添加QA' }}</h2>
        <form @submit.prevent="submitQA">
          <div class="form-group">
            <label>问题 *</label>
            <textarea v-model="qaForm.question" rows="3" placeholder="请输入常见问题" required></textarea>
          </div>
          <div class="form-group">
            <label>答案 *</label>
            <textarea v-model="qaForm.answer" rows="5" placeholder="请输入标准回答" required></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <input v-model="qaForm.category" type="text" placeholder="如：产品咨询" />
            </div>
            <div class="form-group">
              <label>关键词</label>
              <input v-model="qaForm.keywords" type="text" placeholder="逗号分隔" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeQAEditModal" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBotStore } from '@/stores/botStore'
import { adminApi } from '@/api'

const router = useRouter()
const { botList, isAtLimit, fetchBots, createBot: createBotStore, deleteBot: deleteBotStore } = useBotStore()

// 排序后的智能体列表：默认优先，其余按创建顺序
const sortedBotList = computed(() => {
  return [...botList.value].sort((a, b) => {
    if (a.is_default && !b.is_default) return -1
    if (!a.is_default && b.is_default) return 1
    return 0
  })
})

// Create modal
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const showEditModal = ref(false)
const botToDelete = ref<any>(null)
const editingBot = ref<any>(null)
const botStats = ref<Record<string, any>>({})

const editBotForm = ref({
  name: '',
  industry_type: 'general',
  description: '',
  system_prompt: '',
  set_as_default: false
})

// Knowledge base modal
const showKnowledgeModal = ref(false)
const currentBotForModal = ref<any>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const botDocuments = ref<any[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

// QA modal
const showQAModal = ref(false)
const qaSearchQuery = ref('')
const botQA = ref<any[]>([])
const showQAEditModal = ref(false)
const editingQA = ref<any>(null)
const qaForm = ref({ question: '', answer: '', category: '', keywords: '' })

const newBot = ref({
  name: '',
  industry_type: 'general',
  description: '',
  system_prompt: '',
  set_as_default: false
})

// First bot confirmation dialog
const showFirstBotDialog = ref(false)
const pendingBotId = ref<string | null>(null)

const statusText: Record<string, string> = {
  active: '运行中',
  inactive: '已停止',
  training: '训练中',
  pending: '等待中',
  parsing: '处理中',
  indexed: '已索引',
  failed: '失败'
}

const industryText: Record<string, string> = {
  ecommerce: '电商',
  medical: '医疗',
  saas: 'SaaS',
  it: 'IT服务',
  general: '通用'
}

const filteredBotQA = computed(() => {
  if (!qaSearchQuery.value) return botQA.value
  const q = qaSearchQuery.value.toLowerCase()
  return botQA.value.filter(qa =>
    qa.question.toLowerCase().includes(q) ||
    qa.answer.toLowerCase().includes(q)
  )
})

function getBotStats(botId: string) {
  return botStats.value[botId] || {}
}

function getSatisfactionClass(rate: number) {
  if (!rate) return ''
  if (rate >= 85) return 'stat-value-green'
  if (rate >= 60) return 'stat-value-orange'
  return 'stat-value-red'
}

async function loadStats() {
  const stats: Record<string, any> = {}
  for (const bot of botList.value) {
    try {
      const data = await adminApi.getAnalytics(bot.id)
      stats[bot.id] = data
    } catch (e) {
      stats[bot.id] = {}
    }
  }
  botStats.value = stats
}

async function editBot(bot: any) {
  editingBot.value = bot
  // Load full config including system_prompt
  try {
    const config = await adminApi.getBotConfig(bot.id)
    editBotForm.value = {
      name: bot.name,
      industry_type: bot.industry_type,
      description: bot.description || '',
      system_prompt: config.system_prompt || '',
      set_as_default: bot.is_default || false
    }
  } catch (e) {
    editBotForm.value = {
      name: bot.name,
      industry_type: bot.industry_type,
      description: bot.description || '',
      system_prompt: '',
      set_as_default: bot.is_default || false
    }
  }
  showEditModal.value = true
}

async function updateBot() {
  if (!editingBot.value) return
  try {
    const { name, industry_type, description, system_prompt } = editBotForm.value
    await adminApi.updateBotConfig(editingBot.value.id, { name, industry_type, description, system_prompt })
    showEditModal.value = false
    await fetchBots()
  } catch (e) {
    console.error('Failed to update bot:', e)
    alert('更新失败')
  }
}

function confirmDelete(bot: any) {
  botToDelete.value = bot
  showDeleteModal.value = true
}

async function createBot() {
  try {
    const { name, industry_type, description, system_prompt, set_as_default } = newBot.value
    const result = await createBotStore({ name, industry_type, description })
    const botId = typeof result === 'object' ? result.id : result

    // Save system_prompt via updateBotConfig
    if (botId && system_prompt) {
      await adminApi.updateBotConfig(botId, { system_prompt })
    }

    // If checkbox was checked, set as default directly
    if (set_as_default && botId) {
      await adminApi.setDefaultBot(botId)
      await fetchBots()
    }

    showCreateModal.value = false
    newBot.value = { name: '', industry_type: 'general', description: '', system_prompt: '', set_as_default: false }
    await loadStats()

    // If this is the first bot and checkbox wasn't checked, show confirmation dialog
    if (botList.value.length === 0 && !set_as_default) {
      pendingBotId.value = botId
      showFirstBotDialog.value = true
    }
  } catch (e) {
    console.error('Failed to create bot:', e)
    alert('创建失败')
  }
}

async function setAsDefault(bot: any) {
  try {
    await adminApi.setDefaultBot(bot.id)
    await fetchBots()
  } catch (e) {
    console.error('Failed to set default bot:', e)
    alert('设置默认智能体失败')
  }
}

async function confirmSetFirstBotDefault() {
  if (pendingBotId.value) {
    try {
      await adminApi.setDefaultBot(pendingBotId.value)
      await fetchBots()
    } catch (e) {
      console.error('Failed to set default bot:', e)
    }
  }
  showFirstBotDialog.value = false
  pendingBotId.value = null
}

function cancelSetFirstBotDefault() {
  showFirstBotDialog.value = false
  pendingBotId.value = null
}

async function deleteBot() {
  if (!botToDelete.value) return
  try {
    await deleteBotStore(botToDelete.value.id)
    showDeleteModal.value = false
    botToDelete.value = null
  } catch (e) {
    console.error('Failed to delete bot:', e)
    alert('删除失败')
  }
}

// Knowledge base functions
async function openKnowledgeBase(bot: any) {
  currentBotForModal.value = bot
  selectedFile.value = null
  botDocuments.value = []
  showKnowledgeModal.value = true
  await loadBotDocuments()
}

function closeKnowledgeModal() {
  showKnowledgeModal.value = false
  currentBotForModal.value = null
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    selectedFile.value = target.files[0]
  }
}

async function loadBotDocuments() {
  if (!currentBotForModal.value) return
  try {
    const data = await adminApi.getDocuments(currentBotForModal.value.id)
    botDocuments.value = data.documents || []
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

async function uploadDocument() {
  if (!selectedFile.value || !currentBotForModal.value) return

  // Check max 10 documents limit
  if (botDocuments.value.length >= 10) {
    alert('每个智能体最多上传10个文档，请先删除部分文档')
    return
  }

  uploading.value = true
  try {
    await adminApi.uploadDocument(currentBotForModal.value.id, selectedFile.value)
    selectedFile.value = null
    await loadBotDocuments()
  } catch (e) {
    console.error('Failed to upload:', e)
    alert('上传失败')
  } finally {
    uploading.value = false
  }
}

async function deleteDocument(doc: any) {
  if (!confirm(`确定要删除文档 "${doc.title}" 吗？`)) return
  try {
    await adminApi.deleteDocument(doc.id)
    await loadBotDocuments()
  } catch (e) {
    console.error('Failed to delete:', e)
    alert('删除失败')
  }
}

// QA functions
async function openQAManagement(bot: any) {
  currentBotForModal.value = bot
  qaSearchQuery.value = ''
  botQA.value = []
  showQAModal.value = true
  await loadBotQA()
}

function closeQAModal() {
  showQAModal.value = false
  currentBotForModal.value = null
}

async function loadBotQA() {
  if (!currentBotForModal.value) return
  try {
    const data = await adminApi.getQA(currentBotForModal.value.id)
    botQA.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Failed to load QA:', e)
  }
}

function openAddQA() {
  editingQA.value = null
  qaForm.value = { question: '', answer: '', category: '', keywords: '' }
  showQAEditModal.value = true
}

function openEditQA(qa: any) {
  editingQA.value = qa
  qaForm.value = {
    question: qa.question,
    answer: qa.answer,
    category: qa.category || '',
    keywords: qa.keywords || ''
  }
  showQAEditModal.value = true
}

function closeQAEditModal() {
  showQAEditModal.value = false
  editingQA.value = null
}

async function submitQA() {
  if (!qaForm.value.question || !qaForm.value.answer) return
  try {
    if (editingQA.value) {
      await adminApi.updateQA(editingQA.value.id, qaForm.value)
    } else {
      await adminApi.createQA({
        bot_id: currentBotForModal.value.id,
        ...qaForm.value
      })
    }
    closeQAEditModal()
    await loadBotQA()
  } catch (e) {
    console.error('Failed to save QA:', e)
    alert('保存失败')
  }
}

async function deleteQA(qa: any) {
  if (!confirm('确定要删除这条QA吗？')) return
  try {
    await adminApi.deleteQA(qa.id)
    await loadBotQA()
  } catch (e) {
    console.error('Failed to delete QA:', e)
    alert('删除失败')
  }
}

onMounted(async () => {
  await fetchBots()
  await loadStats()
})
</script>

<style scoped>
.bots-page { max-width: 1200px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 { font-size: 24px; color: #333; }

.btn-primary {
  padding: 10px 20px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 20px;
  background: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-danger {
  padding: 10px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-small.btn-primary {
  background: #4a90d9;
  color: white;
}

.btn-small.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-small.btn-default {
  background: #4a90d9;
  color: white;
}

.btn-small.btn-disabled {
  background: #ccc;
  color: #999;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  background: white;
  border-radius: 12px;
}

.bots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.bot-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px 20px 20px;
  padding-top: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 360px;
  box-sizing: border-box;
}

.bot-card.is-default {
  border: 2px solid #4a90d9;
}

.default-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #4a90d9;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.bot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.bot-header h3 { margin: 0; font-size: 18px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; }

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  flex-shrink: 0;
}

.status-badge.active { background: #e8f5e9; color: #2e7d32; }
.status-badge.inactive { background: #f5f5f5; color: #666; }
.status-badge.training { background: #fff3e0; color: #e65100; }
.status-badge.pending { background: #f5f5f5; color: #666; }
.status-badge.parsing { background: #fff3e0; color: #e65100; }
.status-badge.indexed { background: #e8f5e9; color: #2e7d32; }
.status-badge.failed { background: #ffebee; color: #c62828; }

.bot-info {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.info-row {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  text-align: left;
}

.info-label {
  font-weight: 500;
  margin-right: 4px;
  flex-shrink: 0;
}

.description-row {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  height: 2.8em;
}

.description-text {
  word-break: break-word;
}

.bot-stats {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.stat-value-green { color: #4caf50; }
.stat-value-orange { color: #ff9800; }
.stat-value-red { color: #f44336; }

.stat-label {
  font-size: 12px;
  color: #999;
}

.feature-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.bot-actions {
  margin-top: auto;
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

.feature-btn {
  flex: 1;
  padding: 8px 12px;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
}

.feature-btn:hover {
  background: #e8f4fd;
  border-color: #4a90d9;
  color: #4a90d9;
}

.bot-actions { display: flex; gap: 8px; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 560px;
}

.modal-large {
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h2 { margin: 0 0 20px 0; font-size: 18px; color: #333;}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 16px; color: #666; text-align: left; }
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group-full {
  margin-bottom: 16px;
}

.char-count {
  font-size: 12px;
  color: #999;
  text-align: right;
  margin-top: 4px;
}

.checkbox-label-row {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
}

.checkbox-label-row input {
  width: 18px;
  height: 18px;
}

.checkbox-hint-row {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.default-checkbox-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.default-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.default-checkbox-label input {
  width: 18px;
  height: 18px;
}

.tooltip-icon {
  color: #999;
  cursor: help;
  font-size: 16px;
  position: relative;
}

.tooltip-icon:hover {
  color: #4a90d9;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Knowledge base modal styles */
.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  margin-bottom: 16px;
}

.upload-area:hover {
  border-color: #4a90d9;
  background: #f8f9fa;
}

.upload-icon { font-size: 36px; }
.upload-area p { margin: 8px 0 0 0; color: #666; }
.formats { font-size: 12px; color: #999 !important; }

.selected-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 16px;
}

.selected-file span { font-size: 14px; }

.documents-list {
  margin-top: 20px;
}

.documents-list h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.no-docs {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 8px;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-name {
  font-size: 14px;
  color: #333;
}

/* QA modal styles */
.qa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.qa-list {
  max-height: 300px;
  overflow-y: auto;
}

.no-qa {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.qa-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 8px;
}

.qa-content { margin-bottom: 8px; }
.qa-question, .qa-answer { margin-bottom: 4px; font-size: 14px; }
.label { font-weight: 600; color: #4a90d9; }
.qa-actions { display: flex; gap: 8px; justify-content: flex-end; }
</style>

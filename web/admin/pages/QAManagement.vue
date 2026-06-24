<template>
  <div class="qa-management">
    <div class="header">
      <h1>QA对管理</h1>
      <button class="add-btn" @click="showAddModal = true">+ 添加QA</button>
    </div>

    <!-- 筛选 -->
    <div class="filters">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索问题或答案..."
        class="search-input"
      />
    </div>

    <!-- QA列表 -->
    <div class="qa-list">
      <div v-for="qa in filteredQA" :key="qa.id" class="qa-card">
        <div class="qa-content">
          <div class="qa-question">
            <span class="label">Q:</span>
            <span class="text">{{ qa.question }}</span>
          </div>
          <div class="qa-answer">
            <span class="label">A:</span>
            <span class="text">{{ qa.answer }}</span>
          </div>
        </div>
        <div class="qa-meta">
          <span v-if="qa.category" class="tag">{{ qa.category }}</span>
          <span v-if="qa.keywords" class="keywords">{{ qa.keywords }}</span>
          <span class="stats">
            使用 {{ qa.usage_count }} 次
            <span v-if="qa.satisfaction_rate">
              | 满意度 {{ (qa.satisfaction_rate * 100).toFixed(0) }}%
            </span>
          </span>
        </div>
        <div class="qa-actions">
          <button class="edit-btn" @click="editQA(qa)">编辑</button>
          <button class="delete-btn" @click="confirmDelete(qa)">删除</button>
        </div>
      </div>

      <div v-if="filteredQA.length === 0" class="empty-state">
        <p>暂无QA对，请添加开始构建问答库</p>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showAddModal || editingQA" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingQA ? '编辑QA' : '添加QA' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>问题 *</label>
            <textarea
              v-model="formData.question"
              placeholder="请输入常见问题"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label>答案 *</label>
            <textarea
              v-model="formData.answer"
              placeholder="请输入标准回答"
              rows="5"
            ></textarea>
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
          <button class="submit-btn" @click="submitQA" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
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

const props = defineProps<{
  botId: string
}>()

const qaPairs = ref<QA[]>([])
const searchQuery = ref('')
const showAddModal = ref(false)
const editingQA = ref<QA | null>(null)
const deleteTarget = ref<QA | null>(null)
const submitting = ref(false)

const formData = ref({
  question: '',
  answer: '',
  category: '',
  keywords: ''
})

interface QA {
  id: string
  question: string
  answer: string
  keywords: string
  category: string
  usage_count: number
  satisfaction_rate: number | null
}

const filteredQA = computed(() => {
  if (!searchQuery.value) return qaPairs.value

  const query = searchQuery.value.toLowerCase()
  return qaPairs.value.filter(qa =>
    qa.question.toLowerCase().includes(query) ||
    qa.answer.toLowerCase().includes(query) ||
    qa.keywords?.toLowerCase().includes(query)
  )
})

async function loadQA() {
  try {
    const response = await fetch(`/api/admin/qa?bot_id=${props.botId}`)
    const data = await response.json()
    qaPairs.value = data
  } catch (error) {
    console.error('加载QA失败:', error)
  }
}

function editQA(qa: QA) {
  editingQA.value = qa
  formData.value = {
    question: qa.question,
    answer: qa.answer,
    category: qa.category || '',
    keywords: qa.keywords || ''
  }
}

function closeModal() {
  showAddModal.value = false
  editingQA.value = null
  formData.value = { question: '', answer: '', category: '', keywords: '' }
}

async function submitQA() {
  if (!formData.value.question.trim() || !formData.value.answer.trim()) return

  submitting.value = true

  try {
    if (editingQA.value) {
      await fetch(`/api/admin/qa/${editingQA.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData.value)
      })
    } else {
      await fetch('/api/admin/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bot_id: props.botId,
          ...formData.value
        })
      })
    }

    closeModal()
    loadQA()
  } catch (error) {
    console.error('保存QA失败:', error)
  } finally {
    submitting.value = false
  }
}

function confirmDelete(qa: QA) {
  deleteTarget.value = qa
}

async function deleteQA() {
  if (!deleteTarget.value) return

  try {
    await fetch(`/api/admin/qa/${deleteTarget.value.id}`, {
      method: 'DELETE'
    })
    deleteTarget.value = null
    loadQA()
  } catch (error) {
    console.error('删除QA失败:', error)
  }
}

onMounted(() => {
  loadQA()
})
</script>

<style scoped>
.qa-management {
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.add-btn {
  padding: 10px 20px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.filters {
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.search-input:focus {
  border-color: #4a90d9;
}

.qa-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.qa-content {
  margin-bottom: 12px;
}

.qa-question,
.qa-answer {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.label {
  font-weight: 600;
  color: #4a90d9;
}

.text {
  color: #333;
  line-height: 1.5;
}

.qa-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #999;
}

.tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
}

.keywords {
  color: #666;
}

.qa-actions {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.edit-btn {
  background: #f5f5f5;
  border: 1px solid #ddd;
  color: #666;
}

.delete-btn {
  background: #fef0f0;
  border: 1px solid #f56c6c;
  color: #f56c6c;
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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 560px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #666;
}

.form-group textarea,
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.form-group textarea:focus,
.form-group input:focus {
  border-color: #4a90d9;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.cancel-btn,
.submit-btn,
.delete-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.cancel-btn {
  background: none;
  border: 1px solid #ddd;
  color: #666;
}

.submit-btn {
  background: #4a90d9;
  border: none;
  color: white;
}

.delete-btn {
  background: #f56c6c;
  border: none;
  color: white;
}

.submit-btn:disabled {
  background: #ccc;
}

/* Confirm */
.modal-content.confirm {
  padding: 24px;
  text-align: center;
}

.modal-content.confirm h3 {
  margin: 0 0 12px 0;
}

.modal-content.confirm p {
  color: #666;
  margin: 0 0 20px 0;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>

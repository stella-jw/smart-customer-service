<template>
  <div class="knowledge-page">
    <div class="header">
      <h1>知识库管理</h1>
      <button @click="showUpload = true" class="upload-btn">+ 上传文档</button>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <label>筛选机器人：</label>
      <select v-model="filterBotId" @change="loadDocuments">
        <option value="">全部机器人</option>
        <option v-for="bot in botList" :key="bot.id" :value="bot.id">
          {{ bot.name }}
        </option>
      </select>
    </div>

    <div class="document-list">
      <table>
        <thead>
          <tr>
            <th>文档名称</th>
            <th>所属机器人</th>
            <th>类型</th>
            <th>状态</th>
            <th>分块数</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.id">
            <td>{{ doc.title }}</td>
            <td>{{ getBotName(doc.bot_id) }}</td>
            <td>{{ doc.file_type?.toUpperCase() }}</td>
            <td><span :class="['status', doc.status]">{{ statusLabel(doc.status) }}</span></td>
            <td>{{ doc.chunk_count }}</td>
            <td>{{ formatDate(doc.created_at) }}</td>
            <td>
              <button @click="reindex(doc.id)" class="action-btn" title="重新索引">🔄</button>
              <button @click="confirmDelete(doc)" class="action-btn delete" title="删除">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="documents.length === 0" class="empty-state">
        <p>暂无文档，请上传文档开始构建知识库</p>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>上传文档</h3>
          <button @click="showUpload = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择机器人</label>
            <select v-model="uploadBotId" required>
              <option value="">请选择机器人</option>
              <option v-for="bot in botList" :key="bot.id" :value="bot.id">
                {{ bot.name }}
              </option>
            </select>
          </div>
          <div
            class="upload-area"
            :class="{ dragover: isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave="isDragover = false"
            @drop.prevent="handleDrop"
          >
            <input type="file" ref="fileInput" @change="handleFileSelect" accept=".pdf,.docx,.txt,.md,.html" hidden />
            <div class="upload-hint" @click="fileInput.click()">
              <span class="icon">📁</span>
              <p>点击选择文件或拖拽到此处</p>
              <p class="formats">支持 PDF, DOCX, TXT, MD, HTML</p>
            </div>
          </div>
          <div v-if="selectedFile" class="selected-file">
            <span>已选择: {{ selectedFile.name }}</span>
            <span class="size">{{ formatSize(selectedFile.size) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showUpload = false">取消</button>
          <button class="upload-btn" @click="uploadDocument" :disabled="!selectedFile || !uploadBotId || uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-content confirm">
        <h3>确认删除</h3>
        <p>确定要删除文档 "{{ deleteTarget.title }}" 吗？</p>
        <div class="confirm-actions">
          <button class="cancel-btn" @click="deleteTarget = null">取消</button>
          <button class="delete-btn" @click="deleteDocument">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useBotStore } from '@/stores/botStore'

const { botList, fetchBots } = useBotStore()

interface Document {
  id: string
  bot_id: string
  title: string
  file_type: string
  file_size: number
  status: string
  chunk_count: number
  created_at: string
}

const documents = ref<Document[]>([])
const showUpload = ref(false)
const isDragover = ref(false)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const deleteTarget = ref<Document | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const filterBotId = ref('')
const uploadBotId = ref('')

function getBotName(botId: string) {
  const bot = botList.value.find(b => b.id === botId)
  return bot?.name || '未知'
}

async function loadDocuments() {
  try {
    const allDocs: Document[] = []
    for (const bot of botList.value) {
      try {
        const data = await adminApi.getDocuments(bot.id)
        if (data.documents) {
          allDocs.push(...data.documents)
        }
      } catch (e) {
        console.error(`Failed to load docs for bot ${bot.id}:`, e)
      }
    }
    if (filterBotId.value) {
      documents.value = allDocs.filter(d => d.bot_id === filterBotId.value)
    } else {
      documents.value = allDocs
    }
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) selectedFile.value = input.files[0]
}

function handleDrop(e: DragEvent) {
  isDragover.value = false
  if (e.dataTransfer?.files?.[0]) selectedFile.value = e.dataTransfer.files[0]
}

async function uploadDocument() {
  if (!selectedFile.value || !uploadBotId.value) return
  uploading.value = true
  try {
    await adminApi.uploadDocument(uploadBotId.value, selectedFile.value)
    showUpload.value = false
    selectedFile.value = null
    uploadBotId.value = ''
    loadDocuments()
  } catch (e) {
    console.error('Upload failed:', e)
    alert('上传失败')
  } finally {
    uploading.value = false
  }
}

async function reindex(docId: string) {
  await adminApi.reindexDocument(docId)
  loadDocuments()
}

function confirmDelete(doc: Document) {
  deleteTarget.value = doc
}

async function deleteDocument() {
  if (!deleteTarget.value) return
  await adminApi.deleteDocument(deleteTarget.value.id)
  deleteTarget.value = null
  loadDocuments()
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: '等待中',
    parsing: '解析中',
    indexed: '已索引',
    failed: '失败'
  }
  return labels[status] || status
}

function formatDate(str: string) {
  return new Date(str).toLocaleDateString('zh-CN')
}

function formatSize(bytes: number) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(async () => {
  await fetchBots()
  await loadDocuments()
})
</script>

<style scoped>
.knowledge-page { max-width: 1200px; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { margin: 0; font-size: 24px; color: #333; }

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
}

.filter-bar label {
  font-size: 14px;
  color: #666;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.upload-btn {
  padding: 10px 20px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.upload-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.document-list { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f9f9f9; font-weight: 500; color: #666; font-size: 14px; }

.status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
.status.pending { background: #fdf6ec; color: #e6a23c; }
.status.parsing { background: #ecf5ff; color: #409eff; }
.status.indexed { background: #f0f9eb; color: #67c23a; }
.status.failed { background: #fef0f0; color: #f56c6c; }

.action-btn { background: none; border: none; cursor: pointer; padding: 4px 8px; font-size: 16px; }
.action-btn.delete:hover { opacity: 0.7; }

.empty-state { padding: 60px; text-align: center; color: #999; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 480px;
  max-width: 90vw;
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid #eee;
}

.modal-header h3 { margin: 0; font-size: 18px; }
.close-btn { background: none; border: none; font-size: 24px; color: #999; cursor: pointer; }

.modal-body { padding: 20px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: #666; }
.form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; box-sizing: border-box; }

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-area.dragover { border-color: #4a90d9; background: #f0f9ff; }
.upload-hint { pointer-events: none; }
.upload-hint .icon { font-size: 48px; }
.upload-hint p { margin: 12px 0 0 0; color: #666; }
.formats { font-size: 12px; color: #999 !important; }

.selected-file {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
}

.size { color: #999; }

.modal-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 16px 20px; border-top: 1px solid #eee;
}

.cancel-btn, .delete-btn {
  padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer;
}

.cancel-btn { background: none; border: 1px solid #ddd; color: #666; }
.delete-btn { background: #f56c6c; border: none; color: white; }

/* Confirm Modal */
.confirm { padding: 24px; text-align: center; }
.confirm h3 { margin: 0 0 12px 0; }
.confirm p { color: #666; margin: 0 0 20px 0; }
.confirm-actions { display: flex; justify-content: center; gap: 12px; }
</style>

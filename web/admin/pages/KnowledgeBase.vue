<template>
  <div class="knowledge-base">
    <div class="header">
      <h1>知识库管理</h1>
      <button class="upload-btn" @click="showUpload = true">
        + 上传文档
      </button>
    </div>

    <!-- 文档列表 -->
    <div class="document-list">
      <table>
        <thead>
          <tr>
            <th>文档名称</th>
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
            <td>{{ doc.file_type.toUpperCase() }}</td>
            <td>
              <span :class="['status', doc.status]">{{ getStatusLabel(doc.status) }}</span>
            </td>
            <td>{{ doc.chunk_count }}</td>
            <td>{{ formatDate(doc.created_at) }}</td>
            <td>
              <button class="action-btn reindex" @click="reindex(doc.id)" title="重新索引">
                🔄
              </button>
              <button class="action-btn delete" @click="confirmDelete(doc)" title="删除">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="documents.length === 0" class="empty-state">
        <p>暂无文档，请上传文档开始构建知识库</p>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>上传文档</h3>
          <button class="close-btn" @click="showUpload = false">×</button>
        </div>

        <div class="modal-body">
          <div
            class="upload-area"
            :class="{ dragover: isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave="isDragover = false"
            @drop.prevent="handleDrop"
          >
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              accept=".pdf,.docx,.txt,.md,.html"
              hidden
            />
            <div class="upload-hint" @click="fileInput.click()">
              <span class="icon">📁</span>
              <p>点击选择文件或拖拽文件到此处</p>
              <p class="formats">支持 PDF, DOCX, TXT, MD, HTML</p>
            </div>
          </div>

          <div v-if="selectedFile" class="selected-file">
            <span>已选择: {{ selectedFile.name }}</span>
            <span class="size">{{ formatSize(selectedFile.size) }}</span>
          </div>

          <div v-if="uploadProgress > 0" class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" @click="showUpload = false">取消</button>
          <button
            class="upload-confirm-btn"
            @click="uploadDocument"
            :disabled="!selectedFile || uploading"
          >
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-content confirm">
        <h3>确认删除</h3>
        <p>确定要删除文档 "{{ deleteTarget.title }}" 吗？此操作不可恢复。</p>
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

const props = defineProps<{
  botId: string
}>()

const documents = ref<Document[]>([])
const showUpload = ref(false)
const isDragover = ref(false)
const selectedFile = ref<File | null>(null)
const uploadProgress = ref(0)
const uploading = ref(false)
const deleteTarget = ref<Document | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

interface Document {
  id: string
  title: string
  file_type: string
  file_size: number
  status: string
  chunk_count: number
  created_at: string
}

async function loadDocuments() {
  try {
    const response = await fetch(`/api/admin/documents?bot_id=${props.botId}`)
    const data = await response.json()
    documents.value = data.documents
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}

function handleDrop(event: DragEvent) {
  isDragover.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

async function uploadDocument() {
  if (!selectedFile.value) return

  uploading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch(`/api/admin/documents?bot_id=${props.botId}`, {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      showUpload.value = false
      selectedFile.value = null
      loadDocuments()
    }
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function reindex(docId: string) {
  try {
    await fetch(`/api/admin/documents/${docId}/reindex`, { method: 'POST' })
    loadDocuments()
  } catch (error) {
    console.error('重新索引失败:', error)
  }
}

function confirmDelete(doc: Document) {
  deleteTarget.value = doc
}

async function deleteDocument() {
  if (!deleteTarget.value) return

  try {
    await fetch(`/api/admin/documents/${deleteTarget.value.id}`, {
      method: 'DELETE'
    })
    deleteTarget.value = null
    loadDocuments()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    'pending': '等待中',
    'parsing': '解析中',
    'indexed': '已索引',
    'failed': '失败'
  }
  return labels[status] || status
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.knowledge-base {
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

.upload-btn {
  padding: 10px 20px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.upload-btn:hover {
  background: #3a7bc8;
}

.document-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f9f9f9;
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

td {
  color: #333;
  font-size: 14px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status.pending { background: #fdf6ec; color: #e6a23c; }
.status.parsing { background: #ecf5ff; color: #409eff; }
.status.indexed { background: #f0f9eb; color: #67c23a; }
.status.failed { background: #fef0f0; color: #f56c6c; }

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 16px;
}

.action-btn:hover {
  opacity: 0.7;
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: #999;
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
  width: 480px;
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

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-area.dragover {
  border-color: #4a90d9;
  background: #f0f9ff;
}

.upload-hint {
  pointer-events: none;
}

.upload-hint .icon {
  font-size: 48px;
}

.upload-hint p {
  margin: 12px 0 0 0;
  color: #666;
}

.formats {
  font-size: 12px;
  color: #999 !important;
}

.selected-file {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
}

.size {
  color: #999;
}

.progress-bar {
  margin-top: 16px;
  height: 4px;
  background: #eee;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4a90d9;
  transition: width 0.3s;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.cancel-btn,
.upload-confirm-btn,
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

.upload-confirm-btn,
.delete-btn {
  background: #4a90d9;
  border: none;
  color: white;
}

.delete-btn {
  background: #f56c6c;
}

.upload-confirm-btn:disabled {
  background: #ccc;
}

/* Confirm Modal */
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

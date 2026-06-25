<template>
  <div class="teams-page">
    <div class="page-header">
      <h1>团队管理</h1>
      <button class="btn-primary" @click="showCreateModal = true">创建团队</button>
    </div>

    <!-- Team List -->
    <div class="team-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="teams.length === 0" class="empty">暂无团队</div>
      <div v-else class="team-cards">
        <div v-for="team in teams" :key="team.id" class="team-card">
          <div class="team-info">
            <h3>{{ team.name }}</h3>
            <span class="member-count">{{ team.member_count }} 名成员</span>
          </div>
          <div class="team-actions">
            <button class="btn-small" @click="editTeam(team)">编辑</button>
            <button class="btn-small btn-danger" @click="confirmDelete(team)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <h3>{{ showEditModal ? '编辑团队' : '创建团队' }}</h3>
        <div class="form-group">
          <label>团队名称</label>
          <input v-model="teamForm.name" type="text" placeholder="请输入团队名称" />
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModals">取消</button>
          <button class="btn-primary" @click="showEditModal ? updateTeam() : createTeam()">
            {{ showEditModal ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <h3>确认删除</h3>
        <p>确定要删除团队 "{{ deleteTarget?.name }}" 吗？此操作不可撤销。</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn-danger" @click="deleteTeam">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { teamApi } from '@/api'

interface Team {
  id: string
  name: string
  member_count: number
}

const teams = ref<Team[]>([])
const loading = ref(false)

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const deleteTarget = ref<Team | null>(null)

const teamForm = ref({ id: '', name: '' })

async function fetchTeams() {
  loading.value = true
  try {
    teams.value = await teamApi.getTeams()
  } catch (e) {
    console.error('Failed to fetch teams:', e)
  } finally {
    loading.value = false
  }
}

function editTeam(team: Team) {
  teamForm.value = { id: team.id, name: team.name }
  showEditModal.value = true
}

function confirmDelete(team: Team) {
  deleteTarget.value = team
  showDeleteModal.value = true
}

async function createTeam() {
  if (!teamForm.value.name.trim()) return
  try {
    await teamApi.createTeam(teamForm.value.name)
    closeModals()
    fetchTeams()
  } catch (e) {
    console.error('Failed to create team:', e)
  }
}

async function updateTeam() {
  if (!teamForm.value.name.trim()) return
  try {
    await teamApi.updateTeam(teamForm.value.id, teamForm.value.name)
    closeModals()
    fetchTeams()
  } catch (e) {
    console.error('Failed to update team:', e)
  }
}

async function deleteTeam() {
  if (!deleteTarget.value) return
  try {
    await teamApi.deleteTeam(deleteTarget.value.id)
    showDeleteModal.value = false
    deleteTarget.value = null
    fetchTeams()
  } catch (e) {
    console.error('Failed to delete team:', e)
  }
}

function closeModals() {
  showCreateModal.value = false
  showEditModal.value = false
  teamForm.value = { id: '', name: '' }
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.teams-page {
  padding: 24px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.btn-primary {
  padding: 10px 20px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-danger {
  padding: 10px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-small {
  padding: 6px 12px;
  font-size: 14px;
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small.btn-danger {
  background: #dc3545;
  color: white;
}

.team-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.team-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.team-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.team-info h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.member-count {
  font-size: 14px;
  color: #999;
}

.team-actions {
  display: flex;
  gap: 8px;
}

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

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
}

.modal h3 {
  margin: 0 0 16px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>

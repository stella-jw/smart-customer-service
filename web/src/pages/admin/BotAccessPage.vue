<template>
  <div class="bot-access-page">
    <div class="page-header">
      <h1>机器人权限配置</h1>
    </div>

    <!-- Bot Selection -->
    <div class="bot-selector">
      <label>选择机器人：</label>
      <select v-model="selectedBotId" @change="loadBotAccess">
        <option value="">请选择机器人</option>
        <option v-for="bot in bots" :key="bot.id" :value="bot.id">
          {{ bot.name }} ({{ industryText[bot.industry_type] || bot.industry_type }})
        </option>
      </select>
    </div>

    <!-- Access Configuration -->
    <div v-if="selectedBotId" class="access-config">
      <div class="config-section">
        <h3>访问权限</h3>
        <div class="radio-group">
          <label class="radio-item">
            <input type="radio" v-model="accessType" value="all" />
            <span class="radio-label">
              <strong>所有人</strong>
              <small>所有用户（包括匿名用户）都可以使用此机器人</small>
            </span>
          </label>
          <label class="radio-item">
            <input type="radio" v-model="accessType" value="specific_users" />
            <span class="radio-label">
              <strong>指定用户</strong>
              <small>只有选定的用户可以使用此机器人</small>
            </span>
          </label>
          <label class="radio-item">
            <input type="radio" v-model="accessType" value="specific_teams" />
            <span class="radio-label">
              <strong>指定团队</strong>
              <small>只有指定团队的成员可以使用此机器人</small>
            </span>
          </label>
        </div>
      </div>

      <!-- Specific Users -->
      <div v-if="accessType === 'specific_users'" class="config-section">
        <h3>选择用户</h3>
        <div class="user-list">
          <div v-for="user in allUsers" :key="user.id" class="user-item">
            <input
              type="checkbox"
              :id="'user_' + user.id"
              :value="user.id"
              v-model="selectedUsers"
            />
            <label :for="'user_' + user.id">{{ user.username }}</label>
          </div>
        </div>
      </div>

      <!-- Specific Teams -->
      <div v-if="accessType === 'specific_teams'" class="config-section">
        <h3>选择团队</h3>
        <div class="team-list">
          <div v-for="team in teams" :key="team.id" class="team-item">
            <input
              type="checkbox"
              :id="'team_' + team.id"
              :value="team.id"
              v-model="selectedTeams"
            />
            <label :for="'team_' + team.id">{{ team.name }}</label>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="save-section">
        <button class="btn-primary" @click="saveAccess" :disabled="saving">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      请选择一个机器人来配置其访问权限
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi, teamApi } from '@/api'

interface Bot {
  id: string
  name: string
  industry_type: string
}

interface Team {
  id: string
  name: string
}

interface User {
  id: string
  username: string
}

const bots = ref<Bot[]>([])
const teams = ref<Team[]>([])
const allUsers = ref<User[]>([])

const selectedBotId = ref('')
const accessType = ref('all')
const selectedUsers = ref<string[]>([])
const selectedTeams = ref<string[]>([])
const saving = ref(false)

const industryText: Record<string, string> = {
  ecommerce: '电商',
  medical: '医疗',
  saas: 'SaaS',
  it: 'IT服务',
  general: '通用'
}

async function loadBots() {
  try {
    bots.value = await adminApi.getBots()
  } catch (e) {
    console.error('Failed to load bots:', e)
  }
}

async function loadTeams() {
  try {
    teams.value = await teamApi.getTeams()
  } catch (e) {
    console.error('Failed to load teams:', e)
  }
}

async function loadUsers() {
  try {
    allUsers.value = await adminApi.getUsers()
  } catch (e) {
    console.error('Failed to load users:', e)
  }
}

async function loadBotAccess() {
  if (!selectedBotId.value) return

  try {
    const access = await adminApi.getBotAccess(selectedBotId.value)
    accessType.value = access.access_type
    selectedUsers.value = access.allowed_users || []
    selectedTeams.value = access.allowed_teams || []
  } catch (e) {
    console.error('Failed to load bot access:', e)
    // Reset to defaults
    accessType.value = 'all'
    selectedUsers.value = []
    selectedTeams.value = []
  }
}

async function saveAccess() {
  if (!selectedBotId.value) return

  saving.value = true
  try {
    await adminApi.updateBotAccess(
      selectedBotId.value,
      accessType.value,
      selectedUsers.value,
      selectedTeams.value
    )
    alert('配置已保存')
  } catch (e) {
    console.error('Failed to save bot access:', e)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadBots()
  loadTeams()
  loadUsers()
})
</script>

<style scoped>
.bot-access-page {
  padding: 24px 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.bot-selector {
  margin-bottom: 24px;
  display: flex;
  align-items: left;
  gap: 12px;
}

.bot-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  min-width: 300px;
}

.access-config {
  background: white;
  border-radius: 8px;
  padding: 24px;
}

.config-section {
  margin-bottom: 24px;
}

.config-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
}

.radio-item:hover {
  background: #f9f9f9;
}

.radio-label {
  display: flex;
  flex-direction: column;
}

.radio-label small {
  color: #999;
  font-size: 12px;
}

.user-list, .team-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.user-item, .team-item {
  display: flex;
  align-items: left;
  gap: 6px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.user-item label, .team-item label {
  cursor: pointer;
}

.save-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.btn-primary {
  padding: 10px 24px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.empty-state {
  text-align: left;
  padding: 60px;
  background: white;
  border-radius: 8px;
  color: #999;
}
</style>

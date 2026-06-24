<template>
  <div class="dashboard-page">
    <h1>智能客服管理后台</h1>

    <div class="stats-grid">
      <router-link to="/admin/bots" class="stat-card clickable">
        <div class="stat-icon">🤖</div>
        <div class="stat-info">
          <span class="stat-value">{{ botCount }}/5</span>
          <span class="stat-label">机器人数量</span>
        </div>
      </router-link>

      <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.document_count || 0 }}</span>
          <span class="stat-label">文档总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.qa_pair_count || 0 }}</span>
          <span class="stat-label">QA对总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">💭</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.today_conversations || 0 }}</span>
          <span class="stat-label">今日对话</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avg_satisfaction || 0 }}%</span>
          <span class="stat-label">平均满意度</span>
        </div>
      </div>
    </div>

    <div class="metrics-section">
      <div class="metric-card">
        <h3>RAG命中率</h3>
        <div class="metric-value">{{ stats.rag_hit_rate || 0 }}%</div>
        <div class="metric-bar">
          <div class="metric-fill" :style="{ width: (stats.rag_hit_rate || 0) + '%' }"></div>
        </div>
      </div>

      <div class="metric-card">
        <h3>QA匹配率</h3>
        <div class="metric-value">{{ stats.qa_match_rate || 0 }}%</div>
        <div class="metric-bar">
          <div class="metric-fill qa" :style="{ width: (stats.qa_match_rate || 0) + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h2>快捷操作</h2>
      <div class="actions-grid">
        <router-link to="/admin/bots" class="action-card">
          <span class="icon">🤖</span>
          <span>机器人管理</span>
        </router-link>
        <router-link to="/admin/knowledge" class="action-card">
          <span class="icon">📚</span>
          <span>知识库管理</span>
        </router-link>
        <router-link to="/admin/qa" class="action-card">
          <span class="icon">❓</span>
          <span>QA维护</span>
        </router-link>
        <router-link to="/admin/config" class="action-card">
          <span class="icon">⚙️</span>
          <span>机器人配置</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'

const botCount = ref(0)
const stats = ref({
  document_count: 0,
  qa_pair_count: 0,
  total_conversations: 0,
  today_conversations: 0,
  avg_satisfaction: 0,
  rag_hit_rate: 0,
  qa_match_rate: 0
})

async function loadData() {
  try {
    const bots = await adminApi.getBots()
    botCount.value = bots.length
  } catch (e) {
    console.error('Failed to load bots:', e)
  }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.dashboard-page { padding: 24px; }

h1 { margin: 0 0 24px 0; font-size: 24px; color: #333; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-card.clickable {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon { font-size: 36px; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: 600; color: #333; }
.stat-label { font-size: 14px; color: #666; }

.metrics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.metric-card h3 { margin: 0 0 12px 0; font-size: 14px; color: #666; }
.metric-value { font-size: 32px; font-weight: 600; color: #4a90d9; margin-bottom: 12px; }

.metric-bar { height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
.metric-fill { height: 100%; background: linear-gradient(90deg, #4a90d9, #6ba3e0); border-radius: 4px; transition: width 0.5s ease; }
.metric-fill.qa { background: linear-gradient(90deg, #67c23a, #85ce61); }

.quick-actions h2 { font-size: 18px; color: #333; margin-bottom: 16px; }

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.action-card .icon { font-size: 32px; }
</style>

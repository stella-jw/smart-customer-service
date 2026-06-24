<template>
  <div class="dashboard">
    <h1>智能客服管理后台</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon documents">📄</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.document_count }}</span>
          <span class="stat-label">文档总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon qa">💬</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.qa_pair_count }}</span>
          <span class="stat-label">QA对总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon conversations">💭</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.today_conversations }}</span>
          <span class="stat-label">今日对话</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon satisfaction">⭐</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avg_satisfaction || 0 }}%</span>
          <span class="stat-label">平均满意度</span>
        </div>
      </div>
    </div>

    <!-- 趋势图 -->
    <div class="chart-section">
      <h2>对话趋势</h2>
      <div class="chart-placeholder">
        <p>近7天对话量: {{ stats.total_conversations }}</p>
      </div>
    </div>

    <!-- 命中率统计 -->
    <div class="metrics-row">
      <div class="metric-card">
        <h3>RAG命中率</h3>
        <div class="metric-value">{{ stats.rag_hit_rate }}%</div>
        <div class="metric-bar">
          <div class="metric-fill" :style="{ width: stats.rag_hit_rate + '%' }"></div>
        </div>
      </div>

      <div class="metric-card">
        <h3>QA匹配率</h3>
        <div class="metric-value">{{ stats.qa_match_rate }}%</div>
        <div class="metric-bar">
          <div class="metric-fill qa" :style="{ width: stats.qa_match_rate + '%' }"></div>
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

const stats = ref({
  document_count: 0,
  qa_pair_count: 0,
  total_conversations: 0,
  today_conversations: 0,
  avg_satisfaction: 0,
  rag_hit_rate: 0,
  qa_match_rate: 0
})

async function loadStats() {
  try {
    const response = await fetch(`/api/admin/analytics/${props.botId}`)
    const data = await response.json()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

h1 {
  margin: 0 0 24px 0;
  font-size: 24px;
  color: #333;
}

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

.stat-icon {
  font-size: 36px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chart-section h2 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.metric-card h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 32px;
  font-weight: 600;
  color: #4a90d9;
  margin-bottom: 12px;
}

.metric-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #4a90d9, #6ba3e0);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.metric-fill.qa {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}
</style>

<template>
  <div class="config-page">
    <div v-if="!currentBotId" class="no-bot">
      <p>请先在「机器人管理」中创建或选择一个机器人</p>
    </div>

    <template v-else>
      <h1>机器人配置</h1>
      <p class="bot-name">当前机器人: {{ currentBot?.name }}</p>

      <div class="config-sections">
        <section class="config-section">
          <h2>基础设置</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>机器人名称</label>
              <input v-model="config.name" type="text" />
            </div>
            <div class="form-group">
              <label>行业类型</label>
              <select v-model="config.industry_type">
                <option value="general">通用</option>
                <option value="ecommerce">电商</option>
                <option value="medical">医疗</option>
                <option value="saas">SaaS</option>
                <option value="it">IT服务</option>
              </select>
            </div>
          </div>
        </section>

        <section class="config-section">
          <h2>话术配置</h2>
          <div class="form-group">
            <label>欢迎消息</label>
            <input v-model="config.welcome_message" type="text" />
          </div>
          <div class="form-group">
            <label>开场白</label>
            <input v-model="config.opening_message" type="text" />
          </div>
          <div class="form-group">
            <label>兜底回复</label>
            <textarea v-model="config.fallback_message" rows="2"></textarea>
          </div>
        </section>

        <section class="config-section">
          <h2>机器人人格</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>性格类型</label>
              <select v-model="config.personality">
                <option value="friendly">亲切友好</option>
                <option value="professional">专业正式</option>
                <option value="humorous">轻松幽默</option>
                <option value="empathetic">富有同理心</option>
              </select>
            </div>
            <div class="form-group">
              <label>回复语气</label>
              <select v-model="config.response_tone">
                <option value="friendly">友好亲切</option>
                <option value="formal">正式严谨</option>
                <option value="casual">轻松随意</option>
                <option value="brief">简洁明了</option>
              </select>
            </div>
          </div>
        </section>

        <section class="config-section">
          <h2>功能开关</h2>
          <div class="toggle-grid">
            <div class="toggle-item">
              <span>启用知识库检索 (RAG)</span>
              <label class="toggle">
                <input type="checkbox" v-model="config.enable_rag" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="toggle-item">
              <span>启用QA匹配</span>
              <label class="toggle">
                <input type="checkbox" v-model="config.enable_qa_match" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="toggle-item">
              <span>启用闲聊</span>
              <label class="toggle">
                <input type="checkbox" v-model="config.enable_chitchat" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </section>

        <section class="config-section">
          <h2>检索参数</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>RAG检索数量 (top_k)</label>
              <input v-model.number="config.rag_top_k" type="number" min="1" max="20" />
            </div>
            <div class="form-group">
              <label>QA匹配阈值</label>
              <input v-model.number="config.qa_match_threshold" type="number" min="0" max="1" step="0.05" />
            </div>
          </div>
        </section>
      </div>

      <div class="actions">
        <button class="save-btn" @click="saveConfig" :disabled="saving">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { adminApi } from '@/api'
import { useBotStore } from '@/stores/botStore'

const { currentBotId, currentBot, fetchBots } = useBotStore()

const saving = ref(false)

const config = reactive({
  name: '',
  industry_type: 'general',
  welcome_message: '您好！有什么可以帮您的？',
  opening_message: '请问有什么可以帮您？',
  fallback_message: '抱歉，我没有找到相关答案，请联系人工客服获取帮助。',
  personality: 'friendly',
  response_tone: 'friendly',
  enable_rag: true,
  enable_qa_match: true,
  enable_chitchat: true,
  rag_top_k: 5,
  qa_match_threshold: 0.85
})

async function loadConfig() {
  if (!currentBotId.value) return
  try {
    const data = await adminApi.getBotConfig(currentBotId.value)
    if (data && Object.keys(data).length > 0) {
      Object.assign(config, data)
    }
    // Update name from currentBot
    if (currentBot.value) {
      config.name = currentBot.value.name
      config.industry_type = currentBot.value.industry_type
    }
  } catch (e) {
    console.error('Failed to load config:', e)
  }
}

async function saveConfig() {
  if (!currentBotId.value) return
  saving.value = true
  try {
    await adminApi.updateBotConfig(currentBotId.value, config)
    alert('配置保存成功！')
  } catch (e) {
    console.error('Failed to save config:', e)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

// Reload config when bot changes
watch(currentBotId, () => {
  loadConfig()
})

onMounted(async () => {
  await fetchBots()
  await loadConfig()
})
</script>

<style scoped>
.config-page { max-width: 800px; }

.no-bot {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.no-bot p {
  color: #666;
  font-size: 16px;
}

h1 { margin: 0 0 8px 0; font-size: 24px; color: #333; }

.bot-name {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #666;
}

.config-sections { display: flex; flex-direction: column; gap: 24px; }

.config-section {
  background: white; border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.config-section h2 {
  margin: 0 0 16px 0; font-size: 16px; color: #333;
  padding-bottom: 12px; border-bottom: 1px solid #eee;
}

.form-group { margin-bottom: 16px; }
.form-group:last-child { margin-bottom: 0; }

.form-group label { display: block; margin-bottom: 6px; font-size: 14px; color: #666; }

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%; padding: 10px 12px; border: 1px solid #ddd;
  border-radius: 8px; font-size: 14px; outline: none; box-sizing: border-box;
}

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.toggle-grid { display: flex; flex-direction: column; gap: 12px; }

.toggle-item {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 0;
}

.toggle {
  position: relative; display: inline-block; width: 48px; height: 24px;
}

.toggle input { opacity: 0; width: 0; height: 0; }

.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #ccc; transition: 0.3s; border-radius: 24px;
}

.slider:before {
  position: absolute; content: ""; height: 18px; width: 18px;
  left: 3px; bottom: 3px; background-color: white; transition: 0.3s; border-radius: 50%;
}

input:checked + .slider { background-color: #4a90d9; }
input:checked + .slider:before { transform: translateX(24px); }

.actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }

.save-btn {
  padding: 12px 24px; background: #4a90d9; color: white; border: none;
  border-radius: 8px; font-size: 14px; cursor: pointer;
}

.save-btn:disabled { background: #ccc; }
</style>

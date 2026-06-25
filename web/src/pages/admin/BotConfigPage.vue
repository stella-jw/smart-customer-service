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
          <h2>系统提示词</h2>
          <div class="form-group">
            <div class="system-prompt-header">
              <label>系统提示词</label>
              <button class="reset-btn" @click="resetToDefault">恢复默认</button>
            </div>
            <textarea
              v-model="config.system_prompt"
              :class="{ 'error': validationError }"
              rows="6"
              maxlength="1200"
              placeholder="输入系统提示词，用于定义机器人的角色设定和行为规则..."
            ></textarea>
            <div class="system-prompt-footer">
              <span class="char-count">{{ (config.system_prompt || '').length }} / 1200</span>
              <span v-if="validationError" class="error-text">{{ validationError }}</span>
            </div>
          </div>
          <div class="form-group">
            <label>默认提示词预览</label>
            <div class="default-prompt-preview">{{ defaultPromptPreview }}</div>
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { adminApi } from '@/api'
import { useBotStore } from '@/stores/botStore'

const { currentBotId, currentBot, fetchBots } = useBotStore()

const saving = ref(false)
const validationError = ref('')

const config = reactive({
  name: '',
  industry_type: 'general',
  welcome_message: '您好！有什么可以帮您的？',
  opening_message: '请问有什么可以帮您？',
  fallback_message: '抱歉，我没有找到相关答案，请联系人工客服获取帮助。',
  personality: 'friendly',
  response_tone: 'friendly',
  system_prompt: '',
  enable_rag: true,
  enable_qa_match: true,
  enable_chitchat: true,
  rag_top_k: 5,
  qa_match_threshold: 0.85
})

// 默认提示词模板
const defaultPrompts = {
  general: {
    friendly: "你是一个热情友好的智能客服助手，始终以积极的态度帮助用户解决问题。你的目标是让每位用户都感到受到尊重和重视。",
    professional: "你是一个专业严谨的智能客服助手，回答问题时条理清晰、言简意赅。你的目标是高效准确地解决用户问题。",
    humorous: "你是一个幽默风趣的智能客服助手，在保持专业的同时会用轻松的方式缓解用户的焦虑。",
    empathetic: "你是一个富有同理心的智能客服助手，善于理解用户的情感需求，给予温暖和关怀的回应。"
  },
  ecommerce: {
    friendly: "你是一家电商平台的热情客服助手，熟悉各类商品特点。你应该友好地与顾客交流，帮助他们找到满意的商品，耐心解答购物过程中的疑问。",
    professional: "你是一家电商平台的专业客服助手，精通商品知识、订单处理和售后流程。你的回答应该准确，专业，高效。",
    humorous: "你是电商平台的幽默客服，能在推荐商品和处理问题时带来轻松愉快的氛围，让购物体验更有趣。",
    empathetic: "你深度理解购物者的需求和担忧，无论是选择困难还是售后问题，都能给予充分的理解和贴心的建议。"
  },
  medical: {
    friendly: "你是一家医疗机构的专业客服助手，熟悉常见健康问题和医疗流程。请以亲切的态度回答用户的健康咨询，引导他们获得合适的医疗服务。",
    professional: "你是一位医疗领域的专业客服，具备扎实的医学知识。你的回答应该严谨准确，帮助用户正确理解健康信息。",
    humorous: "虽然医疗话题严肃，但你可以用温和的幽默缓解用户的紧张情绪，让沟通更加轻松。",
    empathetic: "你理解用户在健康问题上的焦虑，会给予充分的倾听和温暖的回应，同时引导专业医疗建议。"
  },
  it: {
    friendly: "你是一家IT公司的技术支持客服，擅长用通俗易懂的语言解释技术问题。你的服务态度热情耐心，让技术问题不再令人头疼。",
    professional: "你是一位资深技术支持工程师，技术功底扎实。你的回答应该准确，专业，能够快速定位和解决各类技术问题。",
    humorous: "你是IT界的幽默技术顾问，bug和宕机都不是事儿，用轻松的方式化解技术麻烦。",
    empathetic: "你理解技术人员和非技术用户在面对IT问题时的困惑和压力，给予耐心的指导和情绪支持。"
  },
  saas: {
    friendly: "你是SaaS产品的友好客服助手，熟悉产品功能和常见问题。你应该帮助用户快速上手，提供愉快的使用体验。",
    professional: "你是SaaS产品的专业客服专家，精通产品功能和最佳实践，帮助企业用户充分发挥产品价值。",
    humorous: "你是SaaS界的幽默顾问，让枯燥的功能介绍变得生动有趣。",
    empathetic: "你理解企业用户在选型和使用过程中的顾虑，提供贴心、专业的建议。"
  }
}

const defaultPromptPreview = computed(() => {
  const industry = config.industry_type || 'general'
  const personality = config.personality || 'friendly'
  return defaultPrompts[industry]?.[personality] || defaultPrompts.general.friendly
})

function resetToDefault() {
  config.system_prompt = defaultPromptPreview.value
  validateSystemPrompt()
}

function validateSystemPrompt() {
  const value = config.system_prompt || ''
  if (!value) {
    validationError.value = ''
    return true
  }
  // 只允许：中文、英文、数字、常用标点、空格、换行、email格式、电话号码格式
  const validPattern = /^[\u4e00-\u9fa5a-zA-Z0-9，。！？；：""''（）【】《》、·\-\s\n@.+@.+\..+|0\d{2,3}[-\s]?\d{7,8}|1[3-9]\d{9}]+$/
  // 禁止的特殊字符
  const invalidPattern = /[`${}%{}|<>\\=\!~\^&\*\|]+/
  if (invalidPattern.test(value)) {
    validationError.value = '系统提示词不能包含特殊符号'
    return false
  }
  validationError.value = ''
  return true
}

// 监听 system_prompt 变化进行验证
watch(() => config.system_prompt, () => {
  if (validationError.value) {
    validateSystemPrompt()
  }
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
  if (!validateSystemPrompt()) {
    alert('系统提示词格式不正确，请检查后重试')
    return
  }
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

.system-prompt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.system-prompt-header label {
  margin-bottom: 0;
}

.reset-btn {
  padding: 4px 12px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.reset-btn:hover {
  background: #eee;
}

.form-group textarea.error {
  border-color: #dc3545;
}

.system-prompt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
}

.char-count {
  color: #999;
}

.error-text {
  color: #dc3545;
}

.default-prompt-preview {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
}

.save-btn {
  padding: 12px 24px; background: #4a90d9; color: white; border: none;
  border-radius: 8px; font-size: 14px; cursor: pointer;
}

.save-btn:disabled { background: #ccc; }
</style>

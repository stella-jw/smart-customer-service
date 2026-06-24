<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>评价回答</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <p class="question">您对我的回答满意吗？</p>

        <div class="rating-stars">
          <span
            v-for="star in 5"
            :key="star"
            :class="['star', { active: star <= rating, hover: star <= hoverRating }]"
            @click="rating = star"
            @mouseenter="hoverRating = star"
            @mouseleave="hoverRating = 0"
          >
            ★
          </span>
        </div>

        <div v-if="rating > 0" class="feedback-section">
          <p class="feedback-label">请选择反馈原因（可选）:</p>
          <div class="feedback-options">
            <label v-for="option in feedbackOptions" :key="option.value">
              <input type="radio" v-model="feedbackReason" :value="option.value" />
              {{ option.label }}
            </label>
          </div>

          <textarea
            v-model="feedbackText"
            placeholder="其他意见或建议（可选）"
            rows="3"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="skip-btn" @click="$emit('close')">跳过</button>
        <button class="submit-btn" @click="submitRating" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交评价' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  conversationId: string
}>()

const emit = defineEmits<{
  close: []
  rated: []
}>()

const rating = ref(0)
const hoverRating = ref(0)
const feedbackReason = ref('')
const feedbackText = ref('')
const submitting = ref(false)

const feedbackOptions = [
  { value: 'inaccurate', label: '回答不准确' },
  { value: 'irrelevant', label: '不相关' },
  { value: 'incomplete', label: '不完整' },
  { value: 'other', label: '其他' }
]

async function submitRating() {
  if (rating.value === 0) return

  submitting.value = true

  try {
    await fetch('/api/rate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: props.conversationId,
        rating: rating.value,
        feedback: feedbackText.value || undefined,
        feedback_reason: feedbackReason.value || undefined
      })
    })

    emit('rated')
  } catch (error) {
    console.error('提交评价失败:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
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
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.question {
  text-align: center;
  font-size: 16px;
  color: #666;
  margin-bottom: 16px;
}

.rating-stars {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.star {
  font-size: 32px;
  color: #ddd;
  cursor: pointer;
  transition: color 0.2s, transform 0.2s;
}

.star.active,
.star.hover {
  color: #ffc107;
}

.star:hover {
  transform: scale(1.1);
}

.feedback-section {
  margin-top: 16px;
}

.feedback-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.feedback-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.feedback-options label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.feedback-options input {
  cursor: pointer;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  outline: none;
}

textarea:focus {
  border-color: #4a90d9;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.skip-btn,
.submit-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.skip-btn {
  background: none;
  border: 1px solid #ddd;
  color: #666;
}

.skip-btn:hover {
  background: #f5f5f5;
}

.submit-btn {
  background: #4a90d9;
  border: none;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #3a7bc8;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>

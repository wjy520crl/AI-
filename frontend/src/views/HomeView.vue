<template>
  <div class="home">
    <div class="input-section">
      <h2>📊 AI智能套定额</h2>
      <p class="subtitle">输入工程描述，AI自动匹配定额并计算工程造价</p>
      
      <div class="input-group">
        <label>✏️ 工程描述输入</label>
        <textarea v-model="description" :maxlength="2000" placeholder="请输入工程描述..."></textarea>
        <div class="char-count">{{ description.length }}/2000</div>
      </div>

      <div class="template-section">
        <label>📋 快速模板（点击填充）</label>
        <div class="template-tags">
          <span v-for="t in templates" :key="t.text" class="template-tag" @click="fillTemplate(t.text)">{{ t.label }}</span>
        </div>
      </div>

      <div class="quantity-group">
        <label>工程量：</label>
        <div class="quantity-input">
          <button @click="quantity = Math.max(0.01, quantity - 1)">−</button>
          <input type="number" v-model.number="quantity" step="0.01" min="0.01">
          <button @click="quantity += 1">+</button>
        </div>
      </div>

      <div class="button-group">
        <button class="btn-primary" @click="analyze" :disabled="!description || loading">
          {{ loading ? '🤖 AI分析中...' : '🚀 开始智能分析' }}
        </button>
        <button class="btn-secondary" @click="reset">🔄 重置</button>
      </div>
    </div>

    <div class="result-section" v-if="result">
      <h2>📋 分析结果</h2>
      <button class="btn-export" @click="exportExcel">📥 导出Excel</button>
      
      <div class="quota-list">
        <div v-for="item in result.items" :key="item.code" class="quota-card">
          <div class="quota-header">
            <span class="quota-code">{{ item.code }}</span>
            <span class="quota-name">{{ item.name }}</span>
            <span class="match-badge">🎯 {{ item.match_score }}%</span>
          </div>
          <div class="quota-costs">
            <div class="cost-item"><span>人工费</span><strong>¥{{ item.labor_cost }}</strong></div>
            <div class="cost-item"><span>材料费</span><strong>¥{{ item.material_cost }}</strong></div>
            <div class="cost-item"><span>机械费</span><strong>¥{{ item.machinery_cost }}</strong></div>
          </div>
          <div class="quota-total">综合合价 <strong>¥{{ item.subtotal }}</strong></div>
        </div>
      </div>

      <div class="summary-card">
        <h3>📈 工程造价汇总</h3>
        <div class="summary-grid">
          <div class="summary-item"><span>人工费</span><strong>¥{{ result.summary.total_labor }}</strong></div>
          <div class="summary-item"><span>材料费</span><strong>¥{{ result.summary.total_material }}</strong></div>
          <div class="summary-item"><span>机械费</span><strong>¥{{ result.summary.total_machinery }}</strong></div>
          <div class="summary-item"><span>管理费</span><strong>¥{{ result.summary.management_fee }}</strong></div>
          <div class="summary-item"><span>利润</span><strong>¥{{ result.summary.profit }}</strong></div>
          <div class="summary-item"><span>税金</span><strong>¥{{ result.summary.tax }}</strong></div>
        </div>
        <div class="total-section">
          <div class="total-label">工程总造价</div>
          <div class="total-value">¥{{ result.summary.total_amount }}</div>
        </div>
      </div>
    </div>

    <div class="result-section empty" v-else>
      <h2>📋 分析结果</h2>
      <p>输入工程描述后点击分析按钮</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const description = ref('')
const quantity = ref(1)
const loading = ref(false)
const result = ref(null)

const templates = [
  { label: '土方开挖', text: '挖基坑土方，深3米，宽2米，长度50米，采用机械开挖' },
  { label: '混凝土柱', text: '浇筑C30钢筋混凝土矩形柱10根，截面400x400mm，高度4米' },
  { label: '砖墙砌筑', text: '砌筑标准砖外墙，M5混合砂浆，墙体厚度240mm，体积15立方米' },
  { label: '墙面抹灰', text: '墙面一般抹灰，混合砂浆抹面，面积200平方米' },
  { label: '楼地面', text: '铺设陶瓷地砖楼地面，规格600x600mm，面积80平方米' },
  { label: '电气配线', text: '电气配线BV-2.5平方毫米，穿管暗敷，长度500米' },
]

const fillTemplate = (text) => { description.value = text }
const analyze = async () => {
  if (!description.value) return
  loading.value = true
  try {
    const response = await axios.post('/api/analyze', {
      description: description.value, quantity: quantity.value
    })
    result.value = response.data
  } catch (error) {
    alert('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
const reset = () => { description.value = ''; quantity.value = 1; result.value = null }
const exportExcel = () => { if (result.value?.id) window.open(`/api/export/excel/${result.value.id}`) }
</script>

<style scoped>
.home { padding: 24px; max-width: 1200px; margin: 0 auto; }
.input-section, .result-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
h2 { color: #1F2937; margin-bottom: 8px; }
.subtitle { color: #6B7280; margin-bottom: 20px; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; margin-bottom: 8px; font-weight: 600; }
textarea { width: 100%; height: 120px; padding: 12px; border: 1px solid #E5E7EB; border-radius: 8px; font-size: 14px; }
.char-count { text-align: right; color: #9CA3AF; font-size: 12px; }
.template-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.template-tag { background: #EEF2FF; color: #4F46E5; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px; }
.template-tag:hover { background: #4F46E5; color: #fff; }
.quantity-group { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.quantity-input { display: flex; align-items: center; border: 1px solid #E5E7EB; border-radius: 8px; overflow: hidden; }
.quantity-input button { background: #F3F4F6; border: none; padding: 8px 16px; cursor: pointer; font-size: 16px; }
.quantity-input input { width: 80px; border: none; text-align: center; padding: 8px; font-size: 14px; }
.button-group { display: flex; gap: 12px; }
.btn-primary { background: #4F46E5; color: #fff; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; }
.btn-primary:disabled { background: #9CA3AF; cursor: not-allowed; }
.btn-secondary { background: #F3F4F6; color: #374151; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; }
.btn-export { background: #10B981; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-bottom: 16px; }
.quota-list { display: flex
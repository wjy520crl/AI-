<template>
  <div class="history">
    <div class="header">
      <h2>📜 历史记录</h2>
      <button class="btn-danger" @click="clearAll">🗑️ 清空全部</button>
    </div>

    <table class="history-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>工程描述</th>
          <th>定额数</th>
          <th>总造价</th>
          <th>创建时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in histories" :key="h.id">
          <td>{{ h.id }}</td>
          <td>{{ h.description }}</td>
          <td>{{ h.item_count }}</td>
          <td>¥{{ h.total_amount }}</td>
          <td>{{ formatDate(h.created_at) }}</td>
          <td>
            <button class="btn-small" @click="viewDetail(h.id)">👁️</button>
            <button class="btn-small btn-success" @click="exportExcel(h.id)">📊</button>
            <button class="btn-small btn-danger" @click="deleteHistory(h.id)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="detail" class="detail-panel">
      <h3>详情 - {{ detail.description }}</h3>
      <pre>{{ JSON.stringify(detail.result, null, 2) }}</pre>
      <button @click="detail = null">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const histories = ref([])
const detail = ref(null)

const loadHistory = async () => {
  try {
    const res = await axios.get('/api/history')
    histories.value = res.data.items || []
  } catch (e) { console.error(e) }
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const viewDetail = async (id) => {
  try {
    const res = await axios.get(`/api/history/${id}`)
    detail.value = res.data
  } catch (e) { console.error(e) }
}

const exportExcel = (id) => {
  window.open(`/api/export/excel/${id}`)
}

const deleteHistory = async (id) => {
  if (confirm('确定删除?')) {
    await axios.delete(`/api/history/${id}`)
    loadHistory()
  }
}

const clearAll = async () => {
  if (confirm('确定清空所有历史记录?')) {
    await axios.delete('/api/history')
    histories.value = []
  }
}

onMounted(loadHistory)
</script>

<style scoped>
.history { padding: 24px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.history-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }
.history-table th, .history-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #E5E7EB; }
.history-table th { background: #F9FAFB; font-weight: 600; }
.btn-danger { background: #DC2626; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.btn-success { background: #10B981; color: #fff; }
.btn-small { padding: 6px 10px; border-radius: 4px; cursor: pointer; border: none; }
.detail-panel { background: #fff; padding: 24px; border-radius: 8px; margin-top: 20px; }
.detail-panel pre { background: #F3F4F6; padding: 16px; border-radius: 6px; overflow-x: auto; }
.detail-panel button { margin-top: 16px; padding: 8px 16px; background: #4F46E5; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
</style>

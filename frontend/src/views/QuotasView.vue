<template>
  <div class="quotas">
    <div class="header">
      <h2>📚 定额库管理</h2>
      <div class="controls">
        <input v-model="search" placeholder="搜索定额编号或名称" class="search-input" />
        <button class="btn-primary" @click="showAddDialog = true">➕ 新增定额</button>
      </div>
    </div>

    <table class="quota-table">
      <thead>
        <tr>
          <th>定额编号</th>
          <th>定额名称</th>
          <th>分类</th>
          <th>单位</th>
          <th>基价</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in filteredQuotas" :key="q.code">
          <td>{{ q.code }}</td>
          <td>{{ q.name }}</td>
          <td>{{ q.category }}</td>
          <td>{{ q.unit }}</td>
          <td>¥{{ q.base_price }}</td>
          <td>
            <button class="btn-small" @click="editQuota(q)">✏️</button>
            <button class="btn-small btn-danger" @click="deleteQuota(q.code)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++">下一页</button>
    </div>

    <div v-if="showAddDialog" class="dialog">
      <div class="dialog-content">
        <h3>{{ editingQuota ? '编辑' : '新增' }}定额</h3>
        <input v-model="form.code" placeholder="定额编号" />
        <input v-model="form.name" placeholder="定额名称" />
        <input v-model="form.category" placeholder="分类" />
        <input v-model="form.unit" placeholder="单位" />
        <input v-model.number="form.base_price" type="number" placeholder="基价" />
        <div class="dialog-buttons">
          <button @click="showAddDialog = false">取消</button>
          <button class="btn-primary" @click="saveQuota">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const quotas = ref([])
const search = ref('')
const page = ref(1)
const pageSize = 10
const showAddDialog = ref(false)
const editingQuota = ref(null)
const form = ref({ code: '', name: '', category: '', unit: '', base_price: 0 })

const filteredQuotas = computed(() => {
  const filtered = quotas.value.filter(q => 
    q.code.includes(search.value) || q.name.includes(search.value)
  )
  const start = (page.value - 1) * pageSize
  return filtered.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(quotas.value.length / pageSize))

const loadQuotas = async () => {
  try {
    const res = await axios.get('/api/quotas')
    quotas.value = res.data.items || []
  } catch (e) { console.error(e) }
}

const saveQuota = async () => {
  try {
    if (editingQuota.value) {
      await axios.put(`/api/quotas/${form.value.code}`, form.value)
    } else {
      await axios.post('/api/quotas', form.value)
    }
    showAddDialog.value = false
    loadQuotas()
  } catch (e) { alert('保存失败') }
}

const editQuota = (q) => {
  editingQuota.value = q
  form.value = { ...q }
  showAddDialog.value = true
}

const deleteQuota = async (code) => {
  if (confirm('确定删除?')) {
    await axios.delete(`/api/quotas/${code}`)
    loadQuotas()
  }
}

onMounted(loadQuotas)
</script>

<style scoped>
.quotas { padding: 24px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.controls { display: flex; gap: 12px; }
.search-input { padding: 10px 16px; border: 1px solid #E5E7EB; border-radius: 8px; width: 250px; }
.quota-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }
.quota-table th, .quota-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #E5E7EB; }
.quota-table th { background: #F9FAFB; font-weight: 600; }
.btn-primary { background: #4F46E5; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.btn-small { background: #F3F4F6; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; }
.btn-danger { background: #FEE2E2; color: #DC2626; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; }
.pagination button { padding: 8px 16px; background: #F3F4F6; border: none; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.dialog { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
.dialog-content { background: #fff; padding: 24px; border-radius: 12px; width: 400px; }
.dialog-content h3 { margin-bottom: 16px; }
.dialog-content input { width: 100%; padding: 10px; margin-bottom: 12px; border: 1px solid #E5E7EB; border-radius: 6px; box-sizing: border-box; }
.dialog-buttons { display: flex; gap: 12px; justify-content: flex-end; margin-top: 16px; }
.dialog-buttons button { padding: 10px 20px; border-radius: 6px; cursor: pointer; }
</style>

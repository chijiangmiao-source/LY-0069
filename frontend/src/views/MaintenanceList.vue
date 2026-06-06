<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="道具编号/名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="维保类型">
          <el-select
            v-model="filterForm.type"
            placeholder="请选择类型"
            clearable
            style="width: 150px"
          >
            <el-option label="维修" value="repair" />
            <el-option label="保养" value="maintenance" />
            <el-option label="复检" value="inspection" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增维保记录
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="prop_code" label="道具编号" width="140" />
        <el-table-column prop="prop_name" label="道具名称" width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            {{ getTypeText(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_date" label="日期" width="120" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'pass' ? 'success' : row.result === 'fail' ? 'danger' : 'warning'">
              {{ getResultText(row.result) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="费用" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="道具" prop="prop_id">
          <el-select
            v-model="formData.prop_id"
            placeholder="请选择道具"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in propList"
              :key="item.id"
              :label="`[${item.code}] ${item.name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维保类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择维保类型" style="width: 100%">
            <el-option label="维修" value="repair" />
            <el-option label="保养" value="maintenance" />
            <el-option label="复检" value="inspection" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保日期" prop="maintenance_date">
          <el-date-picker
            v-model="formData.maintenance_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="维保描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入维保描述"
          />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="formData.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="维保结果" prop="result">
          <el-select v-model="formData.result" placeholder="请选择结果" style="width: 100%">
            <el-option label="合格" value="pass" />
            <el-option label="不合格" value="fail" />
            <el-option label="待确认" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用">
          <el-input-number v-model="formData.cost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getMaintenanceRecords,
  createMaintenanceRecord,
  updateMaintenanceRecord,
  deleteMaintenanceRecord,
  getProps
} from '@/api/props'
import type { MaintenanceRecord, Prop } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增维保记录')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | string | null>(null)

const tableData = ref<MaintenanceRecord[]>([])
const propList = ref<Prop[]>([])

const filterForm = reactive({
  keyword: '',
  type: ''
})

const formData = reactive({
  prop_id: '',
  type: '',
  maintenance_date: '',
  description: '',
  operator: '',
  result: 'pending',
  cost: 0,
  remark: ''
})

const formRules: FormRules = {
  prop_id: [{ required: true, message: '请选择道具', trigger: 'change' }],
  type: [{ required: true, message: '请选择维保类型', trigger: 'change' }],
  maintenance_date: [{ required: true, message: '请选择维保日期', trigger: 'change' }],
  description: [{ required: true, message: '请输入维保描述', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入操作人', trigger: 'blur' }]
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    repair: '维修',
    maintenance: '保养',
    inspection: '复检'
  }
  return map[type] || type
}

const getResultText = (result: string) => {
  const map: Record<string, string> = {
    pass: '合格',
    fail: '不合格',
    pending: '待确认'
  }
  return map[result] || result
}

const fetchProps = async () => {
  try {
    const data = await getProps()
    propList.value = (data as any) || []
  } catch (e) {
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    let data = await getMaintenanceRecords() as any
    data = data || []
    if (filterForm.keyword) {
      const keyword = filterForm.keyword.toLowerCase()
      data = data.filter((item: MaintenanceRecord) =>
        (item.prop_code || '').toLowerCase().includes(keyword) ||
        (item.prop_name || '').toLowerCase().includes(keyword)
      )
    }
    if (filterForm.type) {
      data = data.filter((item: MaintenanceRecord) => item.type === filterForm.type)
    }
    tableData.value = data
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchList()
}

const handleReset = () => {
  filterForm.keyword = ''
  filterForm.type = ''
  fetchList()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增维保记录'
  editId.value = null
  formData.prop_id = ''
  formData.type = ''
  formData.maintenance_date = ''
  formData.description = ''
  formData.operator = ''
  formData.result = 'pending'
  formData.cost = 0
  formData.remark = ''
  dialogVisible.value = true
}

const handleEdit = (row: MaintenanceRecord) => {
  isEdit.value = true
  dialogTitle.value = '编辑维保记录'
  editId.value = row.id
  formData.prop_id = row.prop_id as any
  formData.type = row.type
  formData.maintenance_date = row.maintenance_date
  formData.description = row.description
  formData.operator = row.operator
  formData.result = row.result
  formData.cost = row.cost
  formData.remark = row.remark || ''
  dialogVisible.value = true
}

const handleDelete = (row: MaintenanceRecord) => {
  ElMessageBox.confirm(`确定要删除该维保记录吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteMaintenanceRecord(row.id)
        ElMessage.success('删除成功')
        fetchList()
      } catch (e) {
      }
    })
    .catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && editId.value) {
          await updateMaintenanceRecord(editId.value, formData)
          ElMessage.success('编辑成功')
        } else {
          await createMaintenanceRecord(formData)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        fetchList()
      } catch (e) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchProps()
  fetchList()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 16px 0;
}

.table-header {
  margin-bottom: 16px;
}
</style>

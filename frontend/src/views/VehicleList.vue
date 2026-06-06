<template>
  <div class="page-container">
    <el-card class="table-card">
      <div class="table-header">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增车辆
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="code" label="车辆编号" width="140" />
        <el-table-column prop="model" label="车型" width="180" />
        <el-table-column prop="capacity" label="承载容量" width="120" />
        <el-table-column prop="current_load" label="当前装载量" width="120" />
        <el-table-column prop="status" label="车辆状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="driver" label="责任司机" width="140" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
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
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="车辆编号" prop="code">
          <el-input v-model="formData.code" placeholder="请输入车辆编号" />
        </el-form-item>
        <el-form-item label="车型" prop="model">
          <el-input v-model="formData.model" placeholder="请输入车型" />
        </el-form-item>
        <el-form-item label="承载容量" prop="capacity">
          <el-input-number
            v-model="formData.capacity"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="当前装载量" prop="current_load">
          <el-input-number
            v-model="formData.current_load"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="车辆状态" prop="status">
          <el-select
            v-model="formData.status"
            placeholder="请选择状态"
            style="width: 100%"
          >
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任司机" prop="driver">
          <el-input v-model="formData.driver" placeholder="请输入责任司机" />
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
  getVehicles,
  createVehicle,
  updateVehicle,
  deleteVehicle
} from '@/api/vehicles'
import type { Vehicle } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增车辆')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | string | null>(null)

const tableData = ref<Vehicle[]>([])

const formData = reactive({
  code: '',
  model: '',
  capacity: 0,
  current_load: 0,
  status: 'active',
  driver: ''
})

const formRules: FormRules = {
  code: [{ required: true, message: '请输入车辆编号', trigger: 'blur' }],
  model: [{ required: true, message: '请输入车型', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入承载容量', trigger: 'blur' }]
}

const fetchList = async () => {
  loading.value = true
  try {
    const data = await getVehicles()
    tableData.value = data as any || []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增车辆'
  editId.value = null
  formData.code = ''
  formData.model = ''
  formData.capacity = 0
  formData.current_load = 0
  formData.status = 'active'
  formData.driver = ''
  dialogVisible.value = true
}

const handleEdit = (row: Vehicle) => {
  isEdit.value = true
  dialogTitle.value = '编辑车辆'
  editId.value = row.id
  formData.code = row.code
  formData.model = row.model
  formData.capacity = row.capacity
  formData.current_load = row.current_load
  formData.status = row.status
  formData.driver = row.driver
  dialogVisible.value = true
}

const handleDelete = (row: Vehicle) => {
  ElMessageBox.confirm(`确定要删除车辆「${row.code}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteVehicle(row.id)
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
        const data = {
          code: formData.code,
          model: formData.model,
          capacity: formData.capacity,
          current_load: formData.current_load,
          status: formData.status,
          driver: formData.driver
        }
        if (isEdit.value && editId.value) {
          await updateVehicle(editId.value, data)
          ElMessage.success('编辑成功')
        } else {
          await createVehicle(data)
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
  fetchList()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.table-header {
  margin-bottom: 16px;
}
</style>

<template>
  <div class="page-container">
    <div class="page-header">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增卸车
      </el-button>
    </div>

    <el-table :data="unloadingList" border stripe style="width: 100%">
      <el-table-column label="关联装车记录">
        <template #default="{ row }">
          <span>#{{ row.loading_id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="vehicle_code" label="车辆" />
      <el-table-column prop="prop_code" label="道具" />
      <el-table-column prop="unloading_date" label="卸车日期" width="140" />
      <el-table-column prop="unloading_quantity" label="卸车数量" width="110" />
      <el-table-column prop="operator" label="操作人" width="120" />
      <el-table-column prop="remark" label="备注" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑卸车' : '新增卸车'"
      width="560px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="装车记录" prop="loading_id">
          <el-select
            v-model="form.loading_id"
            placeholder="请选择装车记录"
            style="width: 100%"
            @change="handleLoadingChange"
          >
            <el-option
              v-for="item in availableLoadingOptions"
              :key="item.id"
              :label="`#${item.id} - ${item.loading_date} (数量: ${item.loading_quantity})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="车辆" prop="vehicle_id">
          <el-select v-model="form.vehicle_id" placeholder="请选择车辆" style="width: 100%">
            <el-option
              v-for="item in vehicleOptions"
              :key="item.id"
              :label="`${item.code} - ${item.model}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="道具" prop="prop_id">
          <el-select v-model="form.prop_id" placeholder="请选择道具" style="width: 100%">
            <el-option
              v-for="item in propOptions"
              :key="item.id"
              :label="`${item.code} - ${item.name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="卸车日期" prop="unloading_date">
          <el-date-picker
            v-model="form.unloading_date"
            type="date"
            placeholder="请选择卸车日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="卸车数量" prop="unloading_quantity">
          <el-input-number v-model="form.unloading_quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="form.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getLoadingList,
  getUnloadingList,
  createUnloading,
  getUnloading,
  updateUnloading,
  deleteUnloading
} from '@/api/loading'
import { getVehicles } from '@/api/vehicles'
import { getProps } from '@/api/props'
import type { LoadingRecord, UnloadingRecord, Vehicle, Prop } from '@/types'

const unloadingList = ref<UnloadingRecord[]>([])
const allLoadingList = ref<LoadingRecord[]>([])
const vehicleOptions = ref<Vehicle[]>([])
const propOptions = ref<Prop[]>([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | string | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  loading_id: null as number | null,
  vehicle_id: null as number | null,
  prop_id: null as number | null,
  unloading_date: '',
  unloading_quantity: 1,
  operator: '',
  remark: ''
})

const rules: FormRules = {
  loading_id: [{ required: true, message: '请选择装车记录', trigger: 'change' }],
  vehicle_id: [{ required: true, message: '请选择车辆', trigger: 'change' }],
  prop_id: [{ required: true, message: '请选择道具', trigger: 'change' }],
  unloading_date: [{ required: true, message: '请选择卸车日期', trigger: 'change' }],
  unloading_quantity: [{ required: true, message: '请输入卸车数量', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入操作人', trigger: 'blur' }]
}

const availableLoadingOptions = computed(() => {
  const usedLoadingIds = new Set(
    unloadingList.value
      .filter(item => !isEdit.value || item.id !== editId.value)
      .map(item => item.loading_id)
  )
  return allLoadingList.value.filter(item => !usedLoadingIds.has(item.id))
})

const fetchUnloadingList = async () => {
  const data = await getUnloadingList()
  unloadingList.value = data as UnloadingRecord[]
}

const fetchAllLoadingList = async () => {
  const data = await getLoadingList()
  allLoadingList.value = data as LoadingRecord[]
}

const fetchVehicleOptions = async () => {
  const data = await getVehicles()
  vehicleOptions.value = data as Vehicle[]
}

const fetchPropOptions = async () => {
  const data = await getProps()
  propOptions.value = data as Prop[]
}

const resetForm = () => {
  form.loading_id = null
  form.vehicle_id = null
  form.prop_id = null
  form.unloading_date = ''
  form.unloading_quantity = 1
  form.operator = ''
  form.remark = ''
  formRef.value?.resetFields()
  isEdit.value = false
  editId.value = null
}

const handleLoadingChange = (loadingId: number) => {
  const loading = allLoadingList.value.find(item => item.id === loadingId)
  if (loading) {
    form.vehicle_id = loading.vehicle_id
    form.prop_id = loading.prop_id
    form.unloading_quantity = loading.loading_quantity
  }
}

const handleAdd = async () => {
  await fetchAllLoadingList()
  await fetchVehicleOptions()
  await fetchPropOptions()
  dialogVisible.value = true
}

const handleEdit = async (row: UnloadingRecord) => {
  await fetchAllLoadingList()
  await fetchVehicleOptions()
  await fetchPropOptions()
  isEdit.value = true
  editId.value = row.id
  const data = (await getUnloading(row.id)) as UnloadingRecord
  form.loading_id = data.loading_id
  form.vehicle_id = data.vehicle_id
  form.prop_id = data.prop_id
  form.unloading_date = data.unloading_date
  form.unloading_quantity = data.unloading_quantity
  form.operator = data.operator
  form.remark = data.remark || ''
  dialogVisible.value = true
}

const handleDelete = (row: UnloadingRecord) => {
  ElMessageBox.confirm('确定要删除该卸车记录吗？此操作将同时恢复车辆装载量和道具状态。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteUnloading(row.id)
    ElMessage.success('删除成功')
    fetchUnloadingList()
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        loading_id: form.loading_id!,
        vehicle_id: form.vehicle_id!,
        prop_id: form.prop_id!,
        unloading_date: form.unloading_date,
        unloading_quantity: form.unloading_quantity,
        operator: form.operator,
        remark: form.remark || undefined
      }
      if (isEdit.value && editId.value) {
        await updateUnloading(editId.value, payload)
        ElMessage.success('编辑成功')
      } else {
        await createUnloading(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchUnloadingList()
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  fetchUnloadingList()
})
</script>

<style scoped>
.page-container {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}

.page-header {
  margin-bottom: 16px;
}
</style>

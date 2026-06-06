<template>
  <div class="page-container">
    <div class="page-header">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增损耗
      </el-button>
    </div>

    <el-table :data="damageList" border stripe style="width: 100%">
      <el-table-column prop="prop_code" label="道具" />
      <el-table-column prop="damage_date" label="损耗日期" width="140" />
      <el-table-column prop="damage_quantity" label="损耗数量" width="110" />
      <el-table-column prop="damage_reason" label="损耗原因" show-overflow-tooltip />
      <el-table-column prop="handler" label="处理人" width="120" />
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
      :title="isEdit ? '编辑损耗' : '新增损耗'"
      width="560px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
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
        <el-form-item label="损耗日期" prop="damage_date">
          <el-date-picker
            v-model="form.damage_date"
            type="date"
            placeholder="请选择损耗日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="损耗数量" prop="damage_quantity">
          <el-input-number v-model="form.damage_quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="损耗原因" prop="damage_reason">
          <el-input
            v-model="form.damage_reason"
            type="textarea"
            :rows="3"
            placeholder="请输入损耗原因"
          />
        </el-form-item>
        <el-form-item label="处理人" prop="handler">
          <el-input v-model="form.handler" placeholder="请输入处理人" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注（可选）" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getDamageList,
  createDamage,
  getDamage,
  updateDamage,
  deleteDamage
} from '@/api/loading'
import { getProps } from '@/api/props'
import type { DamageRecord, Prop } from '@/types'

const damageList = ref<DamageRecord[]>([])
const propOptions = ref<Prop[]>([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | string | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  prop_id: null as number | null,
  damage_date: '',
  damage_quantity: 1,
  damage_reason: '',
  handler: '',
  remark: ''
})

const rules: FormRules = {
  prop_id: [{ required: true, message: '请选择道具', trigger: 'change' }],
  damage_date: [{ required: true, message: '请选择损耗日期', trigger: 'change' }],
  damage_quantity: [{ required: true, message: '请输入损耗数量', trigger: 'blur' }],
  damage_reason: [{ required: true, message: '请输入损耗原因', trigger: 'blur' }],
  handler: [{ required: true, message: '请输入处理人', trigger: 'blur' }]
}

const fetchDamageList = async () => {
  const data = await getDamageList()
  damageList.value = data as DamageRecord[]
}

const fetchPropOptions = async () => {
  const data = await getProps()
  propOptions.value = data as Prop[]
}

const resetForm = () => {
  form.prop_id = null
  form.damage_date = ''
  form.damage_quantity = 1
  form.damage_reason = ''
  form.handler = ''
  form.remark = ''
  formRef.value?.resetFields()
  isEdit.value = false
  editId.value = null
}

const handleAdd = async () => {
  await fetchPropOptions()
  dialogVisible.value = true
}

const handleEdit = async (row: DamageRecord) => {
  await fetchPropOptions()
  isEdit.value = true
  editId.value = row.id
  const data = (await getDamage(row.id)) as DamageRecord
  form.prop_id = data.prop_id
  form.damage_date = data.damage_date
  form.damage_quantity = data.damage_quantity
  form.damage_reason = data.damage_reason
  form.handler = data.handler
  form.remark = data.remark || ''
  dialogVisible.value = true
}

const handleDelete = (row: DamageRecord) => {
  ElMessageBox.confirm('确定要删除该损耗记录吗？此操作将同时恢复道具状态为在库。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteDamage(row.id)
    ElMessage.success('删除成功')
    fetchDamageList()
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        prop_id: form.prop_id!,
        damage_date: form.damage_date,
        damage_quantity: form.damage_quantity,
        damage_reason: form.damage_reason,
        handler: form.handler,
        remark: form.remark || undefined
      }
      if (isEdit.value && editId.value) {
        await updateDamage(editId.value, payload)
        ElMessage.success('编辑成功')
      } else {
        await createDamage(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchDamageList()
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  fetchDamageList()
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

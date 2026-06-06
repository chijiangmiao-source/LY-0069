<template>
  <div v-loading="loading" class="program-container">
    <div class="page-header">
      <h3 class="page-title">剧目管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        <span>新增剧目</span>
      </el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table :data="programList" style="width: 100%" border>
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入剧目名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入剧目描述（可选）"
          />
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
import { getPrograms, createProgram, updateProgram, deleteProgram } from '@/api/programs'
import type { Program } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增剧目')
const isEdit = ref(false)
const editId = ref<number | string | null>(null)
const formRef = ref<FormInstance>()

const programList = ref<Program[]>([])

const formData = reactive({
  name: '',
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入剧目名称', trigger: 'blur' }]
}

const fetchList = async () => {
  loading.value = true
  try {
    const data = await getPrograms()
    programList.value = data
  } catch (e) {
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增剧目'
  editId.value = null
  dialogVisible.value = true
}

const handleEdit = (row: Program) => {
  isEdit.value = true
  dialogTitle.value = '编辑剧目'
  editId.value = row.id
  formData.name = row.name
  formData.description = row.description
  dialogVisible.value = true
}

const handleDelete = (row: Program) => {
  ElMessageBox.confirm(`确定要删除剧目「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteProgram(row.id)
        ElMessage.success('删除成功')
        fetchList()
      } catch (e) {
      }
    })
    .catch(() => {})
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && editId.value) {
          await updateProgram(editId.value, formData)
          ElMessage.success('编辑成功')
        } else {
          await createProgram(formData)
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
.program-container {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.table-card {
  border-radius: 4px;
}
</style>

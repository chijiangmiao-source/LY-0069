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
        <el-form-item label="所属剧目">
          <el-select
            v-model="filterForm.program_id"
            placeholder="请选择剧目"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="item in programList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="在库" value="in_store" />
            <el-option label="已装车" value="loaded" />
            <el-option label="已损坏" value="damaged" />
            <el-option label="已丢失" value="lost" />
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
          新增道具
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="code" label="道具编号" width="140" />
        <el-table-column prop="name" label="道具名称" width="180" />
        <el-table-column prop="program_name" label="所属剧目" width="180" />
        <el-table-column prop="material" label="材质" width="140" />
        <el-table-column prop="status" label="当前状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" />
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
      width="560px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="道具编号" prop="code">
          <el-input v-model="formData.code" placeholder="请输入道具编号" />
        </el-form-item>
        <el-form-item label="道具名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入道具名称" />
        </el-form-item>
        <el-form-item label="所属剧目" prop="program_id">
          <el-select
            v-model="formData.program_id"
            placeholder="请选择剧目"
            style="width: 100%"
          >
            <el-option
              v-for="item in programList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="材质" prop="material">
          <el-input v-model="formData.material" placeholder="请输入材质" />
        </el-form-item>
        <el-form-item label="当前状态" prop="status">
          <el-select
            v-model="formData.status"
            placeholder="请选择状态"
            style="width: 100%"
          >
            <el-option label="在库" value="in_store" />
            <el-option label="已装车" value="loaded" />
            <el-option label="已损坏" value="damaged" />
            <el-option label="已丢失" value="lost" />
          </el-select>
        </el-form-item>
        <el-form-item label="存放位置" prop="location">
          <el-input v-model="formData.location" placeholder="请输入存放位置" />
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
  getProps,
  createProp,
  updateProp,
  deleteProp
} from '@/api/props'
import { getPrograms } from '@/api/programs'
import type { Prop, Program } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增道具')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | string | null>(null)

const tableData = ref<Prop[]>([])
const programList = ref<Program[]>([])

const filterForm = reactive({
  keyword: '',
  program_id: '',
  status: ''
})

const formData = reactive({
  code: '',
  name: '',
  program_id: '',
  material: '',
  status: 'in_store',
  location: ''
})

const formRules: FormRules = {
  code: [{ required: true, message: '请输入道具编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入道具名称', trigger: 'blur' }],
  program_id: [{ required: true, message: '请选择所属剧目', trigger: 'change' }]
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    in_store: '在库',
    loaded: '已装车',
    damaged: '已损坏',
    lost: '已丢失'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    in_store: 'success',
    loaded: 'warning',
    damaged: 'danger',
    lost: 'info'
  }
  return map[status] || ''
}

const fetchPrograms = async () => {
  try {
    const data = await getPrograms()
    programList.value = data as any || []
  } catch (e) {
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params: any = { ...filterForm }
    if (!params.program_id) delete params.program_id
    if (!params.status) delete params.status
    const data = await getProps(params)
    tableData.value = data as any || []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchList()
}

const handleReset = () => {
  filterForm.keyword = ''
  filterForm.program_id = ''
  filterForm.status = ''
  fetchList()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增道具'
  editId.value = null
  formData.code = ''
  formData.name = ''
  formData.program_id = ''
  formData.material = ''
  formData.status = 'in_store'
  formData.location = ''
  dialogVisible.value = true
}

const handleEdit = (row: Prop) => {
  isEdit.value = true
  dialogTitle.value = '编辑道具'
  editId.value = row.id
  formData.code = row.code
  formData.name = row.name
  formData.program_id = row.program_id as any
  formData.material = row.material
  formData.status = row.status
  formData.location = row.location
  dialogVisible.value = true
}

const handleDelete = (row: Prop) => {
  ElMessageBox.confirm(`确定要删除道具「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteProp(row.id)
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
          name: formData.name,
          program_id: formData.program_id,
          material: formData.material,
          status: formData.status,
          location: formData.location
        }
        if (isEdit.value && editId.value) {
          await updateProp(editId.value, data)
          ElMessage.success('编辑成功')
        } else {
          await createProp(data)
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
  fetchPrograms()
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

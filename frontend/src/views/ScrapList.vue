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
        <el-form-item label="审批状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="prop_code" label="道具编号" width="140" />
        <el-table-column prop="prop_name" label="道具名称" width="180" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="apply_date" label="申请日期" width="120" />
        <el-table-column prop="reason" label="报废原因" />
        <el-table-column prop="status" label="审批状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver" label="审批人" width="100" />
        <el-table-column prop="approve_date" label="审批日期" width="120" />
        <el-table-column prop="approve_remark" label="审批意见" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link size="small" @click="handleApprove(row)">批准</el-button>
              <el-button type="danger" link size="small" @click="handleReject(row)">驳回</el-button>
            </template>
            <el-button type="info" link size="small" @click="handleView(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="approveDialogVisible"
      :title="`${approveAction === 'approve' ? '批准' : '驳回'}报废申请`"
      width="560px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="道具编号">
          <el-input v-model="currentRecord.prop_code" disabled />
        </el-form-item>
        <el-form-item label="道具名称">
          <el-input v-model="currentRecord.prop_name" disabled />
        </el-form-item>
        <el-form-item label="报废原因">
          <el-input v-model="currentRecord.reason" type="textarea" :rows="3" disabled />
        </el-form-item>
        <el-form-item label="审批人" prop="approver">
          <el-input v-model="formData.approver" placeholder="请输入审批人" />
        </el-form-item>
        <el-form-item label="审批日期" prop="approve_date">
          <el-date-picker
            v-model="formData.approve_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="审批意见" prop="approve_remark">
          <el-input
            v-model="formData.approve_remark"
            type="textarea"
            :rows="3"
            placeholder="请输入审批意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button
          :type="approveAction === 'approve' ? 'success' : 'danger'"
          :loading="submitLoading"
          @click="handleSubmitApprove"
        >
          {{ approveAction === 'approve' ? '确认批准' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  getScrapApplications,
  approveScrapApplication,
  rejectScrapApplication
} from '@/api/props'
import type { ScrapApplication } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const approveDialogVisible = ref(false)
const approveAction = ref<'approve' | 'reject'>('approve')
const formRef = ref<FormInstance>()
const currentRecord = ref<Partial<ScrapApplication>>({})

const tableData = ref<ScrapApplication[]>([])

const filterForm = reactive({
  keyword: '',
  status: ''
})

const formData = reactive({
  approver: '',
  approve_date: '',
  approve_remark: ''
})

const formRules: FormRules = {
  approver: [{ required: true, message: '请输入审批人', trigger: 'blur' }],
  approve_date: [{ required: true, message: '请选择审批日期', trigger: 'change' }]
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return map[status] || ''
}

const fetchList = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterForm.status) params.status = filterForm.status
    let data = await getScrapApplications(undefined, filterForm.status || undefined) as any
    data = data || []
    if (filterForm.keyword) {
      const keyword = filterForm.keyword.toLowerCase()
      data = data.filter((item: ScrapApplication) =>
        (item.prop_code || '').toLowerCase().includes(keyword) ||
        (item.prop_name || '').toLowerCase().includes(keyword)
      )
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
  filterForm.status = ''
  fetchList()
}

const handleApprove = (row: ScrapApplication) => {
  approveAction.value = 'approve'
  currentRecord.value = row
  formData.approver = ''
  formData.approve_date = ''
  formData.approve_remark = ''
  approveDialogVisible.value = true
}

const handleReject = (row: ScrapApplication) => {
  approveAction.value = 'reject'
  currentRecord.value = row
  formData.approver = ''
  formData.approve_date = ''
  formData.approve_remark = ''
  approveDialogVisible.value = true
}

const handleSubmitApprove = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (approveAction.value === 'approve') {
          await approveScrapApplication(currentRecord.value.id!, formData)
          ElMessage.success('已批准报废申请')
        } else {
          await rejectScrapApplication(currentRecord.value.id!, formData)
          ElMessage.success('已驳回报废申请')
        }
        approveDialogVisible.value = false
        fetchList()
      } catch (e) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleView = (row: ScrapApplication) => {
  currentRecord.value = row
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

.filter-card :deep(.el-card__body) {
  padding: 16px 16px 0;
}
</style>

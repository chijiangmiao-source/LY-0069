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
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保状态">
          <el-select
            v-model="filterForm.maintenance_status"
            placeholder="维保状态"
            clearable
            style="width: 150px"
          >
            <el-option label="正常" value="normal" />
            <el-option label="待维保" value="pending" />
            <el-option label="超期未维保" value="overdue" />
            <el-option label="维保中" value="in_maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="报废状态">
          <el-select
            v-model="filterForm.scrap_status"
            placeholder="报废状态"
            clearable
            style="width: 150px"
          >
            <el-option label="在用" value="active" />
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已报废" value="scrapped" />
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
        <el-table-column prop="status" label="当前状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_status" label="维保状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getMaintenanceStatusType(row.maintenance_status)">
              {{ getMaintenanceStatusText(row.maintenance_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scrap_status" label="报废状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getScrapStatusType(row.scrap_status)">
              {{ getScrapStatusText(row.scrap_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="next_maintenance_date" label="下次维保" width="120" />
        <el-table-column prop="location" label="存放位置" width="140" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="handleMaintenance(row)">维保登记</el-button>
            <el-button type="warning" link size="small" @click="handleScrapApply(row)">申请报废</el-button>
            <el-button type="info" link size="small" @click="handleViewRecords(row)">记录</el-button>
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
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="在库" value="in_store" />
            <el-option label="已装车" value="loaded" />
            <el-option label="已损坏" value="damaged" />
            <el-option label="已丢失" value="lost" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保周期(天)" prop="maintenance_cycle_days">
          <el-input-number v-model="formData.maintenance_cycle_days" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最近维保时间" prop="last_maintenance_date">
          <el-date-picker
            v-model="formData.last_maintenance_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
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

    <el-dialog
      v-model="maintenanceDialogVisible"
      title="维保登记"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="maintenanceFormRef"
        :model="maintenanceFormData"
        :rules="maintenanceFormRules"
        label-width="100px"
      >
        <el-form-item label="道具编号">
          <el-input v-model="currentProp.code" disabled />
        </el-form-item>
        <el-form-item label="道具名称">
          <el-input v-model="currentProp.name" disabled />
        </el-form-item>
        <el-form-item label="维保类型" prop="type">
          <el-select v-model="maintenanceFormData.type" placeholder="请选择维保类型" style="width: 100%">
            <el-option label="维修" value="repair" />
            <el-option label="保养" value="maintenance" />
            <el-option label="复检" value="inspection" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保日期" prop="maintenance_date">
          <el-date-picker
            v-model="maintenanceFormData.maintenance_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="维保描述" prop="description">
          <el-input
            v-model="maintenanceFormData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入维保描述"
          />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="maintenanceFormData.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="维保结果" prop="result">
          <el-select v-model="maintenanceFormData.result" placeholder="请选择结果" style="width: 100%">
            <el-option label="合格" value="pass" />
            <el-option label="不合格" value="fail" />
            <el-option label="待确认" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用">
          <el-input-number v-model="maintenanceFormData.cost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="maintenanceFormData.remark" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="maintenanceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitMaintenance">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="scrapDialogVisible"
      title="报废申请"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="scrapFormRef"
        :model="scrapFormData"
        :rules="scrapFormRules"
        label-width="100px"
      >
        <el-form-item label="道具编号">
          <el-input v-model="currentProp.code" disabled />
        </el-form-item>
        <el-form-item label="道具名称">
          <el-input v-model="currentProp.name" disabled />
        </el-form-item>
        <el-form-item label="申请人" prop="applicant">
          <el-input v-model="scrapFormData.applicant" placeholder="请输入申请人" />
        </el-form-item>
        <el-form-item label="申请日期" prop="apply_date">
          <el-date-picker
            v-model="scrapFormData.apply_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="报废原因" prop="reason">
          <el-input
            v-model="scrapFormData.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入报废原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scrapDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitScrap">提交申请</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="recordsDialogVisible"
      :title="`${currentProp.code} ${currentProp.name} - 相关记录`"
      width="900px"
      destroy-on-close
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="维保记录" name="maintenance">
          <el-table :data="maintenanceRecords" border stripe>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                {{ getMaintenanceTypeText(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="maintenance_date" label="日期" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="operator" label="操作人" width="100" />
            <el-table-column prop="result" label="结果" width="100">
              <template #default="{ row }">
                <el-tag :type="row.result === 'pass' ? 'success' : row.result === 'fail' ? 'danger' : 'warning'">
                  {{ getMaintenanceResultText(row.result) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cost" label="费用" width="100" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="报废申请" name="scrap">
          <el-table :data="scrapRecords" border stripe>
            <el-table-column prop="applicant" label="申请人" width="100" />
            <el-table-column prop="apply_date" label="申请日期" width="120" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getScrapStatusType(row.status)">
                  {{ getScrapStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="approver" label="审批人" width="100" />
            <el-table-column prop="approve_date" label="审批日期" width="120" />
            <el-table-column prop="approve_remark" label="审批意见" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
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
  deleteProp,
  createMaintenanceRecord,
  getMaintenanceRecords,
  getScrapApplications,
  createScrapApplication
} from '@/api/props'
import { getPrograms } from '@/api/programs'
import type { Prop, Program, MaintenanceRecord, ScrapApplication } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const maintenanceDialogVisible = ref(false)
const scrapDialogVisible = ref(false)
const recordsDialogVisible = ref(false)
const activeTab = ref('maintenance')
const dialogTitle = ref('新增道具')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const maintenanceFormRef = ref<FormInstance>()
const scrapFormRef = ref<FormInstance>()
const editId = ref<number | string | null>(null)
const currentProp = ref<Partial<Prop>>({})
const maintenanceRecords = ref<MaintenanceRecord[]>([])
const scrapRecords = ref<ScrapApplication[]>([])

const tableData = ref<Prop[]>([])
const programList = ref<Program[]>([])

const filterForm = reactive({
  keyword: '',
  program_id: '',
  status: '',
  maintenance_status: '',
  scrap_status: ''
})

const formData = reactive({
  code: '',
  name: '',
  program_id: '',
  material: '',
  status: 'in_store',
  maintenance_cycle_days: 90,
  last_maintenance_date: '',
  location: ''
})

const maintenanceFormData = reactive({
  type: '',
  maintenance_date: '',
  description: '',
  operator: '',
  result: 'pending',
  cost: 0,
  remark: ''
})

const scrapFormData = reactive({
  applicant: '',
  apply_date: '',
  reason: ''
})

const formRules: FormRules = {
  code: [{ required: true, message: '请输入道具编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入道具名称', trigger: 'blur' }],
  program_id: [{ required: true, message: '请选择所属剧目', trigger: 'change' }]
}

const maintenanceFormRules: FormRules = {
  type: [{ required: true, message: '请选择维保类型', trigger: 'change' }],
  maintenance_date: [{ required: true, message: '请选择维保日期', trigger: 'change' }],
  description: [{ required: true, message: '请输入维保描述', trigger: 'blur' }],
  operator: [{ required: true, message: '请输入操作人', trigger: 'blur' }]
}

const scrapFormRules: FormRules = {
  applicant: [{ required: true, message: '请输入申请人', trigger: 'blur' }],
  apply_date: [{ required: true, message: '请选择申请日期', trigger: 'change' }],
  reason: [{ required: true, message: '请输入报废原因', trigger: 'blur' }]
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    in_store: '在库',
    loaded: '已装车',
    damaged: '已损坏',
    lost: '已丢失',
    scrapped: '已报废'
  }
  return map[status] || status
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    in_store: 'success',
    loaded: 'warning',
    damaged: 'danger',
    lost: 'info',
    scrapped: 'info'
  }
  return map[status] || ''
}

const getMaintenanceStatusText = (status: string) => {
  const map: Record<string, string> = {
    normal: '正常',
    pending: '待维保',
    overdue: '超期未维保',
    in_maintenance: '维保中'
  }
  return map[status] || status
}

const getMaintenanceStatusType = (status: string) => {
  const map: Record<string, string> = {
    normal: 'success',
    pending: 'warning',
    overdue: 'danger',
    in_maintenance: 'primary'
  }
  return map[status] || ''
}

const getScrapStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '在用',
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    scrapped: '已报废'
  }
  return map[status] || status
}

const getScrapStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    pending: 'warning',
    approved: 'danger',
    rejected: 'info',
    scrapped: 'info'
  }
  return map[status] || ''
}

const getMaintenanceTypeText = (type: string) => {
  const map: Record<string, string> = {
    repair: '维修',
    maintenance: '保养',
    inspection: '复检'
  }
  return map[type] || type
}

const getMaintenanceResultText = (result: string) => {
  const map: Record<string, string> = {
    pass: '合格',
    fail: '不合格',
    pending: '待确认'
  }
  return map[result] || result
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
    if (!params.maintenance_status) delete params.maintenance_status
    if (!params.scrap_status) delete params.scrap_status
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
  filterForm.maintenance_status = ''
  filterForm.scrap_status = ''
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
  formData.maintenance_cycle_days = 90
  formData.last_maintenance_date = ''
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
  formData.maintenance_cycle_days = row.maintenance_cycle_days
  formData.last_maintenance_date = row.last_maintenance_date || ''
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
          maintenance_cycle_days: formData.maintenance_cycle_days,
          last_maintenance_date: formData.last_maintenance_date,
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

const handleMaintenance = (row: Prop) => {
  currentProp.value = row
  maintenanceFormData.type = ''
  maintenanceFormData.maintenance_date = ''
  maintenanceFormData.description = ''
  maintenanceFormData.operator = ''
  maintenanceFormData.result = 'pending'
  maintenanceFormData.cost = 0
  maintenanceFormData.remark = ''
  maintenanceDialogVisible.value = true
}

const handleSubmitMaintenance = async () => {
  if (!maintenanceFormRef.value) return
  await maintenanceFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createMaintenanceRecord({
          prop_id: currentProp.value.id,
          ...maintenanceFormData
        })
        ElMessage.success('维保登记成功')
        maintenanceDialogVisible.value = false
        fetchList()
      } catch (e) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleScrapApply = (row: Prop) => {
  if (row.scrap_status === 'scrapped' || row.scrap_status === 'approved') {
    ElMessage.warning('该道具已报废，无需再次申请')
    return
  }
  if (row.scrap_status === 'pending') {
    ElMessage.warning('该道具已有待审批的报废申请')
    return
  }
  currentProp.value = row
  scrapFormData.applicant = ''
  scrapFormData.apply_date = ''
  scrapFormData.reason = ''
  scrapDialogVisible.value = true
}

const handleSubmitScrap = async () => {
  if (!scrapFormRef.value) return
  await scrapFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createScrapApplication({
          prop_id: currentProp.value.id,
          ...scrapFormData
        })
        ElMessage.success('报废申请提交成功')
        scrapDialogVisible.value = false
        fetchList()
      } catch (e) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleViewRecords = async (row: Prop) => {
  currentProp.value = row
  activeTab.value = 'maintenance'
  try {
    const [mData, sData] = await Promise.all([
      getMaintenanceRecords(row.id),
      getScrapApplications(row.id)
    ])
    maintenanceRecords.value = (mData as any) || []
    scrapRecords.value = (sData as any) || []
  } catch (e) {
  }
  recordsDialogVisible.value = true
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

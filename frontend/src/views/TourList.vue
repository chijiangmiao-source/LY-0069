<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-select
        v-model="filters.status"
        placeholder="任务状态"
        clearable
        style="width: 140px"
        @change="fetchList"
      >
        <el-option label="待执行" value="pending" />
        <el-option label="执行中" value="in_progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
        <el-option label="异常" value="abnormal" />
      </el-select>
      <el-select
        v-model="filters.program_id"
        placeholder="剧目"
        clearable
        filterable
        style="width: 180px"
        @change="fetchList"
      >
        <el-option
          v-for="item in programOptions"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        />
      </el-select>
      <el-input
        v-model="filters.city"
        placeholder="演出城市"
        clearable
        style="width: 160px"
        @keyup.enter="fetchList"
      />
      <el-input
        v-model="filters.keyword"
        placeholder="搜索剧目/场馆/负责人"
        clearable
        style="width: 220px"
        @keyup.enter="fetchList"
      />
      <el-button type="primary" @click="fetchList">
        <el-icon><Search /></el-icon>
        查询
      </el-button>
      <el-button @click="resetFilters">重置</el-button>
    </div>

    <div class="page-header">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增巡演任务
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe>
      <el-table-column prop="program_name" label="剧目" min-width="140" />
      <el-table-column prop="performance_date" label="演出日期" width="120" />
      <el-table-column prop="city" label="演出城市" width="100" />
      <el-table-column prop="venue" label="场馆" min-width="160" show-overflow-tooltip />
      <el-table-column prop="person_in_charge" label="负责人" width="100" />
      <el-table-column label="任务周期" width="220">
        <template #default="{ row }">
          {{ row.start_date }} ~ {{ row.end_date }}
        </template>
      </el-table-column>
      <el-table-column label="任务状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行状态" width="100">
        <template #default="{ row }">
          <el-tag type="info">
            {{ getExecutionStatusText(row.execution_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="车辆" width="140">
        <template #default="{ row }">
          <span v-if="row.vehicles && row.vehicles.length">
            {{ row.vehicles.map(v => v.vehicle_code).join(', ') }}
          </span>
          <span v-else style="color: #909399">未分配</span>
        </template>
      </el-table-column>
      <el-table-column label="道具数" width="80">
        <template #default="{ row }">
          {{ (row.props || []).length }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleView(row)">详情</el-button>
          <el-button
            type="primary"
            link
            size="small"
            :disabled="row.status === 'completed' || row.status === 'cancelled'"
            @click="handleEdit(row)"
          >编辑</el-button>
          <el-button
            type="success"
            link
            size="small"
            :disabled="row.status === 'completed' || row.status === 'cancelled'"
            @click="handleStatus(row)"
          >状态</el-button>
          <el-button
            type="danger"
            link
            size="small"
            :disabled="row.status === 'in_progress'"
            @click="handleDelete(row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      destroy-on-close
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="剧目" prop="program_id">
              <el-select
                v-model="formData.program_id"
                placeholder="请选择剧目"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="item in programOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="演出日期" prop="performance_date">
              <el-date-picker
                v-model="formData.performance_date"
                type="date"
                placeholder="请选择演出日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="演出城市" prop="city">
              <el-input v-model="formData.city" placeholder="请输入演出城市" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场馆" prop="venue">
              <el-input v-model="formData.venue" placeholder="请输入场馆名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="负责人" prop="person_in_charge">
              <el-input v-model="formData.person_in_charge" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="formData.start_date"
                type="date"
                placeholder="请选择任务开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="formData.end_date"
                type="date"
                placeholder="请选择任务结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="参与车辆" prop="vehicle_ids">
          <el-select
            v-model="formData.vehicle_ids"
            multiple
            filterable
            placeholder="请选择参与车辆（可多选）"
            style="width: 100%"
          >
            <el-option
              v-for="item in vehicleOptions"
              :key="item.id"
              :label="`${item.code} - ${item.model}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联道具">
          <div class="prop-select-wrapper">
            <el-button
              type="primary"
              plain
              size="small"
              @click="openPropSelector = true"
            >
              <el-icon><Plus /></el-icon>
              选择道具
            </el-button>
            <div v-if="formData.props.length" class="selected-props">
              <div
                v-for="(prop, idx) in formData.props"
                :key="prop.prop_id"
                class="prop-item"
              >
                <span class="prop-info">
                  {{ getPropLabel(prop.prop_id) }}
                </span>
                <el-input-number
                  v-model="formData.props[idx].quantity"
                  :min="1"
                  size="small"
                  style="width: 120px"
                />
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="removeProp(idx)"
                >移除</el-button>
              </div>
            </div>
            <span v-else class="empty-tip">暂未选择道具</span>
          </div>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="statusDialogVisible"
      title="更新任务状态"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="statusFormRef"
        :model="statusForm"
        :rules="statusFormRules"
        label-width="100px"
      >
        <el-form-item label="任务状态" prop="status">
          <el-select v-model="statusForm.status" style="width: 100%">
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="statusForm.status === 'in_progress'" label="执行状态">
          <el-select v-model="statusForm.execution_status" clearable style="width: 100%">
            <el-option label="未开始" value="not_started" />
            <el-option label="筹备中" value="preparing" />
            <el-option label="运输中" value="transporting" />
            <el-option label="演出中" value="performing" />
            <el-option label="返程中" value="returning" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="statusForm.status === 'abnormal'" label="异常情况" prop="abnormal_situation">
          <el-input
            v-model="statusForm.abnormal_situation"
            type="textarea"
            :rows="3"
            placeholder="请填写异常情况描述"
          />
        </el-form-item>
        <el-form-item label="完成结果">
          <el-input
            v-model="statusForm.completion_result"
            type="textarea"
            :rows="2"
            placeholder="请输入完成结果（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="statusSubmitLoading" @click="handleStatusSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="viewDialogVisible"
      title="任务详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="viewData">
        <el-descriptions-item label="剧目">{{ viewData.program_name }}</el-descriptions-item>
        <el-descriptions-item label="演出日期">{{ viewData.performance_date }}</el-descriptions-item>
        <el-descriptions-item label="演出城市">{{ viewData.city }}</el-descriptions-item>
        <el-descriptions-item label="场馆">{{ viewData.venue }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ viewData.person_in_charge }}</el-descriptions-item>
        <el-descriptions-item label="任务周期">{{ viewData.start_date }} ~ {{ viewData.end_date }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getStatusTagType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行状态">{{ getExecutionStatusText(viewData.execution_status) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '无' }}</el-descriptions-item>
        <el-descriptions-item label="异常情况" :span="2">
          <span v-if="viewData.abnormal_situation" style="color: #f56c6c">{{ viewData.abnormal_situation }}</span>
          <span v-else style="color: #909399">无</span>
        </el-descriptions-item>
        <el-descriptions-item label="完成结果" :span="2">
          <span v-if="viewData.completion_result">{{ viewData.completion_result }}</span>
          <span v-else style="color: #909399">无</span>
        </el-descriptions-item>
      </el-descriptions>
      <div class="detail-section" v-if="viewData">
        <div class="section-title">参与车辆</div>
        <div v-if="viewData.vehicles && viewData.vehicles.length" class="detail-list">
          <el-tag v-for="v in viewData.vehicles" :key="v.id" style="margin: 4px">
            {{ v.vehicle_code }} - {{ v.vehicle_model }}
          </el-tag>
        </div>
        <span v-else style="color: #909399">未分配车辆</span>
      </div>
      <div class="detail-section" v-if="viewData">
        <div class="section-title">关联道具</div>
        <el-table v-if="viewData.props && viewData.props.length" :data="viewData.props" size="small" border>
          <el-table-column prop="prop_code" label="道具编号" width="140" />
          <el-table-column prop="prop_name" label="道具名称" />
          <el-table-column prop="quantity" label="数量" width="100" />
        </el-table>
        <span v-else style="color: #909399">未关联道具</span>
      </div>
    </el-dialog>

    <el-dialog
      v-model="openPropSelector"
      title="选择道具"
      width="700px"
      destroy-on-close
    >
      <div class="prop-selector-header">
        <el-input
          v-model="propSearchKeyword"
          placeholder="搜索道具编号/名称"
          clearable
          style="width: 260px"
        />
        <el-select
          v-model="propFilterProgram"
          placeholder="按剧目筛选"
          clearable
          filterable
          style="width: 180px"
        >
          <el-option
            v-for="item in programOptions"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>
      <el-table
        :data="filteredPropOptions"
        height="360"
        border
        @selection-change="handlePropSelectionChange"
        ref="propTableRef"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column label="所属剧目" width="140">
          <template #default="{ row }">
            {{ getProgramName(row.program_id) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="(row.scrap_status === 'scrapped' || row.maintenance_status === 'overdue') ? 'danger' : 'success'"
              size="small"
            >
              {{ row.scrap_status === 'scrapped' ? '已报废' : (row.maintenance_status === 'overdue' ? '维保超期' : '可用') }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="prop-tip" v-if="unavailableProps.length">
        <el-alert type="warning" :closable="false">
          <span>以下道具因已报废或维保超期不可选择：{{ unavailableProps.map(p => `${p.code} ${p.name}`).join('、') }}</span>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="openPropSelector = false">取消</el-button>
        <el-button type="primary" @click="confirmPropSelection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import {
  ElMessage, ElMessageBox, type FormInstance, type FormRules
} from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getTourTasks,
  createTourTask,
  updateTourTask,
  updateTourTaskStatus,
  deleteTourTask
} from '@/api/tours'
import { getPrograms } from '@/api/programs'
import { getVehicles } from '@/api/vehicles'
import { getProps } from '@/api/props'
import type { TourTask, Program, Vehicle, Prop } from '@/types'

const loading = ref(false)
const submitLoading = ref(false)
const statusSubmitLoading = ref(false)

const filters = reactive({
  status: '',
  program_id: null as number | string | null,
  city: '',
  keyword: ''
})

const tableData = ref<TourTask[]>([])
const programOptions = ref<Program[]>([])
const vehicleOptions = ref<Vehicle[]>([])
const propOptions = ref<Prop[]>([])

const dialogVisible = ref(false)
const dialogTitle = ref('新增巡演任务')
const isEdit = ref(false)
const editId = ref<number | string | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  program_id: null as number | string | null,
  performance_date: '',
  city: '',
  venue: '',
  person_in_charge: '',
  start_date: '',
  end_date: '',
  remark: '',
  vehicle_ids: [] as (number | string)[],
  props: [] as { prop_id: number | string; quantity: number }[]
})

const formRules: FormRules = {
  program_id: [{ required: true, message: '请选择剧目', trigger: 'change' }],
  performance_date: [{ required: true, message: '请选择演出日期', trigger: 'change' }],
  city: [{ required: true, message: '请输入演出城市', trigger: 'blur' }],
  venue: [{ required: true, message: '请输入场馆', trigger: 'blur' }],
  person_in_charge: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

const statusDialogVisible = ref(false)
const statusFormRef = ref<FormInstance>()
const statusEditId = ref<number | string | null>(null)
const statusForm = reactive({
  status: 'pending',
  execution_status: '',
  abnormal_situation: '',
  completion_result: ''
})

const statusFormRules: FormRules = {
  status: [{ required: true, message: '请选择任务状态', trigger: 'change' }],
  abnormal_situation: [{ required: true, message: '请填写异常情况', trigger: 'blur' }]
}

const viewDialogVisible = ref(false)
const viewData = ref<TourTask | null>(null)

const openPropSelector = ref(false)
const propSearchKeyword = ref('')
const propFilterProgram = ref<number | string | null>(null)
const propTableRef = ref()
const tempSelectedProps = ref<Prop[]>([])

const filteredPropOptions = computed(() => {
  let list = propOptions.value.filter(p =>
    p.scrap_status !== 'scrapped' && p.scrap_status !== 'approved' &&
    !(p.next_maintenance_date && new Date(p.next_maintenance_date) < new Date(new Date().toDateString()))
  )
  if (propSearchKeyword.value) {
    const kw = propSearchKeyword.value.toLowerCase()
    list = list.filter(p => p.code.toLowerCase().includes(kw) || p.name.toLowerCase().includes(kw))
  }
  if (propFilterProgram.value) {
    list = list.filter(p => p.program_id === propFilterProgram.value)
  }
  return list
})

const unavailableProps = computed(() => {
  return propOptions.value.filter(p =>
    p.scrap_status === 'scrapped' || p.scrap_status === 'approved' ||
    (p.next_maintenance_date && new Date(p.next_maintenance_date) < new Date(new Date().toDateString()))
  )
})

const getProgramName = (programId: number) => {
  const p = programOptions.value.find(x => x.id === programId)
  return p ? p.name : '-'
}

const getPropLabel = (propId: number | string) => {
  const p = propOptions.value.find(x => x.id === propId)
  return p ? `[${p.code}] ${p.name}` : String(propId)
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    in_progress: '执行中',
    completed: '已完成',
    cancelled: '已取消',
    abnormal: '异常'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'info',
    abnormal: 'danger'
  }
  return map[status] as any || 'info'
}

const getExecutionStatusText = (status: string) => {
  const map: Record<string, string> = {
    not_started: '未开始',
    preparing: '筹备中',
    transporting: '运输中',
    performing: '演出中',
    returning: '返程中',
    finished: '已结束'
  }
  return map[status] || status
}

const fetchList = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filters.status) params.status = filters.status
    if (filters.program_id) params.program_id = filters.program_id
    if (filters.city) params.city = filters.city
    if (filters.keyword) params.keyword = filters.keyword
    const data = await getTourTasks(params)
    tableData.value = data as any || []
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  const [programs, vehicles, props] = await Promise.all([
    getPrograms(),
    getVehicles({ status: 'active' }),
    getProps()
  ])
  programOptions.value = programs as any || []
  vehicleOptions.value = vehicles as any || []
  propOptions.value = props as any || []
}

const resetFilters = () => {
  filters.status = ''
  filters.program_id = null
  filters.city = ''
  filters.keyword = ''
  fetchList()
}

const resetForm = () => {
  formData.program_id = null
  formData.performance_date = ''
  formData.city = ''
  formData.venue = ''
  formData.person_in_charge = ''
  formData.start_date = ''
  formData.end_date = ''
  formData.remark = ''
  formData.vehicle_ids = []
  formData.props = []
  isEdit.value = false
  editId.value = null
  formRef.value?.resetFields()
}

const handleAdd = async () => {
  await fetchOptions()
  dialogTitle.value = '新增巡演任务'
  isEdit.value = false
  editId.value = null
  dialogVisible.value = true
}

const handleEdit = async (row: TourTask) => {
  await fetchOptions()
  dialogTitle.value = '编辑巡演任务'
  isEdit.value = true
  editId.value = row.id
  formData.program_id = row.program_id
  formData.performance_date = row.performance_date
  formData.city = row.city
  formData.venue = row.venue
  formData.person_in_charge = row.person_in_charge
  formData.start_date = row.start_date
  formData.end_date = row.end_date
  formData.remark = row.remark || ''
  formData.vehicle_ids = (row.vehicles || []).map(v => v.vehicle_id)
  formData.props = (row.props || []).map(p => ({ prop_id: p.prop_id, quantity: p.quantity }))
  dialogVisible.value = true
}

const handleView = (row: TourTask) => {
  viewData.value = row
  viewDialogVisible.value = true
}

const handleStatus = (row: TourTask) => {
  statusEditId.value = row.id
  statusForm.status = row.status
  statusForm.execution_status = row.execution_status
  statusForm.abnormal_situation = row.abnormal_situation || ''
  statusForm.completion_result = row.completion_result || ''
  statusDialogVisible.value = true
}

const handleDelete = (row: TourTask) => {
  ElMessageBox.confirm(`确定要删除巡演任务「${row.program_name} - ${row.city}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteTourTask(row.id)
        ElMessage.success('删除成功')
        fetchList()
      } catch (e) {}
    })
    .catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = {
        program_id: formData.program_id!,
        performance_date: formData.performance_date,
        city: formData.city,
        venue: formData.venue,
        person_in_charge: formData.person_in_charge,
        start_date: formData.start_date,
        end_date: formData.end_date,
        remark: formData.remark || undefined,
        vehicle_ids: formData.vehicle_ids,
        props: formData.props
      }
      if (isEdit.value && editId.value) {
        await updateTourTask(editId.value, payload)
        ElMessage.success('编辑成功')
      } else {
        await createTourTask(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchList()
    } catch (e) {} finally {
      submitLoading.value = false
    }
  })
}

const handleStatusSubmit = async () => {
  if (!statusFormRef.value) return
  await statusFormRef.value.validate(async (valid) => {
    if (!valid) return
    if (statusForm.status === 'abnormal' && !statusForm.abnormal_situation) {
      ElMessage.warning('请填写异常情况')
      return
    }
    statusSubmitLoading.value = true
    try {
      const payload: any = { status: statusForm.status }
      if (statusForm.execution_status) payload.execution_status = statusForm.execution_status
      if (statusForm.abnormal_situation) payload.abnormal_situation = statusForm.abnormal_situation
      if (statusForm.completion_result) payload.completion_result = statusForm.completion_result
      await updateTourTaskStatus(statusEditId.value!, payload)
      ElMessage.success('状态更新成功')
      statusDialogVisible.value = false
      fetchList()
    } catch (e) {} finally {
      statusSubmitLoading.value = false
    }
  })
}

const handlePropSelectionChange = (rows: Prop[]) => {
  tempSelectedProps.value = rows
}

const confirmPropSelection = async () => {
  const existingIds = new Set(formData.props.map(p => p.prop_id))
  for (const p of tempSelectedProps.value) {
    if (!existingIds.has(p.id)) {
      formData.props.push({ prop_id: p.id, quantity: 1 })
    }
  }
  openPropSelector.value = false
}

const removeProp = (idx: number) => {
  formData.props.splice(idx, 1)
}

onMounted(() => {
  fetchList()
  fetchOptions()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  background: #fff;
  padding: 16px;
  border-radius: 4px;
}

.page-header {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 0;
}

.prop-select-wrapper {
  width: 100%;
}

.selected-props {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prop-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.prop-info {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.empty-tip {
  display: block;
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.detail-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  margin-bottom: 10px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.detail-list {
  display: flex;
  flex-wrap: wrap;
}

.prop-selector-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.prop-tip {
  margin-top: 12px;
}
</style>

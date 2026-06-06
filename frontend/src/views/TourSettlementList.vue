<template>
  <div class="page-container">
    <el-tabs v-model="activeTab" class="settlement-tabs">
      <el-tab-pane label="成本项登记" name="cost">
        <div class="filter-bar">
          <el-select
            v-model="costFilters.tour_task_id"
            placeholder="巡演任务"
            clearable
            filterable
            style="width: 200px"
            @change="fetchCostItems"
          >
            <el-option
              v-for="item in taskOptions"
              :key="item.id"
              :label="`${item.program_name} - ${item.city} - ${item.performance_date}`"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-model="costFilters.cost_type"
            placeholder="费用类型"
            clearable
            style="width: 140px"
            @change="fetchCostItems"
          >
            <el-option
              v-for="item in costTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-select
            v-model="costFilters.program_id"
            placeholder="剧目"
            clearable
            filterable
            style="width: 160px"
            @change="fetchCostItems"
          >
            <el-option
              v-for="item in programOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-input
            v-model="costFilters.city"
            placeholder="演出城市"
            clearable
            style="width: 140px"
            @keyup.enter="fetchCostItems"
          />
          <el-date-picker
            v-model="costDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
            @change="handleCostDateChange"
          />
          <el-button type="primary" @click="fetchCostItems">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetCostFilters">重置</el-button>
        </div>

        <div class="page-header">
          <el-button type="primary" @click="handleAddCostItem">
            <el-icon><Plus /></el-icon>
            新增成本项
          </el-button>
          <div class="stats-summary">
            <el-tag type="info" size="large">总成本: ¥{{ formatMoney(costSummary.total) }}</el-tag>
            <el-tag v-for="t in costTypeOptions" :key="t.value" size="large" style="margin-left: 8px">
              {{ t.label }}: ¥{{ formatMoney(costSummary.byType[t.value] || 0) }}
            </el-tag>
          </div>
        </div>

        <el-table :data="costItemList" v-loading="costLoading" border stripe>
          <el-table-column prop="tour_task_name" label="巡演任务" min-width="220" show-overflow-tooltip />
          <el-table-column label="费用类型" width="120">
            <template #default="{ row }">
              <el-tag :type="row.cost_type === 'abnormal_handling' ? 'danger' : 'info'">
                {{ row.cost_type_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120" align="right">
            <template #default="{ row }">
              <span :class="{ 'abnormal-amount': row.is_abnormal_cost }">
                ¥{{ formatMoney(row.amount) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="费用说明" min-width="160" show-overflow-tooltip />
          <el-table-column prop="expense_date" label="发生日期" width="120" />
          <el-table-column prop="operator" label="经办人" width="100" />
          <el-table-column prop="receipt_no" label="票据编号" width="120" />
          <el-table-column label="异常费用" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_abnormal_cost" type="danger" size="small">是</el-tag>
              <span v-else style="color: #909399">否</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditCostItem(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteCostItem(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="结算单管理" name="settlement">
        <div class="filter-bar">
          <el-select
            v-model="settlementFilters.tour_task_id"
            placeholder="巡演任务"
            clearable
            filterable
            style="width: 200px"
            @change="fetchSettlements"
          >
            <el-option
              v-for="item in taskOptions"
              :key="item.id"
              :label="`${item.program_name} - ${item.city} - ${item.performance_date}`"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-model="settlementFilters.settlement_status"
            placeholder="结算状态"
            clearable
            style="width: 140px"
            @change="fetchSettlements"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
          <el-select
            v-model="settlementFilters.program_id"
            placeholder="剧目"
            clearable
            filterable
            style="width: 160px"
            @change="fetchSettlements"
          >
            <el-option
              v-for="item in programOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-input
            v-model="settlementFilters.city"
            placeholder="演出城市"
            clearable
            style="width: 140px"
            @keyup.enter="fetchSettlements"
          />
          <el-date-picker
            v-model="settlementDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
            @change="handleSettlementDateChange"
          />
          <el-button type="primary" @click="fetchSettlements">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetSettlementFilters">重置</el-button>
        </div>

        <div class="page-header">
          <el-button type="primary" @click="handleCreateSettlement">
            <el-icon><Plus /></el-icon>
            创建结算单
          </el-button>
          <div class="stats-summary">
            <el-tag type="success" size="large">
              已结算总成本: ¥{{ formatMoney(settlementSummary.total) }}
            </el-tag>
            <el-tag size="large" style="margin-left: 8px">
              结算任务数: {{ settlementSummary.count }}
            </el-tag>
            <el-tag type="warning" size="large" style="margin-left: 8px">
              平均成本: ¥{{ formatMoney(settlementSummary.avg) }}
            </el-tag>
          </div>
        </div>

        <el-table :data="settlementList" v-loading="settlementLoading" border stripe>
          <el-table-column prop="settlement_no" label="结算单号" width="160" />
          <el-table-column prop="program_name" label="剧目" min-width="140" />
          <el-table-column prop="city" label="城市" width="100" />
          <el-table-column prop="performance_date" label="演出日期" width="120" />
          <el-table-column label="任务状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getTaskStatusTagType(row.task_status)">
                {{ getTaskStatusText(row.task_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="结算状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getSettlementStatusTagType(row.settlement_status)">
                {{ getSettlementStatusText(row.settlement_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="总成本" width="120" align="right">
            <template #default="{ row }">
              <strong>¥{{ formatMoney(row.total_cost) }}</strong>
            </template>
          </el-table-column>
          <el-table-column label="异常费用" width="120" align="right">
            <template #default="{ row }">
              <span v-if="row.abnormal_handling_cost > 0" style="color: #f56c6c">
                ¥{{ formatMoney(row.abnormal_handling_cost) }}
              </span>
              <span v-else style="color: #909399">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="settler" label="结算人" width="100" />
          <el-table-column prop="settlement_date" label="结算日期" width="120" />
          <el-table-column label="操作" width="320" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleViewSettlement(row)">详情</el-button>
              <el-button
                type="success"
                link
                size="small"
                :disabled="row.settlement_status !== 'draft'"
                @click="handleRefreshSettlement(row)"
              >刷新</el-button>
              <el-button
                type="warning"
                link
                size="small"
                :disabled="row.settlement_status !== 'draft'"
                @click="handleSubmitSettlement(row)"
              >提交</el-button>
              <el-button
                type="success"
                link
                size="small"
                :disabled="row.settlement_status !== 'submitted'"
                @click="handleConfirmSettlement(row)"
              >确认</el-button>
              <el-button
                type="danger"
                link
                size="small"
                :disabled="row.settlement_status === 'confirmed'"
                @click="handleDeleteSettlement(row)"
              >删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="成本汇总统计" name="stats">
        <div class="filter-bar">
          <el-select
            v-model="statsFilters.program_id"
            placeholder="剧目"
            clearable
            filterable
            style="width: 160px"
            @change="fetchStats"
          >
            <el-option
              v-for="item in programOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-input
            v-model="statsFilters.city"
            placeholder="演出城市"
            clearable
            style="width: 140px"
            @keyup.enter="fetchStats"
          />
          <el-date-picker
            v-model="statsDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
            @change="handleStatsDateChange"
          />
          <el-button type="primary" @click="fetchStats">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </div>

        <el-row :gutter="20" class="stats-cards-row">
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">巡演总成本</div>
                <div class="stat-value primary">¥{{ formatMoney(costStats.total_cost) }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">已结算任务数</div>
                <div class="stat-value success">{{ costStats.task_count }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">单场平均成本</div>
                <div class="stat-value warning">¥{{ formatMoney(costStats.avg_cost_per_task) }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-item">
                <div class="stat-label">异常任务成本占比</div>
                <div class="stat-value danger">{{ costStats.abnormal_cost_ratio }}%</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="stats-charts-row">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span class="card-header-title">费用类型构成</span>
              </template>
              <div ref="costTypeChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span class="card-header-title">高成本剧目排行（Top 10）</span>
              </template>
              <div ref="programCostChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="costItemDialogVisible"
      :title="costItemDialogTitle"
      width="600px"
      destroy-on-close
      @close="resetCostItemForm"
    >
      <el-form
        ref="costItemFormRef"
        :model="costItemForm"
        :rules="costItemFormRules"
        label-width="100px"
      >
        <el-form-item label="巡演任务" prop="tour_task_id">
          <el-select
            v-model="costItemForm.tour_task_id"
            placeholder="请选择巡演任务"
            filterable
            style="width: 100%"
            :disabled="isEditCostItem"
          >
            <el-option
              v-for="item in taskOptions"
              :key="item.id"
              :label="`${item.program_name} - ${item.city} - ${item.performance_date}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="费用类型" prop="cost_type">
          <el-select v-model="costItemForm.cost_type" placeholder="请选择费用类型" style="width: 100%">
            <el-option
              v-for="item in costTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="costItemForm.amount"
            :min="0"
            :precision="2"
            :step="100"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="发生日期" prop="expense_date">
          <el-date-picker
            v-model="costItemForm.expense_date"
            type="date"
            placeholder="请选择费用发生日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用说明">
          <el-input v-model="costItemForm.description" placeholder="请输入费用说明（可选）" />
        </el-form-item>
        <el-form-item label="经办人">
          <el-input v-model="costItemForm.operator" placeholder="请输入经办人（可选）" />
        </el-form-item>
        <el-form-item label="票据编号">
          <el-input v-model="costItemForm.receipt_no" placeholder="请输入票据编号（可选）" />
        </el-form-item>
        <el-form-item label="异常费用">
          <el-switch v-model="costItemForm.is_abnormal_cost" />
        </el-form-item>
        <el-form-item
          v-if="costItemForm.is_abnormal_cost || costItemForm.cost_type === 'abnormal_handling'"
          label="异常说明"
          prop="abnormal_remark"
        >
          <el-input
            v-model="costItemForm.abnormal_remark"
            type="textarea"
            :rows="3"
            placeholder="请填写异常费用说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="costItemDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="costItemSubmitLoading" @click="handleCostItemSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="settlementSubmitDialogVisible"
      title="提交结算单"
      width="560px"
      destroy-on-close
    >
      <el-alert
        v-if="currentSettlement && currentSettlement.task_status === 'abnormal'"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      >
        该任务为异常任务，必须补充额外费用说明
      </el-alert>
      <el-form
        ref="settlementSubmitFormRef"
        :model="settlementSubmitForm"
        :rules="settlementSubmitFormRules"
        label-width="100px"
      >
        <el-form-item
          v-if="currentSettlement && currentSettlement.task_status === 'abnormal'"
          label="异常费用说明"
          prop="abnormal_cost_note"
        >
          <el-input
            v-model="settlementSubmitForm.abnormal_cost_note"
            type="textarea"
            :rows="4"
            placeholder="请补充异常任务的额外费用说明"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="settlementSubmitForm.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settlementSubmitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="settlementSubmitLoading" @click="doSubmitSettlement">确认提交</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="settlementViewVisible"
      title="结算单详情"
      width="700px"
    >
      <el-descriptions v-if="viewSettlement" :column="2" border>
        <el-descriptions-item label="结算单号">{{ viewSettlement.settlement_no }}</el-descriptions-item>
        <el-descriptions-item label="结算状态">
          <el-tag :type="getSettlementStatusTagType(viewSettlement.settlement_status)">
            {{ getSettlementStatusText(viewSettlement.settlement_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="剧目">{{ viewSettlement.program_name }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ viewSettlement.city }}</el-descriptions-item>
        <el-descriptions-item label="演出日期">{{ viewSettlement.performance_date }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getTaskStatusTagType(viewSettlement.task_status)">
            {{ getTaskStatusText(viewSettlement.task_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="运输费" align="right">¥{{ formatMoney(viewSettlement.transport_cost) }}</el-descriptions-item>
        <el-descriptions-item label="人工费" align="right">¥{{ formatMoney(viewSettlement.labor_cost) }}</el-descriptions-item>
        <el-descriptions-item label="场地费" align="right">¥{{ formatMoney(viewSettlement.venue_cost) }}</el-descriptions-item>
        <el-descriptions-item label="维保费" align="right">¥{{ formatMoney(viewSettlement.maintenance_cost) }}</el-descriptions-item>
        <el-descriptions-item label="临时采购费" align="right">¥{{ formatMoney(viewSettlement.temporary_purchase_cost) }}</el-descriptions-item>
        <el-descriptions-item label="异常处理费" align="right">
          <span :style="{ color: viewSettlement.abnormal_handling_cost > 0 ? '#f56c6c' : '' }">
            ¥{{ formatMoney(viewSettlement.abnormal_handling_cost) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="总成本" :span="2" align="right">
          <strong style="font-size: 18px; color: #409eff">
            ¥{{ formatMoney(viewSettlement.total_cost) }}
          </strong>
        </el-descriptions-item>
        <el-descriptions-item label="异常费用说明" :span="2">
          {{ viewSettlement.abnormal_cost_note || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="结算人">{{ viewSettlement.settler || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结算日期">{{ viewSettlement.settlement_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewSettlement.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getCostItems,
  createCostItem,
  updateCostItem,
  deleteCostItem,
  getSettlements,
  createSettlement,
  refreshSettlement,
  submitSettlement,
  confirmSettlement,
  deleteSettlement,
  getCostStatsSummary,
  getCostStatsByProgram
} from '@/api/tours'
import { getPrograms } from '@/api/programs'
import { getTourTasks } from '@/api/tours'
import type {
  TourCostItem,
  TourSettlement,
  TourCostStats,
  ProgramCostRank,
  Program,
  TourTask
} from '@/types'

const activeTab = ref('cost')

const costTypeOptions = [
  { value: 'transport', label: '运输费' },
  { value: 'labor', label: '人工费' },
  { value: 'venue', label: '场地费' },
  { value: 'maintenance', label: '维保费' },
  { value: 'temporary_purchase', label: '临时采购费' },
  { value: 'abnormal_handling', label: '异常处理费' }
]

const formatMoney = (v: number) => {
  return (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    in_progress: '执行中',
    completed: '已完成',
    cancelled: '已取消',
    abnormal: '异常'
  }
  return map[status] || status
}

const getTaskStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'info',
    abnormal: 'danger'
  }
  return map[status] as any || 'info'
}

const getSettlementStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    submitted: '已提交',
    confirmed: '已确认'
  }
  return map[status] || status
}

const getSettlementStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    submitted: 'warning',
    confirmed: 'success'
  }
  return map[status] as any || 'info'
}

const programOptions = ref<Program[]>([])
const taskOptions = ref<TourTask[]>([])

const costLoading = ref(false)
const costItemList = ref<TourCostItem[]>([])
const costFilters = reactive({
  tour_task_id: null as number | string | null,
  cost_type: '',
  program_id: null as number | string | null,
  city: ''
})
const costDateRange = ref<string[]>([])

const costSummary = computed(() => {
  const total = costItemList.value.reduce((s, i) => s + i.amount, 0)
  const byType: Record<string, number> = {}
  for (const item of costItemList.value) {
    byType[item.cost_type] = (byType[item.cost_type] || 0) + item.amount
  }
  return { total, byType }
})

const costItemDialogVisible = ref(false)
const costItemDialogTitle = ref('新增成本项')
const isEditCostItem = ref(false)
const editCostItemId = ref<number | string | null>(null)
const costItemFormRef = ref<FormInstance>()
const costItemSubmitLoading = ref(false)

const costItemForm = reactive({
  tour_task_id: null as number | string | null,
  cost_type: 'transport',
  amount: 0,
  description: '',
  expense_date: '',
  operator: '',
  receipt_no: '',
  is_abnormal_cost: false,
  abnormal_remark: ''
})

const costItemFormRules: FormRules = {
  tour_task_id: [{ required: true, message: '请选择巡演任务', trigger: 'change' }],
  cost_type: [{ required: true, message: '请选择费用类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  expense_date: [{ required: true, message: '请选择费用发生日期', trigger: 'change' }],
  abnormal_remark: [{ required: true, message: '请填写异常费用说明', trigger: 'blur' }]
}

const settlementLoading = ref(false)
const settlementList = ref<TourSettlement[]>([])
const settlementFilters = reactive({
  tour_task_id: null as number | string | null,
  settlement_status: '',
  program_id: null as number | string | null,
  city: ''
})
const settlementDateRange = ref<string[]>([])

const settlementSummary = computed(() => {
  const submitted = settlementList.value.filter(
    s => s.settlement_status === 'submitted' || s.settlement_status === 'confirmed'
  )
  const total = submitted.reduce((s, i) => s + i.total_cost, 0)
  const count = submitted.length
  return { total, count, avg: count > 0 ? total / count : 0 }
})

const settlementViewVisible = ref(false)
const viewSettlement = ref<TourSettlement | null>(null)

const settlementSubmitDialogVisible = ref(false)
const currentSettlement = ref<TourSettlement | null>(null)
const settlementSubmitFormRef = ref<FormInstance>()
const settlementSubmitLoading = ref(false)
const settlementSubmitForm = reactive({
  abnormal_cost_note: '',
  remark: ''
})

const settlementSubmitFormRules: FormRules = {
  abnormal_cost_note: [{ required: true, message: '请补充异常费用说明', trigger: 'blur' }]
}

const costStats = reactive<TourCostStats>({
  total_cost: 0,
  transport_cost: 0,
  labor_cost: 0,
  venue_cost: 0,
  maintenance_cost: 0,
  temporary_purchase_cost: 0,
  abnormal_handling_cost: 0,
  task_count: 0,
  avg_cost_per_task: 0,
  abnormal_cost_ratio: 0
})
const programCostRankList = ref<ProgramCostRank[]>([])
const statsFilters = reactive({
  program_id: null as number | string | null,
  city: ''
})
const statsDateRange = ref<string[]>([])

const costTypeChartRef = ref<HTMLElement | null>(null)
const programCostChartRef = ref<HTMLElement | null>(null)
let costTypeChartInstance: ECharts | null = null
let programCostChartInstance: ECharts | null = null

const fetchOptions = async () => {
  const [programs, tasks] = await Promise.all([
    getPrograms(),
    getTourTasks()
  ])
  programOptions.value = programs as any || []
  taskOptions.value = tasks as any || []
}

const fetchCostItems = async () => {
  costLoading.value = true
  try {
    const params: any = {}
    if (costFilters.tour_task_id) params.tour_task_id = costFilters.tour_task_id
    if (costFilters.cost_type) params.cost_type = costFilters.cost_type
    if (costFilters.program_id) params.program_id = costFilters.program_id
    if (costFilters.city) params.city = costFilters.city
    if (costDateRange.value && costDateRange.value.length === 2) {
      params.start_date = costDateRange.value[0]
      params.end_date = costDateRange.value[1]
    }
    const data = await getCostItems(params)
    costItemList.value = data as any || []
  } finally {
    costLoading.value = false
  }
}

const resetCostFilters = () => {
  costFilters.tour_task_id = null
  costFilters.cost_type = ''
  costFilters.program_id = null
  costFilters.city = ''
  costDateRange.value = []
  fetchCostItems()
}

const handleCostDateChange = () => {
  fetchCostItems()
}

const resetCostItemForm = () => {
  costItemForm.tour_task_id = null
  costItemForm.cost_type = 'transport'
  costItemForm.amount = 0
  costItemForm.description = ''
  costItemForm.expense_date = ''
  costItemForm.operator = ''
  costItemForm.receipt_no = ''
  costItemForm.is_abnormal_cost = false
  costItemForm.abnormal_remark = ''
  isEditCostItem.value = false
  editCostItemId.value = null
  costItemFormRef.value?.resetFields()
}

const handleAddCostItem = async () => {
  await fetchOptions()
  costItemDialogTitle.value = '新增成本项'
  isEditCostItem.value = false
  editCostItemId.value = null
  costItemDialogVisible.value = true
}

const handleEditCostItem = async (row: TourCostItem) => {
  await fetchOptions()
  costItemDialogTitle.value = '编辑成本项'
  isEditCostItem.value = true
  editCostItemId.value = row.id
  costItemForm.tour_task_id = row.tour_task_id
  costItemForm.cost_type = row.cost_type
  costItemForm.amount = row.amount
  costItemForm.description = row.description || ''
  costItemForm.expense_date = row.expense_date
  costItemForm.operator = row.operator || ''
  costItemForm.receipt_no = row.receipt_no || ''
  costItemForm.is_abnormal_cost = row.is_abnormal_cost
  costItemForm.abnormal_remark = row.abnormal_remark || ''
  costItemDialogVisible.value = true
}

const handleDeleteCostItem = (row: TourCostItem) => {
  ElMessageBox.confirm(
    `确定要删除该成本项「${row.cost_type_display} - ¥${formatMoney(row.amount)}」吗？`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  )
    .then(async () => {
      try {
        await deleteCostItem(row.id)
        ElMessage.success('删除成功')
        fetchCostItems()
      } catch (e) {}
    })
    .catch(() => {})
}

const handleCostItemSubmit = async () => {
  if (!costItemFormRef.value) return
  const needAbnormalRemark = costItemForm.is_abnormal_cost || costItemForm.cost_type === 'abnormal_handling'
  if (needAbnormalRemark && !costItemForm.abnormal_remark) {
    ElMessage.warning('请填写异常费用说明')
    return
  }
  await costItemFormRef.value.validate(async (valid) => {
    if (!valid) return
    costItemSubmitLoading.value = true
    try {
      const payload: any = {
        tour_task_id: costItemForm.tour_task_id!,
        cost_type: costItemForm.cost_type,
        amount: costItemForm.amount,
        expense_date: costItemForm.expense_date,
        description: costItemForm.description || undefined,
        operator: costItemForm.operator || undefined,
        receipt_no: costItemForm.receipt_no || undefined,
        is_abnormal_cost: costItemForm.is_abnormal_cost,
        abnormal_remark: costItemForm.abnormal_remark || undefined
      }
      if (isEditCostItem.value && editCostItemId.value) {
        const updatePayload = { ...payload }
        delete updatePayload.tour_task_id
        await updateCostItem(editCostItemId.value, updatePayload)
        ElMessage.success('编辑成功')
      } else {
        await createCostItem(payload)
        ElMessage.success('新增成功')
      }
      costItemDialogVisible.value = false
      fetchCostItems()
    } catch (e) {} finally {
      costItemSubmitLoading.value = false
    }
  })
}

const fetchSettlements = async () => {
  settlementLoading.value = true
  try {
    const params: any = {}
    if (settlementFilters.tour_task_id) params.tour_task_id = settlementFilters.tour_task_id
    if (settlementFilters.settlement_status) params.settlement_status = settlementFilters.settlement_status
    if (settlementFilters.program_id) params.program_id = settlementFilters.program_id
    if (settlementFilters.city) params.city = settlementFilters.city
    if (settlementDateRange.value && settlementDateRange.value.length === 2) {
      params.start_date = settlementDateRange.value[0]
      params.end_date = settlementDateRange.value[1]
    }
    const data = await getSettlements(params)
    settlementList.value = data as any || []
  } finally {
    settlementLoading.value = false
  }
}

const resetSettlementFilters = () => {
  settlementFilters.tour_task_id = null
  settlementFilters.settlement_status = ''
  settlementFilters.program_id = null
  settlementFilters.city = ''
  settlementDateRange.value = []
  fetchSettlements()
}

const handleSettlementDateChange = () => {
  fetchSettlements()
}

const handleCreateSettlement = async () => {
  await fetchOptions()
  const eligibleTasks = taskOptions.value.filter(t => t.status !== 'cancelled')
  if (!eligibleTasks.length) {
    ElMessage.warning('暂无可生成结算单的任务')
    return
  }
  const taskSelectOptions = eligibleTasks.map(t => ({
    label: `${t.program_name} - ${t.city} - ${t.performance_date} [${getTaskStatusText(t.status)}]`,
    value: t.id
  }))
  ElMessageBox.prompt('请选择要创建结算单的巡演任务', '创建结算单', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputType: 'select',
    inputValidator: (v) => !!v || '请选择巡演任务',
    inputOptions: taskSelectOptions as any
  } as any)
    .then(async ({ value }) => {
      try {
        await createSettlement({ tour_task_id: value })
        ElMessage.success('结算单创建成功')
        fetchSettlements()
      } catch (e) {}
    })
    .catch(() => {})
}

const handleViewSettlement = (row: TourSettlement) => {
  viewSettlement.value = row
  settlementViewVisible.value = true
}

const handleRefreshSettlement = async (row: TourSettlement) => {
  try {
    await refreshSettlement(row.id)
    ElMessage.success('已从成本项重新汇总')
    fetchSettlements()
  } catch (e) {}
}

const handleSubmitSettlement = (row: TourSettlement) => {
  currentSettlement.value = row
  settlementSubmitForm.abnormal_cost_note = row.abnormal_cost_note || ''
  settlementSubmitForm.remark = row.remark || ''
  settlementSubmitDialogVisible.value = true
}

const doSubmitSettlement = async () => {
  if (!currentSettlement.value) return
  if (currentSettlement.value.task_status === 'abnormal' && !settlementSubmitForm.abnormal_cost_note) {
    ElMessage.warning('请补充异常费用说明')
    return
  }
  settlementSubmitLoading.value = true
  try {
    await submitSettlement(currentSettlement.value.id, {
      abnormal_cost_note: settlementSubmitForm.abnormal_cost_note || undefined,
      remark: settlementSubmitForm.remark || undefined
    })
    ElMessage.success('结算单已提交')
    settlementSubmitDialogVisible.value = false
    fetchSettlements()
  } catch (e) {} finally {
    settlementSubmitLoading.value = false
  }
}

const handleConfirmSettlement = (row: TourSettlement) => {
  ElMessageBox.confirm(
    `确定要确认结算单「${row.settlement_no}」吗？确认后不可修改。`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  )
    .then(async () => {
      try {
        await confirmSettlement(row.id)
        ElMessage.success('结算单已确认')
        fetchSettlements()
      } catch (e) {}
    })
    .catch(() => {})
}

const handleDeleteSettlement = (row: TourSettlement) => {
  ElMessageBox.confirm(
    `确定要删除结算单「${row.settlement_no}」吗？`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  )
    .then(async () => {
      try {
        await deleteSettlement(row.id)
        ElMessage.success('删除成功')
        fetchSettlements()
      } catch (e) {}
    })
    .catch(() => {})
}

const fetchStats = async () => {
  try {
    const params: any = {}
    if (statsFilters.program_id) params.program_id = statsFilters.program_id
    if (statsFilters.city) params.city = statsFilters.city
    if (statsDateRange.value && statsDateRange.value.length === 2) {
      params.start_date = statsDateRange.value[0]
      params.end_date = statsDateRange.value[1]
    }
    const [summary, byProgram] = await Promise.all([
      getCostStatsSummary(params),
      getCostStatsByProgram({
        start_date: params.start_date,
        end_date: params.end_date
      })
    ])
    const s = summary as any
    costStats.total_cost = s.total_cost
    costStats.transport_cost = s.transport_cost
    costStats.labor_cost = s.labor_cost
    costStats.venue_cost = s.venue_cost
    costStats.maintenance_cost = s.maintenance_cost
    costStats.temporary_purchase_cost = s.temporary_purchase_cost
    costStats.abnormal_handling_cost = s.abnormal_handling_cost
    costStats.task_count = s.task_count
    costStats.avg_cost_per_task = s.avg_cost_per_task
    costStats.abnormal_cost_ratio = s.abnormal_cost_ratio
    programCostRankList.value = byProgram as any || []
    await nextTick()
    initCostTypeChart()
    initProgramCostChart()
  } catch (e) {}
}

const handleStatsDateChange = () => {
  fetchStats()
}

const initCostTypeChart = () => {
  if (!costTypeChartRef.value) return
  if (!costTypeChartInstance) {
    costTypeChartInstance = echarts.init(costTypeChartRef.value)
  }
  const seriesData = [
    { name: '运输费', value: costStats.transport_cost },
    { name: '人工费', value: costStats.labor_cost },
    { name: '场地费', value: costStats.venue_cost },
    { name: '维保费', value: costStats.maintenance_cost },
    { name: '临时采购费', value: costStats.temporary_purchase_cost },
    { name: '异常处理费', value: costStats.abnormal_handling_cost }
  ].filter(d => d.value > 0)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      name: '费用类型',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['65%', '50%'],
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: ¥{c}' },
      data: seriesData.length ? seriesData : [{ name: '暂无数据', value: 1, itemStyle: { color: '#e4e7ed' } }]
    }]
  }
  costTypeChartInstance.setOption(option)
}

const initProgramCostChart = () => {
  if (!programCostChartRef.value) return
  if (!programCostChartInstance) {
    programCostChartInstance = echarts.init(programCostChartRef.value)
  }
  const xAxisData = programCostRankList.value.map(item => item.program_name)
  const totalData = programCostRankList.value.map(item => item.total_cost)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const p = programCostRankList.value[idx]
        return `
          <div>剧目：${p.program_name}</div>
          <div>总成本：¥${formatMoney(p.total_cost)}</div>
          <div>任务数：${p.task_count}</div>
          <div>单场平均：¥${formatMoney(p.avg_cost_per_task)}</div>
        `
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: xAxisData.length ? xAxisData : ['暂无数据'],
      axisLabel: { interval: 0, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: '总成本（元）',
      axisLabel: {
        formatter: (v: any) => {
          if (v >= 10000) return (v / 10000) + '万'
          return v
        }
      }
    },
    series: [{
      name: '总成本',
      type: 'bar',
      data: totalData.length ? totalData : [0],
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#f093fb' },
          { offset: 1, color: '#f5576c' }
        ])
      },
      label: {
        show: true,
        position: 'top',
        formatter: (p: any) => '¥' + formatMoney(p.value)
      }
    }]
  }
  programCostChartInstance.setOption(option)
}

const handleResize = () => {
  costTypeChartInstance?.resize()
  programCostChartInstance?.resize()
}

watch(activeTab, (val) => {
  if (val === 'cost') fetchCostItems()
  if (val === 'settlement') fetchSettlements()
  if (val === 'stats') {
    fetchStats()
    nextTick(() => {
      initCostTypeChart()
      initProgramCostChart()
    })
  }
})

onMounted(() => {
  fetchOptions()
  fetchCostItems()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  costTypeChartInstance?.dispose()
  programCostChartInstance?.dispose()
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.stats-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.abnormal-amount {
  color: #f56c6c;
  font-weight: bold;
}

.settlement-tabs {
  background: #fff;
  border-radius: 4px;
  padding: 0 16px 16px;
}

.stats-cards-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
}

.stat-value.primary { color: #409eff; }
.stat-value.success { color: #67c23a; }
.stat-value.warning { color: #e6a23c; }
.stat-value.danger { color: #f56c6c; }

.stats-charts-row {
  margin-bottom: 0;
}

.card-header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 360px;
}
</style>

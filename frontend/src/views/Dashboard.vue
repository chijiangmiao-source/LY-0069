<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon loading-icon">
              <el-icon :size="36"><Upload /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">装车记录总数</div>
              <div class="stat-value">{{ tourFlowStats.total_loading_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon unloading-icon">
              <el-icon :size="36"><Download /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">卸车记录总数</div>
              <div class="stat-value">{{ tourFlowStats.total_unloading_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tour-icon">
              <el-icon :size="36"><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">巡演流转次数</div>
              <div class="stat-value">{{ tourFlowStats.total_tour_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon scrap-icon">
              <el-icon :size="36"><Delete /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">报废道具占比</div>
              <div class="stat-value">{{ maintenanceStats.scrap_proportion }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="12">
        <el-card shadow="hover" class="stat-card warning-card">
          <div class="stat-content">
            <div class="stat-icon maintenance-due-icon">
              <el-icon :size="36"><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">7天内维保到期数量</div>
              <div class="stat-value warning-value">{{ maintenanceStats.maintenance_due_count }}</div>
              <div class="stat-tip" v-if="maintenanceStats.maintenance_due_count > 0">
                请及时安排维保工作
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="stat-card danger-card">
          <div class="stat-content">
            <div class="stat-icon maintenance-overdue-icon">
              <el-icon :size="36"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">超期未处理数量</div>
              <div class="stat-value danger-value">{{ maintenanceStats.maintenance_overdue_count }}</div>
              <div class="stat-tip" v-if="maintenanceStats.maintenance_overdue_count > 0">
                ⚠ 存在超期未维保道具，装车将被限制
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>车辆装载率统计</span>
            </div>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>剧目道具分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>高损耗剧目排行（Top 10）</span>
            </div>
          </template>
          <div ref="lossChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { Upload, Download, Van, Tools, Warning, Delete } from '@element-plus/icons-vue'
import { getDashboardData } from '@/api/dashboard'
import type { DashboardData, TourFlowStats, VehicleLoadRate, ProgramPropDist, MaintenanceStats, HighLossProgram } from '@/types'

const barChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)
const lossChartRef = ref<HTMLElement | null>(null)

let barChartInstance: ECharts | null = null
let pieChartInstance: ECharts | null = null
let lossChartInstance: ECharts | null = null

const tourFlowStats = reactive<TourFlowStats>({
  total_loading_count: 0,
  total_unloading_count: 0,
  total_tour_count: 0
})

const maintenanceStats = reactive<MaintenanceStats>({
  maintenance_due_count: 0,
  maintenance_overdue_count: 0,
  scrap_proportion: 0
})

const vehicleLoadRates = ref<VehicleLoadRate[]>([])
const programPropDist = ref<ProgramPropDist[]>([])
const highLossPrograms = ref<HighLossProgram[]>([])

const initBarChart = () => {
  if (!barChartRef.value) return

  barChartInstance = echarts.init(barChartRef.value)

  const xAxisData = vehicleLoadRates.value.map(item => item.vehicle_code)
  const seriesData = vehicleLoadRates.value.map(item => ({
    value: item.load_rate,
    itemStyle: {
      color: item.load_rate > 100 ? '#F56C6C' : '#409EFF'
    }
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const data = params[0]
        const vehicle = vehicleLoadRates.value[data.dataIndex]
        return `
          <div>车辆编号：${vehicle.vehicle_code}</div>
          <div>车型：${vehicle.model}</div>
          <div>容量：${vehicle.capacity}</div>
          <div>当前装载：${vehicle.current_load}</div>
          <div>装载率：${vehicle.load_rate}%</div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '装载率(%)',
      max: 150,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '装载率',
        type: 'bar',
        data: seriesData,
        barWidth: '50%',
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%'
        }
      }
    ]
  }

  barChartInstance.setOption(option)
}

const initPieChart = () => {
  if (!pieChartRef.value) return

  pieChartInstance = echarts.init(pieChartRef.value)

  const seriesData = programPropDist.value.map(item => ({
    name: item.program_name,
    value: item.prop_count
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: '道具数量',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: seriesData
      }
    ]
  }

  pieChartInstance.setOption(option)
}

const initLossChart = () => {
  if (!lossChartRef.value) return

  lossChartInstance = echarts.init(lossChartRef.value)

  const xAxisData = highLossPrograms.value.map(item => item.program_name)
  const seriesData = highLossPrograms.value.map(item => item.total_damage_quantity)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const data = params[0]
        const program = highLossPrograms.value[data.dataIndex]
        return `
          <div>剧目：${program.program_name}</div>
          <div>总损耗数量：${program.total_damage_quantity}</div>
          <div>道具总数：${program.prop_count}</div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '损耗数量'
    },
    series: [
      {
        name: '损耗数量',
        type: 'bar',
        data: seriesData,
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ee0a24' },
            { offset: 1, color: '#ff976a' }
          ])
        },
        label: {
          show: true,
          position: 'top'
        }
      }
    ]
  }

  lossChartInstance.setOption(option)
}

const handleResize = () => {
  barChartInstance?.resize()
  pieChartInstance?.resize()
  lossChartInstance?.resize()
}

const fetchData = async () => {
  try {
    const data = await getDashboardData() as DashboardData

    tourFlowStats.total_loading_count = data.tour_flow_stats.total_loading_count
    tourFlowStats.total_unloading_count = data.tour_flow_stats.total_unloading_count
    tourFlowStats.total_tour_count = data.tour_flow_stats.total_tour_count

    maintenanceStats.maintenance_due_count = data.maintenance_stats.maintenance_due_count
    maintenanceStats.maintenance_overdue_count = data.maintenance_stats.maintenance_overdue_count
    maintenanceStats.scrap_proportion = data.maintenance_stats.scrap_proportion

    vehicleLoadRates.value = data.vehicle_load_rates
    programPropDist.value = data.program_prop_dist
    highLossPrograms.value = data.high_loss_programs

    await nextTick()
    initBarChart()
    initPieChart()
    initLossChart()
  } catch (error) {
    console.error('获取看板数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  barChartInstance?.dispose()
  pieChartInstance?.dispose()
  lossChartInstance?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.warning-card {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  border: 1px solid #ffd591;
}

.danger-card {
  background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
  border: 1px solid #ffa39e;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 0;
}

.stat-icon {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.loading-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.unloading-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.tour-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.scrap-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.maintenance-due-icon {
  background: linear-gradient(135deg, #faad14 0%, #fadb14 100%);
}

.maintenance-overdue-icon {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.warning-value {
  color: #d48806;
}

.danger-value {
  color: #cf1322;
}

.stat-tip {
  font-size: 12px;
  color: #e6a23c;
  margin-top: 4px;
}

.danger-card .stat-label,
.warning-card .stat-label {
  color: #606266;
}

.charts-row {
  margin-bottom: 0;
}

.chart-card {
  border-radius: 8px;
}

.chart-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 400px;
}

@media (max-width: 1200px) {
  .stats-row .el-col {
    margin-bottom: 20px;
  }

  .charts-row .el-col {
    margin-bottom: 20px;
  }

  .chart-container {
    height: 350px;
  }
}

@media (max-width: 768px) {
  .stat-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stat-value {
    font-size: 24px;
  }

  .chart-container {
    height: 300px;
  }
}
</style>

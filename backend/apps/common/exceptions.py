from ninja.errors import HttpError


class BusinessException(HttpError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code, message)


class NotFoundException(BusinessException):
    def __init__(self, entity_name: str):
        super().__init__(f'{entity_name}不存在', 404)


class ValidationException(BusinessException):
    def __init__(self, message: str):
        super().__init__(message, 400)


class StatusValidationException(BusinessException):
    def __init__(self, message: str):
        super().__init__(message, 400)


class ConflictException(BusinessException):
    def __init__(self, message: str):
        super().__init__(message, 400)


ERR_MSG_VEHICLE_NOT_EXIST = '车辆不存在'
ERR_MSG_PROP_NOT_EXIST = '道具不存在'
ERR_MSG_PROGRAM_NOT_EXIST = '剧目不存在'
ERR_MSG_LOADING_NOT_EXIST = '装车记录不存在'
ERR_MSG_UNLOADING_NOT_EXIST = '卸车记录不存在'
ERR_MSG_DAMAGE_NOT_EXIST = '损耗记录不存在'
ERR_MSG_TASK_NOT_EXIST = '巡演任务不存在'
ERR_MSG_MAINTENANCE_NOT_EXIST = '维保记录不存在'
ERR_MSG_SCRAP_NOT_EXIST = '报废申请不存在'
ERR_MSG_COST_ITEM_NOT_EXIST = '成本项不存在'
ERR_MSG_SETTLEMENT_NOT_EXIST = '结算单不存在'

ERR_MSG_QUANTITY_MUST_BE_POSITIVE = '数量必须大于0'
ERR_MSG_LOADING_QUANTITY_POSITIVE = '装车数量必须大于0'
ERR_MSG_UNLOADING_QUANTITY_POSITIVE = '卸车数量必须大于0'
ERR_MSG_DAMAGE_QUANTITY_POSITIVE = '损耗数量必须大于0'
ERR_MSG_AMOUNT_NON_NEGATIVE = '金额不能为负数'

ERR_MSG_VEHICLE_INACTIVE = '停用车辆不能进行此操作'
ERR_MSG_VEHICLE_INACTIVE_FOR_TOUR = '车辆「{code}」已停用，不可加入巡演任务'
ERR_MSG_VEHICLE_OVERLOAD = '车辆装载量将超过承载容量（当前: {current}, 承载: {capacity}）'
ERR_MSG_VEHICLE_OVERLOAD_ADJUSTED = '车辆装载量将超过承载容量（调整后: {adjusted}, 承载: {capacity}）'
ERR_MSG_VEHICLE_NEGATIVE_LOAD = '卸车数量超过车辆当前装载量（当前装载: {current}）'
ERR_MSG_VEHICLE_NEGATIVE_LOAD_ADJUSTED = '调整后车辆装载量将为负数（调整后: {adjusted}）'
ERR_MSG_VEHICLE_OVERLOAD_ON_DELETE = '删除该卸车记录将导致车辆装载量超过容量（当前: {current}, 容量: {capacity}）'

ERR_MSG_PROP_SCRAPPED_FOR_LOADING = '道具「{code} {name}」{status_msg}，不可装车'
ERR_MSG_PROP_SCRAPPED_FOR_TOUR = '道具「{code} {name}」已报废，不可加入巡演任务'
ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_LOADING = '道具「{code} {name}」维保已超期（下次维保日期: {date}），请先完成维保后再装车'
ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_TOUR = '道具「{code} {name}」维保已超期（下次维保日期: {date}），不可加入巡演任务'

ERR_MSG_SCRAP_STATUS_SCRAPPED = '已报废'
ERR_MSG_SCRAP_STATUS_PENDING = '报废审批中'

ERR_MSG_UNLOADING_DATE_EARLIER = '卸车日期不能早于装车日期'
ERR_MSG_UNLOADING_RECORD_EXISTS = '该装车记录已存在卸车记录'
ERR_MSG_LOADING_HAS_UNLOADING = '该装车记录已有对应的卸车记录，无法删除'

ERR_MSG_DAMAGE_REASON_REQUIRED = '损耗原因必须填写'

ERR_MSG_TASK_DATE_RANGE_INVALID = '任务开始日期不能晚于结束日期'
ERR_MSG_PERFORMANCE_DATE_OUT_OF_RANGE = '演出日期必须在任务开始和结束日期之间'
ERR_MSG_TASK_COMPLETED_OR_CANCELLED = '已完成或已取消的任务不可修改'
ERR_MSG_TASK_IN_PROGRESS_CANNOT_DELETE = '执行中的任务不可删除，请先取消或完成任务'
ERR_MSG_TASK_INVALID_STATUS = '无效的任务状态: {status}'
ERR_MSG_TASK_INVALID_EXEC_STATUS = '无效的执行状态: {status}'
ERR_MSG_TASK_ABNORMAL_REQUIRES_DESC = '标记为异常任务时必须填写异常情况'

ERR_MSG_VEHICLE_TIME_CONFLICT = '车辆「{code}」在时间段 {start}~{end} 已被安排到其他任务: {tasks}'
ERR_MSG_PROP_TIME_CONFLICT = '道具「{code} {name}」在时间段 {start}~{end} 已被安排到其他任务: {tasks}'

ERR_MSG_COST_TYPE_INVALID = '无效的费用类型: {cost_type}'
ERR_MSG_COST_DATE_OUT_OF_RANGE = '费用发生日期必须在任务开始和结束日期之间'
ERR_MSG_TASK_CANCELLED_NO_COST = '已取消的任务不可登记成本'
ERR_MSG_TASK_CANCELLED_COST_CANNOT_EDIT = '已取消任务的成本项不可修改'
ERR_MSG_ABNORMAL_COST_REQUIRES_REMARK = '标记为异常费用时必须填写异常费用说明'
ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_EDIT_COST = '该任务已提交结算，成本项不可修改'
ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_DELETE_COST = '该任务已提交结算，成本项不可删除'

ERR_MSG_TASK_CANCELLED_NO_SETTLEMENT = '已取消的任务不可生成结算记录'
ERR_MSG_SETTLEMENT_ALREADY_EXISTS = '该任务已存在结算单'
ERR_MSG_SETTLEMENT_SUBMITTED_OR_CONFIRMED_CANNOT_REFRESH = '已提交或已确认的结算单不可刷新'
ERR_MSG_TASK_NOT_COMPLETED_CANNOT_SUBMIT_SETTLEMENT = '未完成的任务不能提交最终结算'
ERR_MSG_ABNORMAL_TASK_REQUIRES_COST_NOTE = '异常任务必须补充额外费用说明'
ERR_MSG_SETTLEMENT_ALREADY_CONFIRMED = '已确认的结算单不可重复提交'
ERR_MSG_SETTLEMENT_ONLY_SUBMITTED_CAN_CONFIRM = '只有已提交的结算单可以确认'
ERR_MSG_SETTLEMENT_CONFIRMED_CANNOT_DELETE = '已确认的结算单不可删除'

ERR_MSG_PROP_CODE_ALREADY_EXISTS = '道具编号已存在'
ERR_MSG_VEHICLE_CODE_ALREADY_EXISTS = '车辆编号已存在'
ERR_MSG_PROP_ALREADY_SCRAPPED = '该道具已报废'
ERR_MSG_SCRAP_APPLICATION_PENDING_EXISTS = '该道具已存在待审批的报废申请'
ERR_MSG_SCRAP_ONLY_PENDING_CAN_APPROVE = '只有待审批的申请才能审批'

VALID_COST_TYPES = [
    'transport',
    'labor',
    'venue',
    'maintenance',
    'temporary_purchase',
    'abnormal_handling',
]

COST_TYPE_DISPLAY = {
    'transport': '运输费',
    'labor': '人工费',
    'venue': '场地费',
    'maintenance': '维保费',
    'temporary_purchase': '临时采购费',
    'abnormal_handling': '异常处理费',
}

TOUR_TASK_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled', 'abnormal']
TOUR_EXECUTION_STATUSES = ['not_started', 'preparing', 'transporting', 'performing', 'returning', 'finished']
TOUR_TASK_STATUSES_FOR_CONFLICT = ['pending', 'in_progress']

PROP_SCRAP_STATUSES_BLOCKING = ('scrapped', 'approved', 'pending')
PROP_SCRAP_STATUSES_BLOCKING_FOR_TOUR = ('scrapped', 'approved')

SETTLEMENT_STATUSES_LOCKED = ('submitted', 'confirmed')

PROPS_MAINTENANCE_WARNING_DAYS = 7

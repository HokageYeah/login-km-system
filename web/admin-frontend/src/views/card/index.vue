<template>
  <div class="card-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">卡密管理</h1>
        <p class="page-subtitle">管理系统中的所有卡密，支持生成、查询、状态管理</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          @click="showGenerateDialog"
          class="generate-btn"
        >
          生成卡密
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="应用">
          <el-select
            v-model="filterForm.app_id"
            placeholder="选择应用"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="app in appList"
              :key="app.id"
              :label="app.app_name"
              :value="app.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            class="filter-select"
          >
            <el-option label="未使用" value="unused" />
            <el-option label="已使用" value="used" />
            <el-option label="已禁用" value="disabled" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索卡密或备注"
            clearable
            class="filter-input"
            :prefix-icon="Search"
          />
        </el-form-item>

        <el-form-item label="用户名">
          <el-input
            v-model="filterForm.username"
            placeholder="搜索关联用户名"
            clearable
            class="filter-input"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 卡密列表表格 -->
    <div class="table-section">
      <!-- 批量操作工具栏 -->
      <div v-if="selectedCards.length > 0" class="batch-actions-bar">
        <div class="selected-info">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
          <span>已选择 <strong>{{ selectedCards.length }}</strong> 个卡密</span>
        </div>
        <div class="action-buttons">
          <el-button
            type="primary"
            plain
            :icon="CopyDocument"
            @click="handleBatchCopy"
          >
            批量复制
          </el-button>
          <el-button
            type="danger"
            :icon="Delete"
            @click="handleBatchDelete"
          >
            批量删除
          </el-button>
          <el-button @click="clearSelection">
            取消选择
          </el-button>
        </div>
      </div>

      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="cardList"
        stripe
        class="card-table"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" sortable="custom" />
        
        <el-table-column prop="card_key" label="卡密" min-width="200">
          <template #default="{ row }">
            <div class="card-key-cell">
              <span class="card-key-text">{{ row.card_key }}</span>
              <el-button
                :icon="CopyDocument"
                size="small"
                text
                @click="copyCardKey(row.card_key)"
                class="copy-btn"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="app_name" label="所属应用" width="140">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="plain"
              :style="getAppBadgeStyle(row)"
            >
              {{ row.app_name || '未绑定应用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="160">
          <template #default="{ row }">
            <div class="status-tags">
              <el-tag
                :type="getStatusType(row.status)"
                effect="dark"
                class="status-tag"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
              <el-tag
                v-if="row.is_expired"
                type="danger"
                effect="plain"
                class="status-tag expired-tag"
              >
                已过期
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="expire_time" label="过期时间" width="180">
          <template #default="{ row }">
            <div class="expire-time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDateTime(row.expire_time) }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="max_device_count" label="设备限制" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ row.bind_device_count || 0 }} / {{ row.max_device_count }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="price" width="120" align="right">
          <template #header>
            <div class="price-header">
              <span>卡密价格</span>
              <el-tooltip
                placement="top"
                effect="light"
                :show-after="150"
                content="权限月价按当前有效天数折算，超出 3 台设备后每增加 1 台直接加价 ¥0.50；最终价格为折算后的权限价格 + 设备加价，最低 ¥0.50。"
              >
                <el-icon class="price-help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <template #default="{ row }">
            <span class="price-cell">{{ formatPrice(row.price) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="关联用户" min-width="220">
          <template #default="{ row }">
            <div v-if="getRelatedUsers(row).length" class="related-users-cell">
              <el-tag
                v-for="username in getRelatedUsers(row)"
                :key="username"
                size="small"
                class="related-user-tag"
                effect="plain"
              >
                {{ username }}
              </el-tag>
              <span v-if="(row.bind_user_count || 0) > getRelatedUsers(row).length" class="related-user-more">
                +{{ (row.bind_user_count || 0) - getRelatedUsers(row).length }}
              </span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="permissions" label="权限" min-width="150">
          <template #default="{ row }">
            <div class="permissions-cell">
              <el-tag
                v-for="(perm, index) in getPermissions(row.permissions)"
                :key="index"
                size="small"
                class="permission-tag"
              >
                {{ perm }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="110" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              plain
              :icon="View"
              @click="showCardDetailDrawer(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 卡密详情抽屉 -->
    <el-drawer
      v-model="cardDetailDrawerVisible"
      direction="rtl"
      size="520px"
      class="card-detail-drawer"
      :with-header="false"
      destroy-on-close
    >
      <div v-if="currentCard" class="drawer-page">
        <div class="drawer-hero">
          <div class="drawer-hero-top">
            <div>
              <p class="drawer-eyebrow">卡密详情</p>
              <h2 class="drawer-title">{{ currentCard.card_key }}</h2>
            </div>
            <div class="drawer-hero-actions">
              <el-button
                :icon="CopyDocument"
                circle
                class="drawer-icon-btn"
                @click="copyCardKey(currentCard.card_key)"
              />
              <el-button
                :icon="Close"
                circle
                class="drawer-icon-btn"
                @click="cardDetailDrawerVisible = false"
              />
            </div>
          </div>
          <div class="drawer-status-row">
            <el-tag :type="getStatusType(currentCard.status)" effect="dark">
              {{ getStatusText(currentCard.status) }}
            </el-tag>
            <el-tag v-if="currentCard.is_expired" type="danger" effect="plain">
              已过期
            </el-tag>
            <span class="drawer-app-name">{{ currentCard.app_name || '未关联应用' }}</span>
          </div>
        </div>

        <div class="drawer-stats-grid">
          <div class="drawer-stat-card">
            <span class="drawer-stat-label">关联用户</span>
            <strong>{{ getRelatedUserTotal(currentCard) }}</strong>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-label">设备占用</span>
            <strong>{{ getDeviceUsageText(currentCard) }}</strong>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-label">权限项</span>
            <strong>{{ getPermissions(currentCard.permissions).length }}</strong>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-label">过期状态</span>
            <strong :class="{ 'danger-text': currentCard.is_expired }">
              {{ currentCard.is_expired ? '已过期' : '有效中' }}
            </strong>
          </div>
        </div>

        <section class="drawer-section">
          <div class="section-title">基础信息</div>
          <div class="info-list">
            <div class="info-row">
              <span>卡密</span>
              <strong class="mono-text">{{ currentCard.card_key }}</strong>
            </div>
            <div class="info-row">
              <span>所属应用</span>
              <strong>{{ currentCard.app_name || '-' }}</strong>
            </div>
            <div class="info-row">
              <span>状态</span>
              <strong>{{ getDisplayStatusText(currentCard) }}</strong>
            </div>
            <div class="info-row">
              <span>过期时间</span>
              <strong>{{ formatDateTime(currentCard.expire_time) }}</strong>
            </div>
            <div class="info-row">
              <span>卡密价格</span>
              <strong>{{ formatPrice(currentCard.price) }}</strong>
            </div>
            <div class="info-row">
              <span>创建时间</span>
              <strong>{{ formatDateTime(currentCard.created_at) }}</strong>
            </div>
          </div>
        </section>

        <section class="drawer-section">
          <div class="section-title">关联信息</div>
          <div class="drawer-related-block">
            <div class="drawer-block-head">
              <span>关联用户</span>
              <small>{{ getRelatedUserTotal(currentCard) }} 个</small>
            </div>
            <div v-if="getAllRelatedUsers(currentCard).length" class="drawer-tag-list">
              <el-tag
                v-for="username in getAllRelatedUsers(currentCard)"
                :key="username"
                effect="plain"
                class="related-user-tag"
              >
                {{ username }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无关联用户" :image-size="72" />
          </div>

          <div class="drawer-related-block">
            <div class="drawer-block-head">
              <span>权限</span>
              <small>{{ getPermissions(currentCard.permissions).length }} 项</small>
            </div>
            <div v-if="getPermissions(currentCard.permissions).length" class="drawer-tag-list">
              <el-tag
                v-for="permission in getPermissions(currentCard.permissions)"
                :key="permission"
                class="permission-tag"
              >
                {{ permission }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无权限配置" :image-size="72" />
          </div>
        </section>

        <section class="drawer-section">
          <div class="section-title">备注</div>
          <div class="remark-card">
            {{ currentCard.remark || '暂无备注' }}
          </div>
        </section>

        <section class="drawer-section action-panel">
          <div class="section-title">操作</div>
          <div class="drawer-actions">
            <el-button :icon="View" @click="showDeviceDialog(currentCard)">
              查看设备
            </el-button>
            <el-button :icon="Edit" @click="showPermissionDialog(currentCard)">
              修改权限
            </el-button>
            <el-button
              v-if="userStore.isAdmin"
              type="primary"
              plain
              :icon="Clock"
              @click="showExpireTimeDialog(currentCard)"
            >
              修改过期时间
            </el-button>
            <el-button
              :type="currentCard.status === 'disabled' ? 'success' : 'warning'"
              :icon="currentCard.status === 'disabled' ? CircleCheck : CircleClose"
              @click="handleStatusChange(currentCard)"
            >
              {{ currentCard.status === 'disabled' ? '启用卡密' : '禁用卡密' }}
            </el-button>
            <el-button type="danger" :icon="Delete" @click="handleDelete(currentCard)">
              删除卡密
            </el-button>
          </div>
        </section>
      </div>
    </el-drawer>

    <!-- 修改过期时间弹窗 -->
    <el-dialog
      v-model="expireTimeDialogVisible"
      title="修改过期时间"
      width="460px"
      :close-on-click-modal="false"
      @close="resetExpireTimeDialog"
    >
      <div v-if="currentCard" class="expire-dialog-content">
        <div class="expire-card-preview">
          <span>当前卡密</span>
          <strong>{{ currentCard.card_key }}</strong>
          <div class="expire-preview-time">
            <small>当前过期时间</small>
            <b>{{ formatDateTime(currentCard.expire_time) }}</b>
          </div>
        </div>
        <el-form label-width="96px">
          <el-form-item label="过期时间">
            <span class="form-readonly-text">{{ formatDateTime(currentCard.expire_time) }}</span>
          </el-form-item>
          <el-form-item label="新的时间" required>
            <el-date-picker
              v-model="expireTimeForm.expire_time"
              type="datetime"
              placeholder="请选择新的过期时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              class="w-full"
            />
            <div class="expire-shortcut-group">
              <el-button
                v-for="shortcut in expireShortcutOptions"
                :key="shortcut.key"
                size="small"
                plain
                @click="handleExpireTimeShortcutSelect(shortcut.key)"
              >
                {{ shortcut.label }}
              </el-button>
            </div>
            <div class="form-tip">
              可选择未来时间延长有效期，也可选择过去时间让卡密立即进入已过期状态；保存后会按当前设备数和权限重新计算卡密价格。
            </div>
            <div class="pricing-panel">
              <div class="pricing-summary">
                <span>预计价格</span>
                <strong>{{ formatPrice(expirePricingBreakdown.finalPrice) }}</strong>
              </div>
              <p>
                当前：权限月价 {{ formatPrice(expirePricingBreakdown.monthlyPermissionPrice) }}
                ，有效 {{ expirePricingBreakdown.durationDays }} 天；
                权限折算后 {{ formatPrice(expirePricingBreakdown.proratedPermissionPrice) }}
                + 设备加价 {{ formatPrice(expirePricingBreakdown.extraDevicePrice) }}
                = 最终价格 {{ formatPrice(expirePricingBreakdown.finalPrice) }}。
              </p>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="expireTimeDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="expireTimeSubmitting"
          @click="handleExpireTimeSubmit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 生成卡密弹窗 -->
    <GenerateDialog
      v-model="generateDialogVisible"
      :app-list="appList"
      @success="handleGenerateSuccess"
    />

    <!-- 修改权限弹窗 -->
    <PermissionDialog
      v-model="permissionDialogVisible"
      :card="currentCard"
      :permissions="getPermissions(currentCard?.permissions)"
      @success="handlePermissionSuccess"
    />

    <!-- 查看设备弹窗 -->
    <DeviceDialog
      v-model="deviceDialogVisible"
      :card="currentCard"
      @success="handleDeviceLimitSuccess"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 卡密管理页面
 * @description 管理员管理系统中的所有卡密
 */
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  CopyDocument,
  Clock,
  View,
  Edit,
  CircleCheck,
  CircleClose,
  Delete,
  InfoFilled,
  QuestionFilled,
  Close
} from '@element-plus/icons-vue'
import type { ElTable } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getCardList, updateCardStatus, updateCardExpireTime } from '@/api/admin'
import { batchDeleteCards } from '@/api/card'
import { getAppList } from '@/api/app'
import { getFeaturePermissionList } from '@/api/feature-permission'
import { useUserStore } from '@/stores/user'
import type { Card, App, FeaturePermission } from '@/types'
import { getAppTagStyle } from '@/utils/app-tag'
import { calculateCardPricingBreakdown } from '@/utils/card-pricing'
import {
  EXPIRE_SHORTCUT_OPTIONS,
  formatDateTimeValue,
  getExpireShortcutValue,
  type ExpireShortcutKey
} from '@/utils/expire-shortcuts'
import GenerateDialog from './components/GenerateDialog.vue'
import PermissionDialog from './components/PermissionDialog.vue'
import DeviceDialog from './components/DeviceDialog.vue'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const cardList = ref<Card[]>([])                        // 卡密列表
const appList = ref<App[]>([])                          // 应用列表
const currentCard = ref<Card | null>(null)              // 当前操作的卡密
const selectedCards = ref<Card[]>([])                   // 选中的卡密
const tableRef = ref<InstanceType<typeof ElTable>>()    // 表格引用
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/**
 * 弹窗显示状态
 */
const generateDialogVisible = ref(false)                // 生成卡密弹窗
const permissionDialogVisible = ref(false)              // 修改权限弹窗
const deviceDialogVisible = ref(false)                  // 查看设备弹窗
const cardDetailDrawerVisible = ref(false)              // 卡密详情抽屉
const expireTimeDialogVisible = ref(false)              // 修改过期时间弹窗
const expireTimeSubmitting = ref(false)                 // 修改过期时间提交状态
const expireShortcutOptions = EXPIRE_SHORTCUT_OPTIONS   // 过期时间快捷选项
const expirePricingPermissions = ref<FeaturePermission[]>([]) // 修改过期时间时用于价格拆解的权限元数据

/**
 * 筛选表单
 */
const filterForm = reactive({
  app_id: undefined as number | undefined,
  status: '',
  keyword: '',
  username: ''
})

const expireTimeForm = reactive({
  expire_time: ''
})

const expirePricingBreakdown = computed(() => calculateCardPricingBreakdown({
  permissions: currentCard.value?.permissions || [],
  availablePermissions: expirePricingPermissions.value,
  expireTime: expireTimeForm.expire_time,
  maxDeviceCount: currentCard.value?.max_device_count || 1
}))

const loadExpirePricingPermissions = async (card: Card) => {
  if (!card.app_id) {
    expirePricingPermissions.value = []
    return
  }

  try {
    const response = await getFeaturePermissionList({
      page: 1,
      size: 100,
      app_id: card.app_id
    })
    expirePricingPermissions.value = response.permissions || []
  } catch (error) {
    console.error('[卡密管理] 加载修改过期时间价格计算所需权限失败', error)
    expirePricingPermissions.value = []
  }
}

const syncFilterFromRoute = () => {
  const routeAppId = route.query.app_id
  if (typeof routeAppId === 'string' && routeAppId) {
    const parsedAppId = Number(routeAppId)
    filterForm.app_id = Number.isNaN(parsedAppId) ? undefined : parsedAppId
  } else {
    filterForm.app_id = undefined
  }

  const cardKey = route.query.card_key
  if (typeof cardKey === 'string' && cardKey) {
    filterForm.keyword = cardKey
    filterForm.username = ''
    return
  }

  filterForm.keyword = ''
}

/**
 * 分页参数
 */
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

/**
 * 获取状态标签类型
 * @param status 卡密状态
 * @returns Element Plus Tag 类型
 */
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    unused: 'success',
    used: 'warning',
    disabled: 'danger'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取状态文本
 * @param status 卡密状态
 * @returns 状态中文文本
 */
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    unused: '未使用',
    used: '已使用',
    disabled: '已禁用'
  }
  return textMap[status] || status
}

/**
 * 获取所属应用标签样式
 */
const getAppBadgeStyle = (card: Card) => getAppTagStyle(card.app_key, card.app_name)

/**
 * 获取卡密展示状态文本
 * @description 状态展示保留原始业务状态，同时在已过期时附加提示，
 * 避免把“过期”错误地混入数据库状态枚举。
 */
const getDisplayStatusText = (card: Card) => {
  const baseStatusText = getStatusText(card.status)
  return card.is_expired ? `${baseStatusText}（已过期）` : baseStatusText
}

/**
 * 格式化日期时间
 * @param dateStr ISO 8601 格式的日期字符串
 * @returns 格式化后的日期时间字符串
 */
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 格式化卡密售卖价格
 */
const formatPrice = (price: number | string | null | undefined) => {
  const parsedPrice = Number(price ?? 0)
  if (Number.isNaN(parsedPrice)) {
    return '¥0.00'
  }
  return `¥${parsedPrice.toFixed(2)}`
}

/**
 * 获取权限列表
 * @param permissions 权限数据（可能是数组或对象）
 * @returns 权限字符串数组
 */
const getPermissions = (permissions: any): string[] => {
  if (Array.isArray(permissions)) {
    return permissions
  }
  if (typeof permissions === 'object' && permissions !== null) {
    return Object.keys(permissions)
  }
  return []
}

const getRelatedUsers = (card: Card) => {
  if (Array.isArray(card.related_usernames) && card.related_usernames.length > 0) {
    return card.related_usernames.slice(0, 3)
  }

  return []
}

const getAllRelatedUsers = (card: Card) => {
  return Array.isArray(card.related_usernames) ? card.related_usernames : []
}

const getRelatedUserTotal = (card: Card) => {
  return card.bind_user_count || getAllRelatedUsers(card).length
}

const getBoundDeviceCount = (card: Card) => {
  return card.bind_device_count ?? card.bind_devices ?? 0
}

const getDeviceUsageText = (card: Card) => {
  return `${getBoundDeviceCount(card)} / ${card.max_device_count}`
}

const isExpiredByTime = (expireTime: string) => {
  if (!expireTime) return false
  return new Date(expireTime).getTime() < Date.now()
}

/**
 * 处理修改过期时间弹窗中的快捷时间选择
 * @description 与“批量生成卡密”复用同一套快捷规则，确保各入口行为一致，
 * 后续若扩展快捷项，也只需要修改公共工具文件即可。
 * @param shortcutKey 快捷时间 key
 */
const handleExpireTimeShortcutSelect = (shortcutKey: ExpireShortcutKey) => {
  const selectedShortcut = expireShortcutOptions.find(item => item.key === shortcutKey)
  const expireTimeValue = getExpireShortcutValue(shortcutKey)

  expireTimeForm.expire_time = expireTimeValue

  console.info('[卡密管理] 修改过期时间弹窗选择快捷时间', {
    cardId: currentCard.value?.id,
    cardKey: currentCard.value?.card_key,
    shortcutKey,
    shortcutLabel: selectedShortcut?.label,
    expireTime: expireTimeValue
  })
}

/**
 * 复制文本到剪贴板
 * @description 统一收敛复制行为，避免单个复制、批量复制各自维护提示逻辑。
 * @param text 待复制文本
 * @param successMessage 复制成功提示语
 */
const copyTextToClipboard = async (text: string, successMessage: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(successMessage)
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

/**
 * 复制单个卡密
 * @param cardKey 卡密字符串
 */
const copyCardKey = async (cardKey: string) => {
  await copyTextToClipboard(cardKey, '卡密已复制到剪贴板')
}

/**
 * 处理批量复制
 * @description 选中的卡密按换行拼接，便于直接粘贴到文本框、表格或消息中。
 */
const handleBatchCopy = async () => {
  const cardKeys = selectedCards.value
    .map(card => card.card_key)
    .filter((cardKey): cardKey is string => Boolean(cardKey))

  if (cardKeys.length === 0) {
    ElMessage.warning('请先选择要复制的卡密')
    return
  }

  await copyTextToClipboard(cardKeys.join('\n'), `已复制 ${cardKeys.length} 个卡密`)
}

/**
 * 处理选择变化
 * @param selection 选中的卡密列表
 */
const handleSelectionChange = (selection: Card[]) => {
  selectedCards.value = selection
}

/**
 * 清除选择
 */
const clearSelection = () => {
  tableRef.value?.clearSelection()
}

/**
 * 处理单个删除
 * @param card 卡密信息
 */
const handleDelete = async (card: Card) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除卡密 ${card.card_key} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>卡密：<strong>${card.card_key}</strong></p>
            <p>应用：<strong>${card.app_name}</strong></p>
            <p>状态：<strong>${getDisplayStatusText(card)}</strong></p>
            <p style="color: #f56c6c; margin-top: 10px;">
              <strong>警告：</strong>删除操作不可恢复！
            </p>
            <p style="color: #f56c6c;">
              该卡密的所有绑定数据（用户绑定、设备绑定等）将被永久删除。
            </p>
          </div>
        `
      }
    )
    
    const result = await batchDeleteCards([card.id])
    
    if (result.deleted_count > 0) {
      ElMessage.success('删除成功')
      if (currentCard.value?.id === card.id) {
        cardDetailDrawerVisible.value = false
        currentCard.value = null
      }
      loadCardList()
    } else {
      ElMessage.warning('删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除卡密失败:', error)
    }
  }
}

/**
 * 处理批量删除
 */
const handleBatchDelete = async () => {
  if (selectedCards.value.length === 0) {
    ElMessage.warning('请先选择要删除的卡密')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedCards.value.length} 个卡密吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div>
            <p>即将删除 <strong>${selectedCards.value.length}</strong> 个卡密</p>
            <p style="color: #f56c6c; margin-top: 10px;">
              <strong>警告：</strong>批量删除操作不可恢复！
            </p>
            <p style="color: #f56c6c;">
              所有选中卡密的绑定数据（用户绑定、设备绑定等）将被永久删除。
            </p>
            <p style="color: #f56c6c;">
              已绑定的用户将无法继续使用这些卡密。
            </p>
          </div>
        `
      }
    )
    
    const cardIds = selectedCards.value.map(card => card.id)
    const result = await batchDeleteCards(cardIds)
    
    ElMessage.success(result.message)
    
    // 清除选择并刷新列表
    clearSelection()
    loadCardList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
      console.error('批量删除卡密失败:', error)
    }
  }
}

/**
 * 显示生成卡密弹窗
 */
const showGenerateDialog = () => {
  generateDialogVisible.value = true
}

/**
 * 显示修改权限弹窗
 * @param card 卡密信息
 */
const showPermissionDialog = (card: Card) => {
  currentCard.value = card
  permissionDialogVisible.value = true
}

/**
 * 显示查看设备弹窗
 * @param card 卡密信息
 */
const showDeviceDialog = (card: Card) => {
  currentCard.value = card
  deviceDialogVisible.value = true
}

/**
 * 显示卡密详情抽屉
 * @param card 卡密信息
 */
const showCardDetailDrawer = (card: Card) => {
  currentCard.value = card
  cardDetailDrawerVisible.value = true
}

/**
 * 显示修改过期时间弹窗
 * @param card 卡密信息
 */
const showExpireTimeDialog = (card: Card) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('只有管理员可以修改卡密过期时间')
    return
  }

  currentCard.value = card
  expireTimeForm.expire_time = formatDateTimeValue(new Date())
  loadExpirePricingPermissions(card)
  console.info('[卡密管理] 打开修改过期时间弹窗', {
    cardId: card.id,
    cardKey: card.card_key,
    currentExpireTime: card.expire_time,
    defaultExpireTime: expireTimeForm.expire_time
  })
  expireTimeDialogVisible.value = true
}

/**
 * 重置修改过期时间弹窗
 */
const resetExpireTimeDialog = () => {
  console.info('[卡密管理] 重置修改过期时间弹窗状态', {
    cardId: currentCard.value?.id,
    cardKey: currentCard.value?.card_key
  })
  expireTimeForm.expire_time = ''
  expirePricingPermissions.value = []
  expireTimeSubmitting.value = false
}

/**
 * 提交修改过期时间
 */
const handleExpireTimeSubmit = async () => {
  if (!currentCard.value) {
    ElMessage.warning('请选择要修改的卡密')
    return
  }

  if (!expireTimeForm.expire_time) {
    ElMessage.warning('请选择新的过期时间')
    return
  }

  expireTimeSubmitting.value = true
  try {
    console.info('[卡密管理] 开始提交新的过期时间', {
      cardId: currentCard.value.id,
      cardKey: currentCard.value.card_key,
      oldExpireTime: currentCard.value.expire_time,
      newExpireTime: expireTimeForm.expire_time
    })

    const result = await updateCardExpireTime(currentCard.value.id, expireTimeForm.expire_time)

    const updatedCard = {
      ...currentCard.value,
      expire_time: expireTimeForm.expire_time,
      is_expired: isExpiredByTime(expireTimeForm.expire_time),
      price: result.price ?? currentCard.value.price
    }

    currentCard.value = updatedCard
    const listIndex = cardList.value.findIndex(card => card.id === updatedCard.id)
    if (listIndex !== -1) {
      cardList.value[listIndex] = updatedCard
    }

    console.info('[卡密管理] 过期时间更新成功', {
      cardId: updatedCard.id,
      cardKey: updatedCard.card_key,
      newExpireTime: updatedCard.expire_time,
      isExpired: updatedCard.is_expired,
      newPrice: updatedCard.price
    })
    ElMessage.success('卡密过期时间更新成功，卡密价格已重新计算')
    expireTimeDialogVisible.value = false
    loadCardList()
  } catch (error) {
    ElMessage.error('卡密过期时间更新失败')
    console.error('卡密过期时间更新失败:', error)
  } finally {
    expireTimeSubmitting.value = false
  }
}

/**
 * 处理状态变更
 * @param card 卡密信息
 */
const handleStatusChange = async (card: Card) => {
  const newStatus = card.status === 'disabled' ? 'unused' : 'disabled'
  const action = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}卡密 ${card.card_key} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateCardStatus(card.id, newStatus)
    ElMessage.success(`${action}成功`)
    card.status = newStatus
    if (currentCard.value?.id === card.id) {
      currentCard.value = { ...card }
    }
    loadCardList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  loadCardList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  filterForm.app_id = undefined
  filterForm.status = ''
  filterForm.keyword = ''
  filterForm.username = ''
  pagination.page = 1
  if (route.query.card_key) {
    router.replace({
      name: 'Cards',
      query: {}
    })
    return
  }
  loadCardList()
}

/**
 * 处理排序变化
 */
const handleSortChange = ({ prop, order }: any) => {
  // 可以根据需要实现排序逻辑
  console.log('排序变化:', prop, order)
}

/**
 * 处理页码变化
 */
const handlePageChange = (page: number) => {
  pagination.page = page
  loadCardList()
}

/**
 * 处理每页数量变化
 */
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadCardList()
}

/**
 * 生成卡密成功回调
 */
const handleGenerateSuccess = () => {
  loadCardList()
}

/**
 * 修改权限成功回调
 */
const handlePermissionSuccess = (updatedCard?: Card) => {
  if (updatedCard) {
    currentCard.value = updatedCard
    const listIndex = cardList.value.findIndex(card => card.id === updatedCard.id)
    if (listIndex !== -1) {
      cardList.value[listIndex] = updatedCard
    }
  }
  loadCardList()
}

/**
 * 设备限制修改成功回调
 * @description 同步当前编辑卡密与列表数据，随后再刷新列表，确保页面展示及时一致。
 */
const handleDeviceLimitSuccess = (updatedCard: Card) => {
  console.info('[卡密管理] 收到设备限制更新成功回调', {
    cardId: updatedCard.id,
    cardKey: updatedCard.card_key,
    maxDeviceCount: updatedCard.max_device_count
  })

  currentCard.value = updatedCard

  const listIndex = cardList.value.findIndex(card => card.id === updatedCard.id)
  if (listIndex !== -1) {
    cardList.value[listIndex] = updatedCard
  }

  loadCardList()
}

/**
 * 加载卡密列表
 */
const loadCardList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (filterForm.app_id) {
      params.app_id = filterForm.app_id
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }
    if (filterForm.username.trim()) {
      params.username = filterForm.username.trim()
    }
    
    const data = await getCardList(params)
    cardList.value = data.cards
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('加载卡密列表失败')
    console.error('加载卡密列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 加载应用列表
 */
const loadAppList = async () => {
  try {
    const data = await getAppList()
    appList.value = data.apps
  } catch (error) {
    console.error('加载应用列表失败:', error)
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  syncFilterFromRoute()
  loadCardList()
  loadAppList()
})

watch(
  () => [route.query.card_key, route.query.app_id],
  () => {
    syncFilterFromRoute()
    pagination.page = 1
    loadCardList()
  }
)
</script>

<style scoped>
@reference "../../styles/index.css";
.card-management-container {
  @apply w-full h-full p-8;
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  min-height: calc(100vh - 64px);
}

/* 页面头部 */
.page-header {
  @apply flex justify-between items-center mb-8;
}

.page-title {
  @apply text-3xl font-bold text-gray-900 mb-2;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  @apply text-base text-gray-600;
}

.header-actions {
}

.generate-btn {
  @apply px-6 py-2.5;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white font-medium rounded-xl;
  @apply shadow-lg shadow-blue-500/20;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  @apply shadow-xl shadow-blue-500/30;
  transform: translateY(-2px);
}

/* 筛选区域 */
.filter-section {
  @apply bg-white rounded-2xl p-6 mb-6;
  @apply shadow-sm border border-gray-100;
}

.filter-form {
  @apply mb-0;
}

.filter-select {
  @apply w-48;
}

.filter-input {
  @apply w-64;
}

/* 表格区域 */
.table-section {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
}

.card-table {
  @apply w-full;
}

/* 卡密单元格 */
.card-key-cell {
  @apply flex items-center gap-2;
}

.card-key-text {
  @apply font-mono text-sm font-medium text-gray-900;
}

.copy-btn {
  @apply text-blue-600;
}

.related-users-cell {
  @apply flex flex-wrap items-center gap-2;
}

.related-user-tag {
  @apply max-w-full;
}

.related-user-more {
  @apply text-xs text-gray-500;
}

/* 状态标签 */
.status-tags {
  @apply flex flex-wrap gap-2;
}

.status-tag {
  @apply font-medium;
}

.expired-tag {
  @apply border-orange-300 text-orange-600 bg-orange-50;
}

/* 过期时间单元格 */
.expire-time-cell {
  @apply flex items-center gap-2 text-sm text-gray-600;
}

/* 权限单元格 */
.permissions-cell {
  @apply flex flex-wrap gap-1;
}

.permission-tag {
  @apply bg-blue-50 text-blue-700 border-blue-200;
}

.price-header {
  @apply inline-flex items-center justify-end gap-1 text-gray-700;
}

.price-help-icon {
  @apply text-sm text-gray-400 cursor-help transition-colors duration-200;
}

.price-help-icon:hover {
  @apply text-blue-500;
}

.price-cell {
  @apply font-semibold text-gray-900 tabular-nums;
}

/* 批量操作工具栏 */
.batch-actions-bar {
  @apply flex justify-between items-center mb-4 p-4;
  @apply bg-blue-50 border border-blue-200 rounded-xl;
}

.selected-info {
  @apply flex items-center gap-2 text-blue-700;
}

.info-icon {
  @apply text-lg;
}

.selected-info strong {
  @apply text-blue-900 font-bold;
}

/* 操作按钮 */
.action-buttons {
  @apply flex gap-2;
}

/* 详情抽屉 */
:deep(.card-detail-drawer .el-drawer__body) {
  @apply p-0 bg-gray-50;
}

.drawer-page {
  @apply min-h-full p-6 space-y-5;
}

.drawer-hero {
  @apply rounded-3xl p-6 text-white overflow-hidden relative;
  background:
    radial-gradient(circle at 12% 20%, rgba(255, 255, 255, 0.32), transparent 28%),
    linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
  box-shadow: 0 24px 60px rgba(59, 130, 246, 0.24);
}

.drawer-hero::after {
  content: '';
  @apply absolute rounded-full;
  width: 180px;
  height: 180px;
  right: -72px;
  bottom: -96px;
  background: rgba(255, 255, 255, 0.16);
}

.drawer-hero-top {
  @apply flex items-start justify-between gap-4 relative z-10;
}

.drawer-eyebrow {
  @apply text-xs font-semibold tracking-widest text-blue-100 mb-2;
}

.drawer-title {
  @apply text-xl font-bold font-mono break-all leading-snug;
}

.drawer-hero-actions {
  @apply flex items-center gap-2 shrink-0;
}

.drawer-icon-btn {
  @apply shrink-0 border-white/30 text-white bg-white/10;
}

.drawer-icon-btn:hover {
  @apply bg-white/20 text-white border-white/50;
}

.drawer-status-row {
  @apply flex flex-wrap items-center gap-2 mt-5 relative z-10;
}

.drawer-app-name {
  @apply text-sm text-blue-50;
}

.drawer-stats-grid {
  @apply grid grid-cols-2 gap-3;
}

.drawer-stat-card {
  @apply bg-white rounded-2xl border border-gray-100 p-4 shadow-sm;
}

.drawer-stat-label {
  @apply block text-xs text-gray-500 mb-2;
}

.drawer-stat-card strong {
  @apply text-lg font-bold text-gray-900;
}

.danger-text {
  @apply text-red-600;
}

.drawer-section {
  @apply bg-white rounded-2xl border border-gray-100 p-5 shadow-sm;
}

.section-title {
  @apply text-sm font-bold text-gray-900 mb-4;
}

.info-list {
  @apply space-y-3;
}

.info-row {
  @apply flex items-start justify-between gap-4 text-sm;
}

.info-row span {
  @apply text-gray-500 shrink-0;
}

.info-row strong {
  @apply text-gray-900 text-right font-medium break-all;
}

.mono-text {
  @apply font-mono;
}

.drawer-related-block {
  @apply rounded-2xl bg-gray-50 border border-gray-100 p-4 mb-4 last:mb-0;
}

.drawer-block-head {
  @apply flex items-center justify-between mb-3 text-sm font-medium text-gray-900;
}

.drawer-block-head small {
  @apply text-xs text-gray-500 font-normal;
}

.drawer-tag-list {
  @apply flex flex-wrap gap-2;
}

.remark-card {
  @apply min-h-20 rounded-2xl bg-gray-50 border border-gray-100 p-4 text-sm text-gray-700 whitespace-pre-wrap;
}

.action-panel {
  @apply mb-4;
}

.drawer-actions {
  @apply grid grid-cols-2 gap-3;
}

.drawer-actions .el-button {
  @apply m-0 w-full justify-center;
}

/* 修改过期时间弹窗 */
.expire-dialog-content {
  @apply space-y-5;
}

.expire-card-preview {
  @apply rounded-2xl border border-blue-100 bg-blue-50 p-4;
}

.expire-card-preview span {
  @apply block text-xs text-blue-600 mb-2;
}

.expire-card-preview strong {
  @apply block font-mono text-sm text-gray-900 break-all;
}

.expire-preview-time {
  @apply mt-4 rounded-xl bg-white/80 border border-blue-100 p-3;
}

.expire-preview-time small {
  @apply block text-xs text-gray-500 mb-1;
}

.expire-preview-time b {
  @apply text-sm text-gray-900 font-semibold;
}

.form-readonly-text {
  @apply text-sm text-gray-700;
}

.form-tip {
  @apply mt-2 text-xs text-gray-500 leading-relaxed;
}

.pricing-panel {
  @apply mt-3 rounded-xl border border-blue-100 bg-blue-50 p-4;
  @apply text-xs leading-5 text-blue-900;
}

.pricing-summary {
  @apply flex items-center justify-between mb-2;
}

.pricing-summary span {
  @apply text-gray-500;
}

.pricing-summary strong {
  @apply text-lg font-bold text-blue-700;
  font-variant-numeric: tabular-nums;
}

.expire-shortcut-group {
  @apply flex flex-wrap gap-2 mt-3;
}

/* 分页 */
.pagination-section {
  @apply flex justify-end mt-6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    @apply flex-col gap-4;
  }

  .header-actions {
    @apply w-full;
  }

  .generate-btn {
    @apply w-full;
  }

  .filter-form {
    @apply flex-col;
  }

  .filter-select,
  .filter-input {
    @apply w-full;
  }

  .batch-actions-bar {
    @apply flex-col gap-3;
  }

  .action-buttons {
    @apply flex-col;
  }

  :deep(.card-detail-drawer) {
    width: 100% !important;
  }

  .drawer-actions {
    @apply grid-cols-1;
  }
}
</style>

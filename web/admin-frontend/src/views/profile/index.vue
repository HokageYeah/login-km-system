<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="profile-header">
      <div>
        <h1 class="profile-title">个人中心</h1>
        <p class="profile-subtitle">管理您的账户和卡密信息</p>
      </div>
      <div class="header-actions">
        <el-button
          v-if="!userStore.isAdmin"
          type="primary"
          :icon="Ticket"
          @click="bindDialogVisible = true"
          class="bind-btn"
        >
          绑定卡密
        </el-button>
      </div>
    </div>

    <div class="profile-content">
      <!-- 用户信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <el-icon class="title-icon"><User /></el-icon>
            基本信息
          </h2>
        </div>
        <div class="user-info-grid">
          <div class="info-item">
            <div class="avatar-section">
              <el-avatar :size="120" class="user-avatar">
                <el-icon :size="60"><User /></el-icon>
              </el-avatar>
            </div>
          </div>
          <div class="info-item">
            <span class="info-label">用户名</span>
            <span class="info-value">{{ userStore.username }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">角色</span>
            <el-tag :type="userStore.role === 'admin' ? 'danger' : 'primary'" size="small" class="info-tag">
              {{ userStore.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">账户状态</span>
            <el-tag :type="userStore.userStatus === 'normal' ? 'success' : 'danger'" size="small" class="info-tag">
              {{ userStore.userStatus === 'normal' ? '正常' : '封禁' }}
            </el-tag>
          </div>
          <div v-if="userInfo" class="info-item">
            <span class="info-label">应用ID</span>
            <span class="info-value">{{ userInfo.app_id || '未设置' }}</span>
          </div>
          <div v-if="userInfo" class="info-item">
            <span class="info-label">设备ID</span>
            <span class="info-value device-id">{{ userInfo.device_id || '未设置' }}</span>
</div>
        </div>
      </div>

      <!-- 管理员快捷入口 -->
      <div v-if="userStore.isAdmin" class="quick-actions-card">
        <div class="card-header">
          <h2 class="card-title">
            <el-icon class="title-icon"><Operation /></el-icon>
            快捷操作
          </h2>
        </div>
        <div class="quick-actions-grid">
          <router-link to="/users" class="action-card">
            <el-icon class="action-icon" :size="32"><User /></el-icon>
            <span class="action-label">用户管理</span>
            <span class="action-desc">管理系统用户</span>
          </router-link>
          <router-link to="/cards" class="action-card">
            <el-icon class="action-icon" :size="32"><Ticket /></el-icon>
            <span class="action-label">卡密管理</span>
            <span class="action-desc">生成和管理卡密</span>
          </router-link>
          <router-link to="/devices" class="action-card">
            <el-icon class="action-icon" :size="32"><Monitor /></el-icon>
            <span class="action-label">设备管理</span>
            <span class="action-desc">查看绑定设备</span>
          </router-link>
          <router-link to="/apps" class="action-card">
            <el-icon class="action-icon" :size="32"><Grid /></el-icon>
            <span class="action-label">应用管理</span>
            <span class="action-desc">管理应用列表</span>
          </router-link>
        </div>
      </div>

      <!-- 我的卡密列表 -->
      <div class="cards-card">
        <div class="card-header">
          <h2 class="card-title">
            <el-icon class="title-icon"><Ticket /></el-icon>
            我的卡密
          </h2>
        </div>
        <div v-loading="cardsLoading" class="cards-list">
          <!-- 无卡密提示 -->
          <div v-if="!cardsLoading && (!cards || cards.length === 0)" class="empty-state">
            <el-empty description="暂无绑定的卡密">
              <el-button
                v-if="!userStore.isAdmin"
                type="primary"
                @click="bindDialogVisible = true"
              >
                立即绑定
              </el-button>
            </el-empty>
          </div>

          <!-- 卡密列表 -->
          <div v-else class="cards-grid">
            <div
              v-for="card in cards"
              :key="card.card_id"
              class="card-item"
            >
              <!-- 卡密头部 -->
              <div class="card-header-row">
                <div class="card-key">{{ formatCardKey(card.card_key) }}</div>
                <el-tag
                  :type="getCardStatusType(card.status)"
                  size="default"
                >
                  {{ getCardStatusText(card.status) }}
                </el-tag>
              </div>

              <!-- 卡密内容 -->
              <div class="card-body">
                <div class="card-row">
                  <span class="card-label">过期时间</span>
                  <span class="card-value">{{ formatDate(card.expire_time) }}</span>
                </div>
                <div class="card-row">
                  <span class="card-label">设备绑定</span>
                  <span class="card-value">
                    {{ card.bind_devices || 0 }} / {{ card.max_device_count }}
                  </span>
                </div>
                <div class="card-row permissions">
                  <span class="card-label">权限列表</span>
                  <div class="permission-tags">
                    <el-tag
                      v-for="perm in card.permissions"
                      :key="perm"
                      size="small"
                      type="info"
                      class="permission-tag"
                    >
                      {{ perm }}
                    </el-tag>
                    <span v-if="!card.permissions || card.permissions.length === 0" class="no-permissions">
                      暂无权限
                    </span>
                  </div>
                </div>
                <div v-if="card.remark" class="card-row">
                  <span class="card-label">备注</span>
                  <span class="card-value">{{ card.remark }}</span>
                </div>
              </div>

              <!-- 卡密操作 -->
              <div class="card-footer">
                <el-button
                  type="primary"
                  size="default"
                  @click="viewDevices(card)"
                  class="w-full"
                >
                  查看设备
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定卡密弹窗 -->
    <el-dialog
      v-model="bindDialogVisible"
      title="绑定卡密"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="bindForm" :rules="bindRules" ref="bindFormRef" label-width="90px">
        <el-form-item label="卡密" prop="card_key">
          <el-input
            v-model="bindForm.card_key"
            placeholder="请输入卡密（格式：XXXX-XXXX-XXXX-XXXX）"
            clearable
          />
        </el-form-item>
        <el-form-item label="设备名称" prop="device_name">
          <el-input
            v-model="bindForm.device_name"
            placeholder="请输入设备名称（可选）"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="bindLoading"
          @click="handleBindCard"
        >
          确定绑定
        </el-button>
      </template>
    </el-dialog>

    <!-- 设备列表弹窗 -->
    <el-dialog
      v-model="deviceDialogVisible"
      title="设备列表"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="deviceDialogLoading" class="device-list">
        <el-table :data="devices" stripe>
          <el-table-column prop="device_id" label="设备ID" min-width="200" />
          <el-table-column prop="device_name" label="设备名称" min-width="150" />
          <el-table-column prop="bind_time" label="绑定时间" min-width="180">
            <template #default="{ row }">
              {{ formatDate(row.bind_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="last_active_at" label="最后活跃" min-width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_active_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ row.status === 'active' ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                link
                @click="handleUnbindDevice(row)"
              >
                解绑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 个人中心页面
 * @description 显示用户信息、管理卡密绑定、查看设备等
 */
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { User, Ticket, Monitor, Grid, Operation } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getMyCards, bindCard, unbindDevice, getCardDetail } from '@/api/card'
import type { Card, Device } from '@/types'

/**
 * Store 实例
 */
const userStore = useUserStore()

/**
 * 状态定义
 */
const userInfo = ref<any>(null)                  // 用户详细信息
const cards = ref<Card[]>([])                     // 卡密列表
const cardsLoading = ref(false)                   // 卡密加载状态
const bindLoading = ref(false)                    // 绑定加载状态
const bindDialogVisible = ref(false)              // 绑定弹窗显示状态
const deviceDialogVisible = ref(false)            // 设备列表弹窗显示状态
const deviceDialogLoading = ref(false)            // 设备列表加载状态
const devices = ref<Device[]>([])                 // 设备列表
const currentCard = ref<Card | null>(null)        // 当前选中的卡密
const bindFormRef = ref<FormInstance>()           // 绑定表单引用

/**
 * 绑定表单数据
 */
const bindForm = ref({
  card_key: '',
  device_name: ''
})

/**
 * 表单验证规则
 */
const bindRules: FormRules = {
  card_key: [
    { required: true, message: '请输入卡密', trigger: 'blur' },
    { min: 19, max: 19, message: '卡密格式为 XXXX-XXXX-XXXX-XXXX', trigger: 'blur' }
  ],
  device_name: [
    { max: 50, message: '设备名称最多50个字符', trigger: 'blur' }
  ]
}


/**
 * 格式化卡密显示
 * @description 将卡密格式化为 XXXX-XXXX-XXXX-XXXX
 * @param key 卡密字符串
 * @returns 格式化后的卡密
 */
const formatCardKey = (key: string) => {
  if (!key) return ''
  return key.replace(/(\w{4})(?=\w)/g, '$1-')
}

/**
 * 格式化日期
 * @description 将 ISO 8601 格式的时间格式化为可读格式
 * @param dateStr 日期字符串
 * @returns 格式化后的日期
 */
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 获取卡密状态类型
 * @description 根据卡密状态返回对应的 Element Plus 标签类型
 * @param status 卡密状态
 * @returns 标签类型
 */
const getCardStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    unused: 'info',
    used: 'success',
    disabled: 'danger'
  }
  return statusMap[status] || 'info'
}

/**
 * 获取卡密状态文本
 * @description 根据卡密状态返回对应的中文文本
 * @param status 卡密状态
 * @returns 中文文本
 */
const getCardStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    unused: '未使用',
    used: '已使用',
    disabled: '已禁用'
  }
  return statusMap[status] || '未知'
}

/**
 * 加载用户信息
 */
const loadUserInfo = async () => {
  try {
    // 从 Store 中获取用户基本信息
    userInfo.value = {
      app_id: '',
      device_id: userStore.username || ''
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

/**
 * 加载卡密列表
 */
const loadCards = async () => {
  cardsLoading.value = true
  try {
    const response = await getMyCards()
    const data = response.data || response
    cards.value = data.cards || []
    // 假设不存在 setHasCard 方法,直接访问 hasCard 状态
    // userStore.setHasCard(data.has_card)
  } catch (error) {
    ElMessage.error('加载卡密列表失败')
    console.error('加载卡密列表失败:', error)
  } finally {
    cardsLoading.value = false
  }
}

/**
 * 绑定卡密
 */
const handleBindCard = async () => {
  if (!bindFormRef.value) return

  await bindFormRef.value.validate(async (valid) => {
    if (!valid) return

    bindLoading.value = true
    try {
      const deviceId = userStore.username || ''  // 使用用户名作为设备ID
      await bindCard({
        card_key: bindForm.value.card_key,
        device_id: deviceId,
        device_name: bindForm.value.device_name || undefined
      })

      ElMessage.success('绑定成功')
      bindForm.value.card_key = ''
      bindForm.value.device_name = ''
      bindDialogVisible.value = false
      await loadCards()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '绑定失败')
    } finally {
      bindLoading.value = false
    }
  })
}
/**
 * 加载设备列表
 */
const loadDevices = async () => {
  if (!currentCard.value) return
  deviceDialogLoading.value = true
  try {
    const response = await getCardDetail(currentCard.value.card_id)
    const data = response.data || response
    devices.value = data.devices || []
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('加载设备列表失败:', error)
  } finally {
    deviceDialogLoading.value = false
  }
}

/**
 * 查看卡密绑定的设备
 */
const viewDevices = async (card: Card) => {
  currentCard.value = card
  deviceDialogVisible.value = true
  await loadDevices()
}

/**
 * 解绑设备
 * @description 将指定设备从卡密中解绑
 * @param device 设备信息
 */
const handleUnbindDevice = async (device: Device) => {
  try {
    await ElMessageBox.confirm(
      `确定要解绑设备 "${device.device_name || device.device_id}" 吗？`,
      '确认解绑',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (!currentCard.value?.card_id) return

    await unbindDevice({
      card_id: currentCard.value.card_id,
      device_id: device.device_id
    })

    ElMessage.success('设备解绑成功')
    // 重新加载设备列表
    await loadDevices()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '解绑设备失败')
      console.error('解绑设备失败:', error)
    }
  }
}

/**
 * 滚动到绑定表单
 * @description 方便用户快速定位到绑定表单
 */
const scrollToBindForm = () => {
  const bindCardElement = document.querySelector('.bind-card')
  if (bindCardElement) {
    bindCardElement.scrollIntoView({ behavior: 'smooth' })
  }
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadUserInfo()
  loadCards()
})
</script>

<style scoped>
@reference "../../styles/index.css";

.profile-container {
  @apply w-full h-full;
  @apply p-8;
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  min-height: calc(100vh - 64px);
}

/* 页面头部 */
.profile-header {
  @apply flex justify-between items-center mb-8;
}

.profile-title {
  @apply text-3xl font-bold text-gray-900;
  @apply mb-2;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-subtitle {
  @apply text-base text-gray-600;
}

.header-actions {
  @apply flex gap-4;
}

.bind-btn {
  @apply px-6 py-2.5;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white font-medium rounded-xl;
  @apply shadow-lg shadow-blue-500/20;
  transition: all 0.3s ease;
}

.bind-btn:hover {
  @apply shadow-xl shadow-blue-500/30;
  transform: translateY(-2px);
}

/* 页面内容区域 */
.profile-content {
  @apply space-y-6;
}

/* 用户信息卡片 */
.info-card {
  @apply bg-white rounded-2xl p-8;
  @apply shadow-sm border border-gray-100;
  transition: all 0.3s ease;
}

.info-card:hover {
  @apply shadow-lg shadow-blue-500/10;
}

.card-header {
  @apply flex justify-between items-center mb-6;
  @apply pb-4 border-b border-gray-100;
}

.card-title {
  @apply text-xl font-bold text-gray-900;
  @apply flex items-center gap-2;
}

.title-icon {
  @apply text-blue-600;
}

.user-info-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}

.info-item {
  @apply flex flex-col gap-2;
}

.avatar-section {
  @apply col-span-full flex justify-center mb-4;
}

.user-avatar {
  @apply bg-gradient-to-br from-blue-500 to-purple-600;
  @apply text-white;
  @apply shadow-lg;
}

.info-label {
  @apply text-sm text-gray-600 font-medium;
}

.info-value {
  @apply text-lg font-semibold text-gray-900;
}

.info-tag {
  @apply text-sm;
  @apply px-3 py-1;
  @apply rounded-md;
  height: 28px;
  line-height: 20px;
}

.device-id {
  @apply font-mono text-sm;
  @apply bg-gray-100 px-2 py-1 rounded;
}

/* 管理员快捷操作卡片 */
.quick-actions-card {
  @apply bg-white rounded-2xl p-8;
  @apply shadow-sm border border-gray-100;
  transition: all 0.3s ease;
}

.quick-actions-card:hover {
  @apply shadow-lg shadow-blue-500/10;
}

.quick-actions-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
}

.action-card {
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  @apply rounded-xl p-6;
  @apply border border-gray-200;
  @apply flex flex-col items-center justify-center gap-3;
  @apply transition-all duration-300;
  @apply cursor-pointer;
  @apply no-underline;
}

.action-card:hover {
  @apply shadow-lg shadow-blue-500/20;
  @apply border-blue-300;
  @apply bg-gradient-to-br from-blue-50 to-purple-50;
  transform: translateY(-4px);
}

.action-icon {
  @apply text-blue-600;
}

.action-card:hover .action-icon {
  @apply text-purple-600;
}

.action-label {
  @apply text-base font-bold text-gray-900;
}

.action-desc {
  @apply text-sm text-gray-600;
}

/* 卡密列表卡片 */
.cards-card {
  @apply bg-white rounded-2xl p-8;
  @apply shadow-sm border border-gray-100;
  transition: all 0.3s ease;
}

.cards-card:hover {
  @apply shadow-lg shadow-blue-500/10;
}

.cards-list {
  @apply min-h-[300px];
}

.empty-state {
  @apply py-12;
}

.cards-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}

/* 单个卡密项 */
.card-item {
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  @apply rounded-xl p-6;
  @apply border border-gray-200;
  @apply transition-all duration-300;
}

.card-item:hover {
  @apply shadow-lg shadow-blue-500/20;
  @apply border-blue-300;
  transform: translateY(-2px);
}

.card-header-row {
  @apply flex justify-between items-center mb-4;
  @apply pb-4 border-b border-gray-200;
}

.card-key {
  @apply font-mono text-base font-bold text-gray-900;
  @apply bg-white px-3 py-1.5 rounded-lg;
  @apply shadow-sm;
}

.card-body {
  @apply space-y-3 mb-4;
}

.card-row {
  @apply flex justify-between items-start;
  @apply py-2;
}

.card-row.permissions {
  @apply flex-col gap-2;
  @apply items-start;
}

.card-label {
  @apply text-sm text-gray-600 font-medium;
}

.card-value {
  @apply text-sm text-gray-900 font-semibold;
}

.permission-tags {
  @apply flex flex-wrap gap-2;
}

.permission-tag {
  @apply text-xs;
}

.no-permissions {
  @apply text-sm text-gray-400 italic;
}

.card-footer {
  @apply pt-4 border-t border-gray-200;
}

/* 设备列表弹窗 */
.device-list {
  @apply min-h-[300px];
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-container {
    @apply p-4;
  }

  .profile-header {
    @apply flex-col items-start gap-4;
  }

  .user-info-grid {
    @apply grid-cols-1;
  }

  .quick-actions-grid {
    @apply grid-cols-2;
  }

  .cards-grid {
    @apply grid-cols-1;
  }
}
</style>

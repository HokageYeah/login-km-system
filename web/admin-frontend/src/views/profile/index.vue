<template>
  <div class="profile-container">
    <section class="profile-hero">
      <div class="hero-main">
        <div class="hero-avatar-wrap">
          <el-avatar :size="96" class="user-avatar">
            <el-icon :size="48"><User /></el-icon>
          </el-avatar>
        </div>

        <div class="hero-copy">
          <span class="hero-badge">Profile Center</span>
          <h1 class="profile-title">个人中心</h1>
          <p class="profile-subtitle">
            集中查看账户信息、当前状态、卡密使用情况与设备绑定情况，让个人信息展示更清晰、更容易判断当前授权状态。
          </p>

          <div class="hero-tags">
            <el-tag :type="userStore.role === 'admin' ? 'danger' : 'primary'" class="hero-tag" effect="light">
              {{ userStore.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
            <el-tag :type="userStore.userStatus === 'normal' ? 'success' : 'danger'" class="hero-tag" effect="light">
              {{ userStore.userStatus === 'normal' ? '账户正常' : '账户封禁' }}
            </el-tag>
            <el-tag v-if="!userStore.isAdmin" :type="cards.length > 0 ? 'success' : 'warning'" class="hero-tag" effect="light">
              {{ cards.length > 0 ? `已绑定 ${cards.length} 张卡密` : '暂未绑定卡密' }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="hero-actions">
        <div class="hero-status-card">
          <span>当前用户</span>
          <strong>{{ userStore.username || '-' }}</strong>
        </div>
        <div class="hero-status-card">
          <span>最近状态</span>
          <strong>{{ userStore.userStatus === 'normal' ? '可正常使用' : '受限中' }}</strong>
        </div>
        <!-- <div v-if="userInfo" class="hero-status-card">
              <span class="hero-info-label">应用 ID</span>
              <strong class="hero-info-value">{{ userInfo.app_id || '未设置' }}</strong>
            </div>
        <div v-if="userInfo" class="hero-status-card">
            <span class="hero-info-label">设备 ID</span>
            <strong class="hero-info-value hero-info-code">{{ userInfo.device_id || '未设置' }}</strong>
        </div> -->
        <el-button
          v-if="!userStore.isAdmin"
          type="primary"
          :icon="Ticket"
          @click="bindDialogVisible = true"
          class="bind-btn"
        >
          绑定卡密
        </el-button>
        <el-button
          v-if="!userStore.isAdmin"
          circle
          :icon="QuestionFilled"
          @click="tipsDialogVisible = true"
          class="help-btn"
        />
      </div>
    </section>

    <section class="metrics-grid">
      <article v-for="item in profileMetrics" :key="item.label" class="metric-card">
        <div class="metric-head">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
        <p>{{ item.desc }}</p>
      </article>
    </section>

    <section class="profile-main-grid">
      <div class="left-column">
        <article class="panel-card info-card">
          <div class="card-header">
            <div>
              <p class="card-eyebrow">Usage Summary</p>
              <h2 class="card-title">
                <el-icon class="title-icon"><Monitor /></el-icon>
                状态摘要
              </h2>
            </div>
          </div>

          <div class="info-summary-block">
            <div class="status-list">
              <div v-for="item in statusSummary" :key="item.label" class="status-item">
                <span class="status-dot" :class="item.levelClass" />
                <div class="status-body">
                  <strong>{{ item.label }}</strong>
                  <p>{{ item.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>

      <div class="right-column">
        <article v-if="userStore.isAdmin" class="panel-card quick-actions-card">
          <div class="card-header">
            <div>
              <p class="card-eyebrow">Admin Shortcuts</p>
              <h2 class="card-title">
                <el-icon class="title-icon"><Operation /></el-icon>
                快捷操作
              </h2>
            </div>
          </div>
          <div class="quick-actions-grid">
            <router-link to="/users" class="action-card">
              <el-icon class="action-icon" :size="28"><User /></el-icon>
              <span class="action-label">用户管理</span>
              <span class="action-desc">管理系统用户</span>
            </router-link>
            <router-link to="/cards" class="action-card">
              <el-icon class="action-icon" :size="28"><Ticket /></el-icon>
              <span class="action-label">卡密管理</span>
              <span class="action-desc">生成和管理卡密</span>
            </router-link>
            <router-link to="/devices" class="action-card">
              <el-icon class="action-icon" :size="28"><Monitor /></el-icon>
              <span class="action-label">设备管理</span>
              <span class="action-desc">查看绑定设备</span>
            </router-link>
            <router-link to="/apps" class="action-card">
              <el-icon class="action-icon" :size="28"><Grid /></el-icon>
              <span class="action-label">应用管理</span>
              <span class="action-desc">管理应用列表</span>
            </router-link>
          </div>
        </article>
      </div>
    </section>

    <section class="panel-card cards-card">
      <div class="card-header">
        <div>
          <p class="card-eyebrow">My Cards</p>
          <h2 class="card-title">
            <el-icon class="title-icon"><Ticket /></el-icon>
            我的卡密
          </h2>
        </div>
        <div class="cards-header-meta">
          <span>总数 {{ cards.length }}</span>
          <span>设备绑定 {{ totalBoundDevices }}</span>
        </div>
      </div>

      <div v-loading="cardsLoading" class="cards-list">
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

        <div v-else class="cards-grid">
          <div
            v-for="card in cards"
            :key="card.card_id"
            class="card-item"
          >
            <div class="card-header-row">
              <div>
                <div class="card-key">{{ formatCardKey(card.card_key) }}</div>
                <div class="card-subline">
                  <span>{{ getCardStatusText(card.status) }}</span>
                  <span>{{ getCardHealthText(card) }}</span>
                </div>
              </div>
              <el-tag
                :type="getCardStatusType(card.status)"
                size="default"
              >
                {{ getCardStatusText(card.status) }}
              </el-tag>
            </div>

            <div class="card-highlights">
              <div class="highlight-box">
                <span>过期时间</span>
                <strong>{{ formatDate(card.expire_time) }}</strong>
              </div>
              <div class="highlight-box">
                <span>设备绑定</span>
                <strong>{{ card.bind_devices || 0 }} / {{ card.max_device_count }}</strong>
              </div>
            </div>

            <div class="card-body">
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

              <div v-if="card.remark" class="card-row card-remark-row">
                <span class="card-label">备注</span>
                <span class="card-value">{{ card.remark }}</span>
              </div>
            </div>

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
    </section>

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

    <el-dialog
      v-model="tipsDialogVisible"
      title="使用提示"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="tips-list">
        <div v-for="item in personalTips" :key="item.title" class="tip-item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.text }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="tipsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

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
 * @description 功能保持不变，重点优化展示结构：
 * 1. 把账户信息、授权状态、卡密概览拆成更清晰的模块；
 * 2. 用现有卡密数据派生摘要指标，方便用户快速判断当前状态；
 * 3. 增加中文日志，方便后续调试个人中心的加载流程。
 */
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { User, Ticket, Monitor, Grid, Operation, QuestionFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getMyCards, bindCard, unbindDevice, getCardDetail } from '@/api/card'
import type { Card, Device } from '@/types'

const userStore = useUserStore()

const userInfo = ref<any>(null)                   // 用户详细信息
const cards = ref<Card[]>([])                    // 卡密列表
const cardsLoading = ref(false)                  // 卡密加载状态
const bindLoading = ref(false)                   // 绑定加载状态
const bindDialogVisible = ref(false)             // 绑定弹窗显示状态
const tipsDialogVisible = ref(false)             // 使用提示弹窗显示状态
const deviceDialogVisible = ref(false)           // 设备列表弹窗显示状态
const deviceDialogLoading = ref(false)           // 设备列表加载状态
const devices = ref<Device[]>([])                // 设备列表
const currentCard = ref<Card | null>(null)       // 当前选中的卡密
const bindFormRef = ref<FormInstance>()          // 绑定表单引用

const bindForm = ref({
  card_key: '',
  device_name: ''
})

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
 * 卡密派生统计
 * @description 不新增接口，完全基于当前卡密列表做摘要展示。
 */
const activeCardCount = computed(() => cards.value.filter(card => card.status === 'used').length)
const reserveCardCount = computed(() => cards.value.filter(card => card.status === 'unused').length)
const disabledCardCount = computed(() => cards.value.filter(card => card.status === 'disabled').length)
const totalBoundDevices = computed(() => cards.value.reduce((sum, card) => sum + (card.bind_devices || 0), 0))
const totalMaxDevices = computed(() => cards.value.reduce((sum, card) => sum + card.max_device_count, 0))

const profileMetrics = computed(() => {
  return [
    {
      label: '已绑定卡密',
      value: `${cards.value.length}`,
      desc: userStore.isAdmin ? '管理员账号通常不依赖卡密，也可在这里查看个人绑定情况。' : '当前账号下已经绑定的卡密总数。'
    },
    {
      label: '已使用卡密',
      value: `${activeCardCount.value}`,
      desc: '用于快速判断当前账号已有多少张卡密正在实际使用。'
    },
    {
      label: '库存卡密',
      value: `${reserveCardCount.value}`,
      desc: '表示当前账号下仍未启用或未消耗的卡密数量。'
    },
    {
      label: '设备绑定数',
      value: `${totalBoundDevices.value} / ${totalMaxDevices.value}`,
      desc: '统计当前账号下所有卡密已绑定设备数与总可绑定上限。'
    }
  ]
})

const statusSummary = computed(() => {
  return [
    {
      label: '账户状态',
      text: userStore.userStatus === 'normal'
        ? '当前账户状态正常，可以继续执行卡密绑定、查看设备等操作。'
        : '当前账户状态异常或已封禁，部分操作可能会受到限制。',
      levelClass: userStore.userStatus === 'normal' ? 'level-success' : 'level-danger'
    },
    {
      label: '卡密绑定情况',
      text: cards.value.length > 0
        ? `当前共绑定 ${cards.value.length} 张卡密，其中已使用 ${activeCardCount.value} 张，库存 ${reserveCardCount.value} 张。`
        : '当前还没有绑定任何卡密，如需使用系统功能可以先绑定卡密。',
      levelClass: cards.value.length > 0 ? 'level-info' : 'level-warning'
    },
    {
      label: '设备使用情况',
      text: totalMaxDevices.value > 0
        ? `当前共绑定设备 ${totalBoundDevices.value} 台，可绑定设备总上限 ${totalMaxDevices.value} 台。`
        : '当前没有可统计的设备绑定数据。',
      levelClass: totalBoundDevices.value > 0 ? 'level-success' : 'level-info'
    },
    {
      label: '风险提示',
      text: disabledCardCount.value > 0
        ? `当前存在 ${disabledCardCount.value} 张已禁用卡密，建议检查授权有效性和备注信息。`
        : '当前没有禁用卡密，授权状态整体较稳定。',
      levelClass: disabledCardCount.value > 0 ? 'level-warning' : 'level-success'
    }
  ]
})

const personalTips = computed(() => {
  return [
    {
      title: '先绑定后使用',
      text: '如果当前没有卡密，可以直接点击右上角“绑定卡密”，绑定成功后再查看设备和授权信息。'
    },
    {
      title: '关注过期时间',
      text: '卡密过期后会影响授权有效性，建议优先关注卡片中的过期时间和备注信息。'
    },
    {
      title: '设备过多时及时清理',
      text: '如果设备绑定数量接近上限，可以进入设备列表解绑不再使用的设备。'
    }
  ]
})

const formatCardKey = (key: string) => {
  if (!key) return ''
  return key.replace(/(\w{4})(?=\w)/g, '$1-')
}

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

const getCardStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    unused: 'info',
    used: 'success',
    disabled: 'danger'
  }
  return statusMap[status] || 'info'
}

const getCardStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    unused: '未使用',
    used: '已使用',
    disabled: '已禁用'
  }
  return statusMap[status] || '未知'
}

/**
 * 卡密状态补充文案
 * @description 用于卡片上展示更容易理解的健康提示。
 */
const getCardHealthText = (card: Card) => {
  if (card.status === 'disabled') return '当前不可用'
  if ((card.bind_devices || 0) >= card.max_device_count) return '设备已满'
  if (card.status === 'used') return '授权中'
  return '待启用'
}

const loadUserInfo = async () => {
  try {
    console.info('[个人中心] 开始加载用户信息')
    userInfo.value = {
      app_id: '',
      device_id: userStore.username || ''
    }
    console.info('[个人中心] 用户信息加载完成', userInfo.value)
  } catch (error) {
    console.error('[个人中心] 加载用户信息失败', error)
  }
}

const loadCards = async () => {
  cardsLoading.value = true
  console.info('[个人中心] 开始加载卡密列表')

  try {
    const data = await getMyCards()
    cards.value = data.cards || []
    console.info('[个人中心] 卡密列表加载完成', {
      total: cards.value.length,
      active: activeCardCount.value,
      reserve: reserveCardCount.value,
      disabled: disabledCardCount.value
    })
  } catch (error) {
    ElMessage.error('加载卡密列表失败')
    console.error('[个人中心] 加载卡密列表失败', error)
  } finally {
    cardsLoading.value = false
  }
}

const handleBindCard = async () => {
  if (!bindFormRef.value) return

  await bindFormRef.value.validate(async (valid) => {
    if (!valid) return

    bindLoading.value = true
    console.info('[个人中心] 开始绑定卡密', bindForm.value)

    try {
      const deviceId = userStore.username || ''
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
      console.error('[个人中心] 绑定卡密失败', error)
    } finally {
      bindLoading.value = false
    }
  })
}

const loadDevices = async () => {
  if (!currentCard.value) return
  deviceDialogLoading.value = true
  console.info('[个人中心] 开始加载设备列表', currentCard.value.card_id)

  try {
    const data = await getCardDetail(currentCard.value.card_id)
    devices.value = data.devices || []
    console.info('[个人中心] 设备列表加载完成', {
      cardId: currentCard.value.card_id,
      total: devices.value.length
    })
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('[个人中心] 加载设备列表失败', error)
  } finally {
    deviceDialogLoading.value = false
  }
}

const viewDevices = async (card: Card) => {
  currentCard.value = card
  deviceDialogVisible.value = true
  console.info('[个人中心] 打开设备列表弹窗', {
    cardId: card.card_id,
    cardKey: card.card_key
  })
  await loadDevices()
}

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

    console.info('[个人中心] 开始解绑设备', {
      cardId: currentCard.value.card_id,
      deviceId: device.device_id
    })

    await unbindDevice({
      card_id: currentCard.value.card_id,
      device_id: device.device_id
    })

    ElMessage.success('设备解绑成功')
    await loadDevices()
    await loadCards()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '解绑设备失败')
      console.error('[个人中心] 解绑设备失败', error)
    }
  }
}

onMounted(() => {
  console.info('[个人中心] 页面挂载，开始初始化数据')
  loadUserInfo()
  loadCards()
})
</script>

<style scoped>
@reference "../../styles/index.css";

/*
 * 个人中心（Brutalism 改版）：
 * 纸色底 + 黑框硬阴影面板 + 黄底黑字头像 + 荧光笔主标题。
 * 弹窗/按钮/表格外观统一交给全局 Element Plus 覆盖，这里只处理布局与卡片本身。
 */

.profile-container {
  @apply min-h-full p-6 lg:p-8;
  background: var(--paper);
}

/* 顶部英雄区：黑框硬阴影面板 */
.profile-hero {
  @apply px-6 py-6 lg:px-8 lg:py-7 mb-5;
  @apply flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between;
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal);
}

.hero-main {
  @apply flex flex-col sm:flex-row sm:items-center gap-5;
}

.hero-avatar-wrap {
  @apply shrink-0;
}

/* 头像：黄底黑字贴纸感（直角黑框由全局 el-avatar 覆盖提供） */
.user-avatar {
  background: var(--accent);
  color: var(--ink);
}

.hero-copy {
  @apply max-w-3xl;
}

/* 眉题徽章：黑底黄字标签，替代原蓝色胶囊 */
.hero-badge {
  @apply inline-flex items-center px-3 py-1 text-xs;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  background: var(--ink);
  color: var(--accent);
  font-weight: 800;
}

/* 页面主标题：大号加粗 + 黄色荧光衬底 */
.profile-title {
  @apply mt-4 text-3xl lg:text-4xl;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: var(--ink);
  background: linear-gradient(to top, var(--accent) 32%, transparent 32%);
  display: inline-block;
  padding: 0 0.15em;
}

.profile-subtitle {
  @apply mt-3 text-sm lg:text-base leading-7;
  color: var(--ink-soft);
  font-weight: 600;
}

.hero-tags {
  @apply mt-4 flex flex-wrap gap-2;
}

.hero-actions {
  @apply flex flex-col sm:flex-row sm:flex-wrap gap-3 xl:justify-end;
}

/* 状态小卡：纸色底 + 黑框直角 */
.hero-status-card {
  @apply min-w-[160px] px-4 py-3;
  background: var(--paper);
  border: 2px solid var(--ink);
}

.hero-status-card span {
  @apply block text-xs mb-1;
  color: var(--ink-soft);
  font-weight: 700;
}

.hero-status-card strong {
  @apply text-sm;
  color: var(--ink);
  font-weight: 800;
}

/* 绑定按钮走全局 primary 外观（黑底 → hover 黄），只保留字重 */
.bind-btn {
  font-weight: 700;
}

/* 帮助按钮：交给全局 default 按钮观感 */
.help-btn {
  color: var(--ink-soft);
}

.metrics-grid {
  @apply grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-5;
}

/* 指标卡 / 面板卡：黑框硬阴影 */
.metric-card,
.panel-card {
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal);
}

.metric-card {
  @apply p-5;
}

.metric-head {
  @apply flex items-start justify-between gap-4;
}

.metric-head span {
  @apply text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.metric-head strong {
  @apply text-2xl tabular-nums;
  font-weight: 900;
  color: var(--ink);
}

.metric-card p {
  @apply mt-3 text-sm leading-6;
  color: var(--ink-soft);
  font-weight: 600;
}

.profile-main-grid {
  @apply grid grid-cols-1 xl:grid-cols-[1.18fr_0.82fr] gap-4 mb-5;
}

.left-column,
.right-column {
  @apply space-y-4;
}

.panel-card {
  @apply p-5 lg:p-6;
}

.card-header {
  @apply flex items-start justify-between gap-4 mb-5;
}

.card-eyebrow {
  @apply text-xs uppercase;
  letter-spacing: 0.2em;
  color: var(--ink-soft);
  font-weight: 700;
}

.card-title {
  @apply mt-1 text-xl flex items-center gap-2;
  font-weight: 900;
  color: var(--ink);
}

.title-icon {
  color: var(--ink);
}

.info-summary-block {
  @apply mt-0 pt-0;
}

.status-list,
.tips-list {
  @apply space-y-4;
}

.status-item {
  @apply flex items-start gap-3;
}

/* 状态点：黑框方块（直角），语义色填充 */
.status-dot {
  @apply mt-2 w-3 h-3 shrink-0;
  border: 2px solid var(--ink);
}

.status-body strong,
.tip-item strong {
  @apply block text-sm;
  font-weight: 800;
  color: var(--ink);
}

.status-body p,
.tip-item p {
  @apply mt-1 text-sm leading-6;
  color: var(--ink-soft);
  font-weight: 600;
}

/* 状态语义色：含义保留，色值对齐品牌（成功绿/信息蓝/警告橙/危险红） */
.level-success { background: #1a7f37; }
.level-info { background: var(--accent-blue); }
.level-warning { background: #b45309; }
.level-danger { background: var(--danger); }

.quick-actions-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

/* 快捷入口卡：纸色底 + 黑框，hover 位移放大阴影（按压感） */
.action-card {
  @apply px-5 py-5;
  @apply flex flex-col gap-2 no-underline;
  background: var(--paper);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal-sm);
  transition: transform 0.15s cubic-bezier(0.2, 0, 0, 1),
    box-shadow 0.15s cubic-bezier(0.2, 0, 0, 1);
}

.action-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--ink);
  background: var(--accent-soft);
}

/* 图标色块：黄底黑框直角 */
.action-icon {
  background: var(--accent);
  border: 2px solid var(--ink);
  padding: 6px;
  color: var(--ink);
}

.action-label {
  @apply text-base;
  font-weight: 800;
  color: var(--ink);
}

.action-desc {
  @apply text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.tip-item {
  @apply px-4 py-4;
  background: var(--paper);
  border: 2px solid var(--line-soft);
}

.cards-card {
  @apply p-5 lg:p-6;
}

.cards-header-meta {
  @apply flex flex-wrap gap-3 text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.cards-header-meta span {
  @apply inline-flex items-center px-3 py-1;
  background: var(--paper);
  border: 2px solid var(--ink);
  font-weight: 700;
  color: var(--ink);
}

.cards-list {
  @apply min-h-[260px];
}

.empty-state {
  @apply py-12;
}

.cards-grid {
  @apply grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5;
}

/* 卡密卡片：纸色底黑框，hover 位移放大阴影 */
.card-item {
  @apply p-5;
  background: var(--paper);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal-sm);
  transition: transform 0.15s cubic-bezier(0.2, 0, 0, 1),
    box-shadow 0.15s cubic-bezier(0.2, 0, 0, 1);
}

.card-item:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--ink);
}

.card-header-row {
  @apply flex items-start justify-between gap-4 pb-4;
  border-bottom: 2px solid var(--ink);
}

.card-key {
  @apply font-mono text-base break-all;
  font-weight: 800;
  color: var(--ink);
}

.card-subline {
  @apply mt-2 flex flex-wrap gap-3 text-xs;
  color: var(--ink-soft);
  font-weight: 600;
}

.card-highlights {
  @apply grid grid-cols-2 gap-3 my-4;
}

.highlight-box {
  @apply px-4 py-4;
  background: var(--surface);
  border: 2px solid var(--ink);
}

.highlight-box span {
  @apply block text-xs mb-2;
  color: var(--ink-soft);
  font-weight: 700;
}

.highlight-box strong {
  @apply text-sm leading-6 break-all;
  color: var(--ink);
  font-weight: 800;
}

.card-body {
  @apply space-y-4;
}

.card-row {
  @apply flex justify-between items-start gap-4;
}

.card-row.permissions {
  @apply flex-col gap-2 items-start;
}

.card-remark-row {
  @apply px-4 py-4;
  background: var(--surface);
  border: 2px solid var(--line-soft);
}

.card-label {
  @apply text-sm;
  color: var(--ink-soft);
  font-weight: 600;
}

.card-value {
  @apply text-sm leading-6;
  color: var(--ink);
  font-weight: 700;
}

.permission-tags {
  @apply flex flex-wrap gap-2;
}

.permission-tag {
  @apply text-xs;
}

.no-permissions {
  @apply text-sm italic;
  color: var(--ink-soft);
  font-weight: 600;
}

.card-footer {
  @apply pt-4 mt-4;
  border-top: 2px solid var(--ink);
}

.device-list {
  @apply min-h-[300px];
}

@media (max-width: 768px) {
  .profile-container {
    @apply p-4;
  }

  .profile-hero {
    @apply p-5;
  }

  .profile-title {
    @apply text-3xl;
  }

  .hero-actions {
    @apply flex-col;
  }

  .card-highlights {
    @apply grid-cols-1;
  }

  .cards-grid,
  .quick-actions-grid,
  .metrics-grid {
    @apply grid-cols-1;
  }
}
</style>

<template>
  <!-- 顶部固定区：跑马灯条 + 主导航条，整体 sticky 吸顶（滚动时保持可见） -->
  <div class="topbar-fixed">
    <!-- 品牌跑马灯：黑底黄字，内容从最右侧进场、跑出左侧后再循环 -->
    <div class="top-marquee" aria-hidden="true">
      <div class="marquee-track">
        <span>KM SYSTEM ✦ 授权中心 ✦ 卡密管理 ✦ 设备管控 ✦ 权限校验 ✦ </span>
      </div>
    </div>

    <el-header class="topbar-container">
      <!-- 左侧：折叠按钮与面包屑 -->
      <div class="left-panel">
        <!-- 折叠按钮 -->
        <div
          class="hamburger-container"
          @click="$emit('toggle-collapse')"
        >
          <el-icon :size="20" :class="{ 'is-active': sidebarOpened }">
            <Fold v-if="sidebarOpened" />
            <Expand v-else />
          </el-icon>
        </div>

        <!-- 面包屑导航 -->
        <el-breadcrumb separator="/" class="breadcrumb-container">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
            {{ item.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- 右侧：用户信息与操作 -->
      <div class="right-panel">
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="avatar-wrapper">
            <el-avatar :size="32" class="user-avatar" :icon="UserFilled">
              {{ userStore.username.charAt(0).toUpperCase() }}
            </el-avatar>
            <span class="user-name">{{ userStore.username }}</span>
            <el-icon><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-dropdown">
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
  </div>
</template>

<script setup lang="ts">
/**
 * 顶部导航栏组件
 * @description 包含侧边栏折叠开关、面包屑导航以及用户个人中心入口
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Fold,
  Expand,
  CaretBottom,
  UserFilled
} from '@element-plus/icons-vue'

const props = defineProps<{
  sidebarOpened: boolean
}>()

defineEmits<{
  (e: 'toggle-collapse'): void
}>()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/**
 * 生成面包屑数据
 * @description 基于当前路由Matched数组生成
 */
const breadcrumbs = computed(() => {
  // 暂时简单的取当前路由meta title
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  // 过滤掉首页，因为已经手动添加
  return matched.filter(item => item.path !== '/dashboard' && item.path !== '/').map(item => ({
    title: item.meta.title as string,
    path: item.path
  }))
})

/**
 * 处理下拉菜单命令
 * @param command 命令字符串
 */
const handleCommand = async (command: string) => {
  if (command === 'logout') {
    await userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
@reference "../../styles/index.css";

/*
 * 顶栏（Brutalism 改版 · 第二轮调整）：
 * 结构 = 跑马灯条(28px) + 主导航条(64px)，总高 92px（--topbar-height 令牌）。
 * 整体 sticky 吸顶，滚动时保持可见；内容区用令牌同步计算可用高度。
 */
.topbar-fixed {
  position: sticky;
  top: 0;
  z-index: 20;
}

/* 跑马灯条：黑底黄字，悬停暂停 */
.top-marquee {
  height: 28px;
  overflow: hidden;
  background: var(--ink);
  color: var(--accent);
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.1em;
  line-height: 28px;
  border-bottom: 2px solid var(--ink);
}

.topbar-container {
  @apply h-16 flex items-center justify-between;
  background: var(--surface);
  border-bottom: 2px solid var(--ink);
  padding: 0 16px;
}

.left-panel {
  @apply flex items-center h-full;
}

.hamburger-container {
  @apply flex items-center cursor-pointer px-2 h-9;
  color: var(--ink);
  border: 2px solid transparent;
}

/* 折叠按钮：hover 变为黄色块，与菜单激活态同语言 */
.hamburger-container:hover {
  background: var(--accent);
  border-color: var(--ink);
  box-shadow: 2px 2px 0 var(--ink);
}

.breadcrumb-container {
  @apply ml-4 select-none;
}

.right-panel {
  @apply flex items-center h-full;
}

.avatar-wrapper {
  @apply flex items-center cursor-pointer outline-none px-2 py-1;
  border: 2px solid transparent;
}

.avatar-wrapper:hover {
  background: var(--accent-soft);
  border-color: var(--ink);
}

/* 头像：电光黄底黑字，直角黑框（全局已改直角） */
.user-avatar {
  background: var(--accent);
  color: var(--ink);
  margin-right: 8px;
}

.user-name {
  @apply text-sm mr-1;
  color: var(--ink);
  font-weight: 700;
}
</style>

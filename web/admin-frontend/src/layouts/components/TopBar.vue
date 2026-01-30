<template>
  <el-header class="topbar-container glass-card">
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
.topbar-container {
  @reference "../../styles/index.css";
  @apply h-16 flex items-center justify-between px-4 bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-20;
  /* Reset element-plus header default padding if needed */
  padding: 0 16px;
}

.left-panel {
  @apply flex items-center h-full;
}

.hamburger-container {
  @apply px-2 cursor-pointer transition-colors duration-300 flex items-center text-gray-600 hover:text-blue-500;
}

.breadcrumb-container {
  @apply ml-4 select-none;
}

.right-panel {
  @apply flex items-center h-full;
}

.avatar-wrapper {
  @apply flex items-center cursor-pointer outline-none hover:bg-gray-50 px-2 py-1 rounded-lg transition-colors;
}

.user-avatar {
  @apply bg-blue-500 text-white mr-2;
}

.user-name {
  @apply text-sm font-medium text-gray-700 mr-1;
}

:deep(.user-dropdown) {
  @apply rounded-xl border-gray-100 shadow-lg;
}
</style>

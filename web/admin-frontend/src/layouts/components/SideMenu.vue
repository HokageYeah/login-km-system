<template>
  <el-aside
    :width="isCollapse ? '64px' : '260px'"
    class="sidebar-container"
  >
    <!-- Logo 区域 -->
    <div class="logo-container" :class="{ 'collapsed': isCollapse }">
      <img src="@/assets/logo.svg" alt="logo" class="logo-img" v-if="false" /> <!-- 暂时隐藏图片logo -->
      <el-icon class="logo-icon" v-else><ElementPlus /></el-icon>
      <h1 class="logo-title" v-show="!isCollapse">卡密管理系统</h1>
    </div>

    <!-- 菜单区域 -->
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        class="sidebar-menu"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#fff"
        :collapse-transition="false"
        mode="vertical"
      >
        <!-- 递归生成菜单 -->
        <!-- 暂时写死菜单以验证布局，后续结合路由动态生成 -->
        <el-menu-item index="/dashboard" @click="handleMenuClick('/dashboard')">
          <el-icon><DataLine /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-menu-item index="/users" @click="handleMenuClick('/users')">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/cards" @click="handleMenuClick('/cards')">
          <el-icon><Ticket /></el-icon>
          <template #title>卡密管理</template>
        </el-menu-item>
        
        <el-menu-item index="/devices" @click="handleMenuClick('/devices')">
          <el-icon><Monitor /></el-icon>
          <template #title>设备管理</template>
        </el-menu-item>

        <el-menu-item index="/apps" @click="handleMenuClick('/apps')">
          <el-icon><Grid /></el-icon>
          <template #title>应用管理</template>
        </el-menu-item>
        
      </el-menu>
    </el-scrollbar>
  </el-aside>
</template>

<script setup lang="ts">
/**
 * 侧边栏组件
 * @description 应用左侧导航菜单，支持折叠展开，响应式布局。
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataLine,
  User,
  Ticket,
  Monitor,
  Grid,
  ElementPlus
} from '@element-plus/icons-vue'

// Props 定义
const props = defineProps<{
  isCollapse: boolean
}>()

const route = useRoute()
const router = useRouter()

/**
 * 当前激活的菜单项
 * @description 根据当前路由路径高亮对应的菜单
 */
const activeMenu = computed(() => {
  const { path } = route
  return path
})

/**
 * 菜单点击处理
 * @param path 路由路径
 */
const handleMenuClick = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.sidebar-container {
  @reference "../../styles/index.css";
  @apply h-screen bg-slate-900 border-r border-slate-800 transition-all duration-300 flex flex-col;
}

/* Logo 区域样式 */
.logo-container {
  @apply h-16 flex items-center justify-center relative overflow-hidden transition-all duration-300;
  /* background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); */
}

.logo-container.collapsed {
  @apply px-0;
}

.logo-icon {
  @apply text-blue-500 text-2xl mr-2;
  transition: all 0.3s;
}

.collapsed .logo-icon {
  @apply mr-0 text-3xl;
}

.logo-title {
  @apply text-white font-bold text-lg whitespace-nowrap;
  transition: opacity 0.3s;
}

/* 菜单样式复写 */
.sidebar-menu {
  @apply border-none;
}

:deep(.el-menu-item) {
  @apply mx-2 my-1 rounded-lg transition-all duration-300 font-medium;
}

:deep(.el-menu-item:hover) {
  @apply bg-slate-800 text-white;
}

:deep(.el-menu-item.is-active) {
  @apply bg-blue-600 text-white shadow-lg shadow-blue-500/30;
}

:deep(.el-menu-item .el-icon) {
  @apply text-lg;
}

/* 折叠时候icon居中 */
:deep(.el-menu--collapse .el-menu-item .el-icon) {
  @apply mx-0;
}
</style>

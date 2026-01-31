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
        <template v-for="menu in menus" :key="menu.path">
          <!-- 有子菜单的情况 -->
          <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.path">
            <template #title>
              <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
              <span>{{ menu.title }}</span>
            </template>
            <!-- 递归渲染子菜单 -->
            <template v-for="subMenu in menu.children" :key="subMenu.path">
              <el-menu-item :index="subMenu.path" @click="handleMenuClick(subMenu.path)">
                <el-icon><component :is="getIconComponent(subMenu.icon)" /></el-icon>
                <template #title>{{ subMenu.title }}</template>
              </el-menu-item>
            </template>
          </el-sub-menu>
          <!-- 没有子菜单的情况 -->
          <el-menu-item v-else :index="menu.path" @click="handleMenuClick(menu.path)">
            <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
            <template #title>{{ menu.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>
  </el-aside>
</template>

<script setup lang="ts">
/**
 * 侧边栏组件
 * @description 应用左侧导航菜单，支持折叠展开，响应式布局。根据路由配置和用户权限动态生成菜单。
 */
import { computed, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { generateMenus } from '@/utils/menu'
import router from '@/router'
import {
  DataLine,
  User,
  Ticket,
  Monitor,
  Grid,
  ElementPlus,
  DataAnalysis,
  Lock
} from '@element-plus/icons-vue'
import type { MenuItem } from '@/utils/menu'

// Props 定义
const props = defineProps<{
  isCollapse: boolean
}>()

const route = useRoute()
const vueRouter = useRouter()

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
  vueRouter.push(path)
}

/**
 * 生成菜单数据
 * @description 根据路由配置和用户权限动态生成菜单
 */
const menus = computed<MenuItem[]>(() => {
  console.log('router.options.routes', router.options.routes)
  const generated = generateMenus(router.options.routes)
  console.log('generated menus', generated)
  return generated
})

/**
 * 图标组件映射
 * @description 将字符串图标名称映射到对应的 Element Plus 图标组件
 */
const iconMap = markRaw({
  DataLine,
  User,
  Ticket,
  Monitor,
  Grid,
  DataAnalysis,
  Lock,
})

/**
 * 获取图标组件
 * @param iconName 图标名称字符串
 * @returns 对应的图标组件，如果找不到则返回默认图标
 */
const getIconComponent = (iconName: string | undefined) => {
  if (!iconName) {
    return ElementPlus // 默认图标
  }
  return iconMap[iconName as keyof typeof iconMap] || ElementPlus
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

<template>
  <el-aside
    :width="isCollapse ? '64px' : '260px'"
    class="sidebar-container"
  >
    <!-- Logo 区域：黑底色块 + 黄色图标，粗野主义品牌锚点 -->
    <div class="logo-container" :class="{ 'collapsed': isCollapse }">
      <img src="@/assets/logo.svg" alt="logo" class="logo-img" v-if="false" /> <!-- 暂时隐藏图片logo -->
      <el-icon class="logo-icon" v-else><ElementPlus /></el-icon>
      <h1 class="logo-title" v-show="!isCollapse">新卡密管理系统</h1>
    </div>

    <!-- 菜单区域 -->
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        class="sidebar-menu"
        background-color="transparent"
        text-color="#57534E"
        active-text-color="#141414"
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
/*
 * 侧边栏（Brutalism 改版）：
 * 纸色底 + 2px 黑色右边框；菜单项直角、激活态黄底黑字 + 硬阴影。
 * 仅调整视觉，菜单生成/权限逻辑不变。
 */
.sidebar-container {
  @reference "../../styles/index.css";
  @apply h-screen flex flex-col;
  background: var(--paper);
  border-right: 2px solid var(--ink);
  transition: width 0.2s cubic-bezier(0.2, 0, 0, 1);
}

/* Logo 区域：黑底色块，黄色方块图标 + 加粗标题 */
.logo-container {
  @apply h-16 flex items-center justify-center relative overflow-hidden;
  background: var(--ink);
  border-bottom: 2px solid var(--ink);
}

.logo-container.collapsed {
  @apply px-0;
}

.logo-icon {
  @apply text-xl mr-2 p-1;
  color: var(--ink);
  background: var(--accent);
  border: 2px solid var(--accent);
}

.collapsed .logo-icon {
  @apply mr-0;
}

.logo-title {
  @apply font-black whitespace-nowrap text-base tracking-wide;
  color: var(--paper);
}

/* 菜单样式复写：直角、加粗、黄色激活态 */
.sidebar-menu {
  @apply border-none;
  padding: 8px;
}

:deep(.el-menu-item) {
  @apply my-1 font-bold;
  border-radius: 0;
  border: 2px solid transparent; /* 预留边框位，激活时加黑框不抖动 */
  height: 44px;
  line-height: 40px;
}

:deep(.el-menu-item:hover) {
  background: var(--accent-soft);
  color: var(--ink);
}

/* 激活项：电光黄底 + 黑框 + 硬阴影，参考站 CTA 的"按压感" */
:deep(.el-menu-item.is-active) {
  background: var(--accent);
  color: var(--ink);
  border: 2px solid var(--ink);
  box-shadow: 3px 3px 0 var(--ink);
}

:deep(.el-sub-menu__title) {
  @apply font-bold;
  border-radius: 0;
  height: 44px;
  line-height: 40px;
}

:deep(.el-sub-menu__title:hover) {
  background: var(--accent-soft);
  color: var(--ink);
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  @apply text-lg;
  color: inherit;
}

/* 折叠时候icon居中 */
:deep(.el-menu--collapse .el-menu-item .el-icon) {
  @apply mx-0;
}
</style>

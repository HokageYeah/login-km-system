<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <SideMenu :is-collapse="isCollapse" class="sidebar-container" />
    
    <!-- 主体区域 -->
    <div class="main-container" :class="{ 'collapsed': isCollapse }">
      <!-- 顶部导航 -->
      <TopBar :sidebar-opened="!isCollapse" @toggle-collapse="toggleCollapse" />
      
      <!-- 内容区域 -->
      <AppMain />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 管理后台布局主组件
 * @description 集成 SideMenu, TopBar 和 AppMain，控制整体布局结构和状态
 */
import { ref } from 'vue'
import SideMenu from './components/SideMenu.vue'
import TopBar from './components/TopBar.vue'
import AppMain from './components/AppMain.vue'

// 侧边栏折叠状态
const isCollapse = ref(false)

/**
 * 切换侧边栏折叠状态
 */
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
.app-wrapper {
  @reference "../styles/index.css";
  @apply flex w-full h-full relative;
}

.sidebar-container {
  @apply fixed top-0 left-0 bottom-0 z-30 transition-all duration-300;
  /* 宽度由组件内部控制，这里不需要显式设置宽度，但需要覆盖层级 */
}

.main-container {
  @apply min-h-screen transition-all duration-300 relative ml-[260px] w-full;
  /* ml-64 = 256px -> 接近 260px */
}

/* 折叠后的主容器左边距 */
.main-container.collapsed {
  @apply ml-[64px];
}
</style>

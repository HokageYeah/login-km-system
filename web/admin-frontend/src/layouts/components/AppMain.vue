<template>
  <section class="app-main">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-transform" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </section>
</template>

<script setup lang="ts">
/**
 * 主内容区域组件
 * @description 负责渲染路由视图，提供页面切换动画
 * 支持一级和二级路由，子路由需要在对应的父组件中添加 <router-view>
 */
</script>

<style scoped>
.app-main {
  @reference "../../styles/index.css";
  /* 减去顶栏总高（跑马灯 28px + 主导航 64px，令牌统一维护）；纸色底由全局设计令牌提供 */
  @apply w-full relative overflow-hidden p-6;
  background: var(--paper);
  min-height: calc(100vh - var(--topbar-height));
}

/* 页面切换动画：更利落的位移淡入 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: opacity 0.18s, transform 0.18s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-8px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(8px);
}
</style>

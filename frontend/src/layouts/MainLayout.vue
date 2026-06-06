<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="layout-aside">
      <div class="logo">
        <el-icon :size="24"><Box /></el-icon>
        <span>马戏团系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        class="layout-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计看板</span>
        </el-menu-item>
        <el-menu-item index="/programs">
          <el-icon><Film /></el-icon>
          <span>剧目管理</span>
        </el-menu-item>
        <el-menu-item index="/props">
          <el-icon><Box /></el-icon>
          <span>道具档案</span>
        </el-menu-item>
        <el-menu-item index="/vehicles">
          <el-icon><Van /></el-icon>
          <span>车辆管理</span>
        </el-menu-item>
        <el-menu-item index="/loading">
          <el-icon><Upload /></el-icon>
          <span>装车登记</span>
        </el-menu-item>
        <el-menu-item index="/unloading">
          <el-icon><Download /></el-icon>
          <span>卸车归库</span>
        </el-menu-item>
        <el-menu-item index="/damage">
          <el-icon><Warning /></el-icon>
          <span>损耗记录</span>
        </el-menu-item>
        <el-menu-item index="/maintenance">
          <el-icon><Tools /></el-icon>
          <span>维保记录</span>
        </el-menu-item>
        <el-menu-item index="/scrap">
          <el-icon><Delete /></el-icon>
          <span>报废管理</span>
        </el-menu-item>
        <el-menu-item index="/tours">
          <el-icon><Calendar /></el-icon>
          <span>巡演任务</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-title">马戏团道具装车与巡演归库系统</div>
        <div class="header-user">
          <el-icon><User /></el-icon>
          <span class="username">管理员</span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  Film,
  Box,
  Van,
  Upload,
  Download,
  Warning,
  User,
  Tools,
  Delete,
  Calendar
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('token')
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #304156;
  height: 100vh;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b2f3a;
}

.layout-menu {
  border-right: none;
  height: calc(100vh - 60px);
}

.layout-header {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #606266;
}

.username {
  font-size: 14px;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>

<template>
  <div class="config-container">
    <el-card shadow="never" class="config-card">
      <template #header>
        <div class="card-header">
          <div class="title-group">
            <el-icon class="title-icon"><Operation /></el-icon>
            <span class="title">全局系统配置</span>
          </div>
          <el-button type="primary" :loading="saving" @click="handleSave">
            <el-icon class="mr-1"><Check /></el-icon> 保存并生效
          </el-button>
        </div>
      </template>

      <el-form :model="configForm" label-position="top" class="config-form">
        <el-tabs tab-position="left" class="config-tabs">
          <el-tab-pane label="AI 引擎设置">
            <div class="tab-content">
              <h4 class="section-title">大模型参数</h4>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="首选 AI 模型">
                    <el-select v-model="configForm.aiModel" class="w-full">
                      <el-option label="GPT-4o (全能型)" value="gpt-4o" />
                      <el-option label="GPT-4-Turbo" value="gpt-4-turbo" />
                      <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet" />
                      <el-option label="DeepSeek-V3" value="deepseek-v3" />
                    </el-select>
                    <p class="input-tip">系统将优先调用该模型进行图片解析与报告生成</p>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="API 中转地址">
                    <el-input v-model="configForm.apiBaseUrl" placeholder="https://api.example.com/v1" />
                    <p class="input-tip">用于中转 AI 调用的 API 地址</p>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="API 密钥 (Key)">
                <el-input v-model="configForm.apiKey" type="password" show-password placeholder="sk-..." />
              </el-form-item>
            </div>
          </el-tab-pane>

          <el-tab-pane label="产品与计费">
            <div class="tab-content">
              <h4 class="section-title">业务规则</h4>
              <el-form-item label="生成报告消耗 (次/份)">
                <el-input-number v-model="configForm.reportPrice" :min="1" />
                <p class="input-tip">单份报告核销卡密的次数</p>
              </el-form-item>
              <el-form-item label="默认卡密有效期 (天)">
                <el-input-number v-model="configForm.defaultValidDays" :min="1" />
              </el-form-item>
              <el-form-item label="开启卡密校验">
                <el-switch v-model="configForm.enableCardVerify" />
                <p class="input-tip">关闭后用户无需输入卡密即可生成报告 (仅限测试使用)</p>
              </el-form-item>
            </div>
          </el-tab-pane>

          <el-tab-pane label="系统安全">
            <div class="tab-content">
              <h4 class="section-title">运行安全</h4>
              <el-form-item label="维护模式">
                <el-switch v-model="configForm.maintenanceMode" active-color="#ef4444" />
                <p class="input-tip text-danger">开启后前端将显示维护中，暂停所有服务</p>
              </el-form-item>
              <el-form-item label="允许新用户注册 (后台)">
                <el-switch v-model="configForm.allowRegistration" />
              </el-form-item>
              <el-form-item label="日志留存天数">
                <el-input-number v-model="configForm.logRetentionDays" :min="7" :max="365" />
              </el-form-item>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, Check } from '@element-plus/icons-vue'

const saving = ref(false)

const configForm = reactive({
  aiModel: 'gpt-4o',
  apiBaseUrl: 'https://shiyunapi.com/v1',
  apiKey: '********************************',
  reportPrice: 1,
  defaultValidDays: 365,
  enableCardVerify: true,
  maintenanceMode: false,
  allowRegistration: false,
  logRetentionDays: 30
})

const handleSave = () => {
  saving.value = true
  // 模拟保存接口
  setTimeout(() => {
    saving.value = false
    ElMessage.success({
      message: '系统配置已保存，部分设置将在重启服务后生效',
      duration: 3000
    })
  }, 1000)
}
</script>

<style scoped>
.config-container {
  animation: fadeIn 0.5s ease-out;
}

.config-card {
  border-radius: 12px;
  border: none;
  min-height: 600px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
  color: #6366f1;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.config-tabs {
  height: 500px;
}

.tab-content {
  padding: 0 40px;
  max-width: 1000px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.input-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
  line-height: 1.4;
}

.text-danger {
  color: #ef4444;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 14px;
}

:deep(.el-tabs__active-bar) {
  width: 3px;
  border-radius: 3px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

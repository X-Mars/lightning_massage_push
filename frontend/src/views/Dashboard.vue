<template>
  <div class="dashboard-container">
    <el-row :gutter="28" class="statistics-row">
      <!-- 统计卡片 -->
      <el-col :span="8" v-for="(card, index) in statisticsCards" :key="index">
        <el-card class="statistics-card" :body-style="{ padding: '28px' }">
          <div class="card-content">
            <div class="icon-container" :style="{ backgroundColor: card.bgColor }">
              <el-icon :size="32" :color="card.iconColor"><component :is="card.icon" /></el-icon>
            </div>
            <div class="statistics-info">
              <div class="statistics-title">{{ card.title }}</div>
              <div class="statistics-number">{{ card.count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="28" class="chart-row">
      <!-- 消息发送趋势图 -->
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>消息发送趋势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button value="week">本周</el-radio-button>
                <el-radio-button value="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="lineChartRef"></div>
        </el-card>
      </el-col>

      <!-- 机器人类型占比图 -->
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>机器人类型占比</span>
            </div>
          </template>
          <div class="chart-container" ref="pieChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近消息记录 -->
    <el-row>
      <el-col :span="24">
        <el-card class="log-card">
          <template #header>
            <div class="log-header">
              <span>最近消息记录</span>
              <el-button type="primary" text @click="viewMoreLogs">查看更多</el-button>
            </div>
          </template>
          <el-table :data="recentLogs" stripe style="width: 100%">
            <el-table-column prop="template_name" label="模板名称" width="180"></el-table-column>
            <el-table-column prop="robot_name" label="机器人" width="180"></el-table-column>
            <el-table-column prop="created_at" label="发送时间" width="160" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status ? 'success' : 'danger'">
                  {{ scope.row.status ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column width="100" fixed="right">
              <template #default="scope">
                <el-button type="primary" text size="small" @click="viewLog(scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { Document, ChatDotRound, SetUp } from '@element-plus/icons-vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { dashboardApi } from '../api';
import type { MessageLog } from '../types';

const router = useRouter();
const timeRange = ref('week');
const lineChartRef = ref<HTMLElement | null>(null);
const pieChartRef = ref<HTMLElement | null>(null);
let lineChart: echarts.ECharts | null = null;
let pieChart: echarts.ECharts | null = null;
const loading = ref(false);

// 统计数据
const statisticsCards = reactive([
  {
    title: '模板总数',
    count: 0,
    icon: 'Document',
    bgColor: 'rgba(64, 158, 255, 0.15)',
    iconColor: '#409EFF'
  },
  {
    title: '机器人总数',
    count: 0,
    icon: 'SetUp',
    bgColor: 'rgba(103, 194, 58, 0.15)',
    iconColor: '#67C23A'
  },
  {
    title: '本月发送消息',
    count: 0,
    icon: 'ChatDotRound',
    bgColor: 'rgba(230, 162, 60, 0.15)',
    iconColor: '#E6A23C'
  }
]);

// 最近日志数据
const recentLogs = ref<MessageLog[]>([]);

// 初始化图表
const initCharts = async (forceRefresh = false) => {
  if (forceRefresh && lineChart) {
    lineChart.dispose();
    lineChart = null;
  }
  
  if (forceRefresh && pieChart) {
    pieChart.dispose();
    pieChart = null;
  }
  
  try {
    // 获取图表数据
    const chartResponse = await dashboardApi.getCharts(timeRange.value);
    const chartData = chartResponse.data;
    
    // 更新线图表
    if (lineChartRef.value) {
      if (!lineChart) {
        lineChart = echarts.init(lineChartRef.value);
      }
      
      const trendData = chartData.trend_data;
      const lineOption = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['成功', '失败']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: trendData.categories
        },
        yAxis: {
          type: 'value'
        },
        series: trendData.series.map((item: any) => ({
          name: item.name,
          type: 'line',
          stack: 'Total',
          areaStyle: { opacity: 0.3 },
          emphasis: {
            focus: 'series'
          },
          data: item.data
        }))
      };
      lineChart.setOption(lineOption);
    }

    // 更新饼图
    if (pieChartRef.value) {
      if (!pieChart) {
        pieChart = echarts.init(pieChartRef.value);
      }
      
      const robotTypeData = chartData.robot_type_stats;
      const pieOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          data: robotTypeData.map((item: any) => item.name)
        },
        series: [
          {
            name: '机器人类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '16',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: robotTypeData
          }
        ]
      };
      pieChart.setOption(pieOption);
    }
  } catch (error) {
    console.error('获取图表数据失败:', error);
    ElMessage.error('获取图表数据失败');
  }
};

// 监听时间范围变化，更新折线图
watch(timeRange, () => {
  // 重新获取并初始化图表
  initCharts(true);
});

// 查看更多日志
const viewMoreLogs = () => {
  router.push('/messages');
};

// 查看日志详情
const viewLog = (log: MessageLog) => {
  ElMessageBox.alert(log.formatted_content, `消息内容 - ${log.template_name}`, {
    dangerouslyUseHTMLString: true
  });
};

// 窗口大小变化时重置图表大小
const handleResize = () => {
  lineChart?.resize();
  pieChart?.resize();
};

// 加载仪表盘数据
const loadDashboardData = async () => {
  loading.value = true;
  try {
    // 1. 加载统计数据
    const statsResponse = await dashboardApi.getStats();
    const statsData = statsResponse.data;
    
    // 更新统计卡片数据
    statisticsCards[0].count = statsData.template_count;
    statisticsCards[1].count = statsData.robot_count;
    statisticsCards[2].count = statsData.current_month_messages;
    
    // 2. 加载图表数据
    await initCharts();
    
    // 3. 加载最近日志数据
    const logsResponse = await dashboardApi.getRecentLogs();
    recentLogs.value = logsResponse.data;
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
    ElMessage.error('加载仪表盘数据失败');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // 加载仪表盘数据
  loadDashboardData();
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
  
  // 在组件卸载前移除事件监听
  return () => {
    window.removeEventListener('resize', handleResize);
    lineChart?.dispose();
    pieChart?.dispose();
  };
});
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  width: 100%;
}

.statistics-row {
  margin-bottom: 28px;
}

.statistics-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
  overflow: hidden;
}

.statistics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

.card-content {
  display: flex;
  align-items: center;
}

.icon-container {
  padding: 16px;
  border-radius: 10px;
  margin-right: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.statistics-card:hover .icon-container {
  transform: scale(1.08);
}

.statistics-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.statistics-title {
  font-size: 15px;
  color: #606266;
  margin-bottom: 12px;
  font-weight: 500;
}

.statistics-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}

.chart-row {
  margin-bottom: 28px;
}

.chart-card {
  margin-bottom: 24px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
  overflow: hidden;
}

.chart-header, .log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.log-card {
  margin-bottom: 24px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
  overflow: hidden;
}
</style>
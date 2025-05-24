import datetime
import calendar
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Template, Robot, MessageLog, RobotType
from .serializers import MessageLogSerializer


class DashboardStatsView(APIView):
    """仪表盘数据统计视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 获取当前用户创建的模板总数
        template_count = Template.objects.filter(created_by=request.user).count()
        
        # 获取当前用户创建的机器人总数
        robot_count = Robot.objects.filter(created_by=request.user).count()
        
        # 获取当前月份
        today = timezone.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 获取本月消息发送总数
        current_month_messages = MessageLog.objects.filter(
            created_by=request.user,
            created_at__gte=first_day
        ).count()
        
        # 构建响应数据
        response_data = {
            "template_count": template_count,
            "robot_count": robot_count,
            "current_month_messages": current_month_messages
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class DashboardChartView(APIView):
    """仪表盘图表数据视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        time_range = request.query_params.get('time_range', 'week')
        
        if time_range == 'week':
            # 获取本周数据
            chart_data = self._get_week_data(request.user)
        else:
            # 获取本月数据
            chart_data = self._get_month_data(request.user)
        
        # 获取机器人类型占比
        robot_type_stats = self._get_robot_type_stats(request.user)
        
        response_data = {
            "trend_data": chart_data,
            "robot_type_stats": robot_type_stats
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_week_data(self, user):
        """获取本周数据"""
        today = timezone.now()
        # 计算本周的起始日期（周一）
        start_of_week = today - datetime.timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 准备7天数据存储结构
        days = []
        success_data = [0] * 7
        fail_data = [0] * 7
        
        # 生成周一到周日的日期
        for i in range(7):
            day = start_of_week + datetime.timedelta(days=i)
            days.append(day.strftime('%m-%d'))
            
            # 查询当天成功消息数
            success_count = MessageLog.objects.filter(
                created_by=user,
                created_at__date=day.date(),
                status=True
            ).count()
            success_data[i] = success_count
            
            # 查询当天失败消息数
            fail_count = MessageLog.objects.filter(
                created_by=user,
                created_at__date=day.date(),
                status=False
            ).count()
            fail_data[i] = fail_count
        
        return {
            "categories": days,
            "series": [
                {"name": "成功", "data": success_data},
                {"name": "失败", "data": fail_data}
            ]
        }
    
    def _get_month_data(self, user):
        """获取本月数据"""
        today = timezone.now()
        # 获取本月第一天
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # 获取本月天数
        _, last_day = calendar.monthrange(today.year, today.month)
        
        # 准备每天数据存储结构
        days = []
        success_data = [0] * last_day
        fail_data = [0] * last_day
        
        # 生成每一天的日期
        for i in range(last_day):
            day = first_day + datetime.timedelta(days=i)
            days.append(day.strftime('%d'))
            
            # 查询当天成功消息数
            success_count = MessageLog.objects.filter(
                created_by=user,
                created_at__date=day.date(),
                status=True
            ).count()
            success_data[i] = success_count
            
            # 查询当天失败消息数
            fail_count = MessageLog.objects.filter(
                created_by=user,
                created_at__date=day.date(),
                status=False
            ).count()
            fail_data[i] = fail_count
        
        return {
            "categories": days,
            "series": [
                {"name": "成功", "data": success_data},
                {"name": "失败", "data": fail_data}
            ]
        }
    
    def _get_robot_type_stats(self, user):
        """获取机器人类型占比"""
        robot_stats = Robot.objects.filter(created_by=user).values('robot_type').annotate(count=Count('id'))
        
        # 构建响应数据
        result = []
        robot_type_map = {
            RobotType.WECHAT: '企业微信',
            RobotType.FEISHU: '飞书',
            RobotType.DINGTALK: '钉钉',
        }
        
        for stat in robot_stats:
            robot_type = stat['robot_type']
            result.append({
                "name": robot_type_map.get(robot_type, robot_type),
                "value": stat['count']
            })
        
        return result


class DashboardRecentLogsView(APIView):
    """仪表盘最近消息记录视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 获取最近5条消息记录
        recent_logs = MessageLog.objects.filter(
            created_by=request.user
        ).order_by('-created_at')[:5]
        
        # 序列化数据
        serializer = MessageLogSerializer(recent_logs, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

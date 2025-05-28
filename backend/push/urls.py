from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .dashboard import DashboardStatsView, DashboardChartView, DashboardRecentLogsView

router = DefaultRouter()
router.register(r'templates', views.TemplateViewSet)
router.register(r'robots', views.RobotViewSet)
router.register(r'logs', views.MessageLogViewSet)
router.register(r'distribution/rules', views.DistributionRuleViewSet)
router.register(r'distribution/instances', views.InstanceMappingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('push/', views.MessagePushView.as_view(), name='message-push'),
    path('public/push/<int:template_id>/<int:robot_id>/', views.PublicMessagePushView.as_view(), name='public-message-push'),
    path('public/push/<int:template_id>/', views.PublicMessagePushByNameView.as_view(), name='public-message-push-by-name'),
    path('public/distribution/push/<int:template_id>/', views.DistributionPushView.as_view(), name='distribution-push'),
    path('templates/<int:template_id>/send/', views.TemplateDirectPushView.as_view(), name='template-direct-push'),
    path('templates/<int:template_id>/info/', views.TemplateInfoView.as_view(), name='template-info'),
    
    # 仪表盘相关接口
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/charts/', DashboardChartView.as_view(), name='dashboard-charts'),
    path('dashboard/recent-logs/', DashboardRecentLogsView.as_view(), name='dashboard-recent-logs'),
    
    # 分发相关接口
    path('distribution/alert/', views.DistributionAlertView.as_view(), name='distribution-alert'),
    path('distribution/refresh-instances/', views.RefreshInstancesView.as_view(), name='refresh-instances'),
]

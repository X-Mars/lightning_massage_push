from django.contrib import admin
from .models import Template, Robot, MessageLog, DistributionRule, InstanceMapping, AlertRecord


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'robot_type', 'created_by', 'created_at', 'updated_at')
    list_filter = ('robot_type', 'created_at')
    search_fields = ('name', 'description', 'content')


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('name', 'robot_type', 'is_default', 'created_by', 'created_at', 'updated_at')
    list_filter = ('robot_type', 'is_default', 'created_at')
    search_fields = ('name', 'description', 'webhook_url')


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('template', 'robot', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'raw_data', 'error_message')


@admin.register(DistributionRule)
class DistributionRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'extract_path', 'extract_pattern')
    ordering = ('-created_at',)


@admin.register(InstanceMapping)
class InstanceMappingAdmin(admin.ModelAdmin):
    list_display = ('instance_name', 'robot_count', 'alert_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('instance_name',)
    filter_horizontal = ('robots',)  # 添加多对多字段的水平过滤器
    
    def robot_count(self, obj):
        return obj.robot_count
    robot_count.short_description = '机器人数量'


@admin.register(AlertRecord)
class AlertRecordAdmin(admin.ModelAdmin):
    list_display = ('instance_mapping', 'rule_name', 'processed', 'alert_time')
    list_filter = ('processed', 'alert_time')
    search_fields = ('instance_mapping__instance_name', 'alert_content')
    readonly_fields = ('alert_time',)

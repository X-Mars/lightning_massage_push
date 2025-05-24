from django.contrib import admin
from .models import Template, Robot, MessageLog


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'robot_type', 'created_by', 'created_at', 'updated_at')
    list_filter = ('robot_type', 'created_at')
    search_fields = ('name', 'description', 'content')


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('name', 'robot_type', 'created_by', 'created_at', 'updated_at')
    list_filter = ('robot_type', 'created_at')
    search_fields = ('name', 'description', 'webhook_url')


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('template', 'robot', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'raw_data', 'error_message')

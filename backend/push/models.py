from django.db import models
from django.contrib.auth.models import User
import uuid


class RobotType(models.TextChoices):
    """机器人类型"""
    WECHAT = 'wechat', '企业微信'
    FEISHU = 'feishu', '飞书'
    DINGTALK = 'dingtalk', '钉钉'


class Template(models.Model):
    """消息模板"""
    name = models.CharField(max_length=100, verbose_name="模板名称")
    description = models.TextField(blank=True, null=True, verbose_name="模板描述")
    content = models.TextField(verbose_name="模板内容")
    robot_type = models.CharField(
        max_length=20, 
        choices=RobotType.choices, 
        verbose_name="适用机器人类型"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates', verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "消息模板"
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Robot(models.Model):
    """机器人配置"""
    name = models.CharField(max_length=100, verbose_name="机器人名称")
    webhook_url = models.URLField(max_length=500, verbose_name="Webhook地址")
    robot_type = models.CharField(
        max_length=20, 
        choices=RobotType.choices, 
        verbose_name="机器人类型"
    )
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robots', verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "机器人配置"
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class MessageLog(models.Model):
    """消息发送日志"""
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, related_name='message_logs', verbose_name="使用模板")
    robot = models.ForeignKey(Robot, on_delete=models.SET_NULL, null=True, related_name='message_logs', verbose_name="发送机器人")
    content = models.TextField(verbose_name="发送内容")
    raw_data = models.TextField(blank=True, null=True, verbose_name="原始数据")
    formatted_content = models.TextField(blank=True, null=True, verbose_name="格式化后内容")
    status = models.BooleanField(default=False, verbose_name="发送状态")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='message_logs', verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "消息日志"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template} - {self.created_at}"

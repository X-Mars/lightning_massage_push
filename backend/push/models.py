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
    english_name = models.CharField(max_length=100, verbose_name="英文名称", blank=True, null=True, unique=True)
    webhook_url = models.URLField(max_length=500, verbose_name="Webhook地址")
    robot_type = models.CharField(
        max_length=20, 
        choices=RobotType.choices, 
        verbose_name="机器人类型"
    )
    is_default = models.BooleanField(default=False, verbose_name="是否为默认机器人")
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


class DistributionRule(models.Model):
    """分发规则"""
    RULE_TYPE_CHOICES = [
        ('json', 'JSON模式'),
        ('string', '字符串模式'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="规则名称")
    type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, verbose_name="匹配类型")
    description = models.TextField(blank=True, verbose_name="规则描述")
    extract_path = models.CharField(max_length=500, blank=True, verbose_name="JSON提取路径")
    extract_pattern = models.CharField(max_length=500, blank=True, verbose_name="字符串提取模式")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "分发规则"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class InstanceMapping(models.Model):
    """实例映射"""
    instance_name = models.CharField(max_length=255, unique=True, verbose_name="实例名称")
    distribution_channels = models.ManyToManyField('DistributionChannel', blank=True, related_name='instance_mappings', verbose_name="配置分发通道")
    source_rule = models.ForeignKey(DistributionRule, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='instance_mappings', verbose_name="来源规则")
    alert_count = models.IntegerField(default=0, verbose_name="告警次数")
    last_alert_time = models.DateTimeField(null=True, blank=True, verbose_name="最后告警时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "实例映射"
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.instance_name
    
    @property
    def channel_names(self):
        """获取关联的分发通道名称列表"""
        return list(self.distribution_channels.values_list('name', flat=True))
    
    @property
    def channel_count(self):
        """获取关联的分发通道数量"""
        return self.distribution_channels.count()
    
    @property
    def robot_names(self):
        """获取关联的机器人名称列表（保持向后兼容）"""
        return list(self.distribution_channels.values_list('robot__name', flat=True))
    
    @property
    def robot_count(self):
        """获取关联的机器人数量（保持向后兼容）"""
        return self.distribution_channels.count()


class AlertRecord(models.Model):
    """告警记录"""
    instance_mapping = models.ForeignKey(InstanceMapping, on_delete=models.CASCADE, 
                                       related_name='alert_records', verbose_name="关联实例")
    rule_name = models.CharField(max_length=100, verbose_name="规则名称")
    alert_content = models.TextField(verbose_name="告警内容")
    raw_data = models.TextField(verbose_name="原始数据")
    extracted_values = models.JSONField(default=list, verbose_name="提取的值")
    alert_time = models.DateTimeField(auto_now_add=True, verbose_name="告警时间")
    processed = models.BooleanField(default=False, verbose_name="是否已处理")
    
    class Meta:
        verbose_name = "告警记录"
        verbose_name_plural = verbose_name
        ordering = ['-alert_time']
    
    def __str__(self):
        return f"{self.instance_mapping.instance_name} - {self.alert_time}"


class DistributionChannel(models.Model):
    """分发通道 - 一对一绑定机器人和消息模板"""
    name = models.CharField(max_length=100, verbose_name="通道名称")
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='distribution_channels', verbose_name="绑定机器人")
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='distribution_channels', verbose_name="绑定模板")
    description = models.TextField(blank=True, verbose_name="通道描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='distribution_channels', verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "分发通道"
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']
        # 确保同一个机器人和模板只能绑定一次
        unique_together = ['robot', 'template']
    
    def __str__(self):
        return f"{self.name} ({self.robot.name} -> {self.template.name})"

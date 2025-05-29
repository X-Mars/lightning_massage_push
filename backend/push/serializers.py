from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Template, Robot, MessageLog, DistributionRule, InstanceMapping, AlertRecord, DistributionRule, InstanceMapping, AlertRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TemplateSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None
    
    class Meta:
        model = Template
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class RobotSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None
    
    class Meta:
        model = Robot
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MessageLogSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    robot_name = serializers.CharField(source='robot.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    
    class Meta:
        model = MessageLog
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'status', 'error_message', 'formatted_content', 'template_name', 'robot_name', 'created_by_username']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MessagePushSerializer(serializers.Serializer):
    """消息推送序列化器"""
    content = serializers.JSONField(help_text="消息内容，JSON格式")
    template_id = serializers.IntegerField(help_text="模板ID", required=False, allow_null=True)
    robot_id = serializers.IntegerField(help_text="机器人ID")
    test_mode = serializers.BooleanField(help_text="测试模式", required=False, default=False)
    direct_content = serializers.CharField(help_text="直接发送的内容", required=False, allow_blank=True)

    def validate(self, data):
        # 获取机器人
        try:
            robot = Robot.objects.get(id=data['robot_id'])
            data['robot'] = robot
        except Robot.DoesNotExist:
            raise serializers.ValidationError({"robot_id": "机器人不存在"})
        
        # 测试模式下，模板可以为空
        if data.get('test_mode', False):
            data['template'] = None
            return data
            
        # 非测试模式下，需要验证模板
        if 'template_id' not in data or not data['template_id']:
            raise serializers.ValidationError({"template_id": "需要提供模板ID"})
            
        try:
            template = Template.objects.get(id=data['template_id'])
            data['template'] = template
        except Template.DoesNotExist:
            raise serializers.ValidationError({"template_id": "模板不存在"})
        
        # 验证模板与机器人类型匹配
        if template.robot_type != robot.robot_type:
            raise serializers.ValidationError("模板与机器人类型不匹配")
        
        return data


class DistributionRuleSerializer(serializers.ModelSerializer):
    """分发规则序列化器"""
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    
    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None
    
    class Meta:
        model = DistributionRule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """验证规则配置"""
        rule_type = data.get('type')
        if rule_type == 'json':
            if not data.get('extract_path'):
                raise serializers.ValidationError({'extract_path': 'JSON模式下必须指定提取路径'})
        elif rule_type == 'string':
            if not data.get('extract_pattern'):
                raise serializers.ValidationError({'extract_pattern': '字符串模式下必须指定提取模式'})
        return data


class InstanceMappingSerializer(serializers.ModelSerializer):
    """实例映射序列化器"""
    robot_name = serializers.CharField(source='robot.name', read_only=True)
    source_rule_name = serializers.CharField(source='source_rule.name', read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    last_alert_time = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    
    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None
    
    def get_last_alert_time(self, obj):
        return obj.last_alert_time.strftime('%Y-%m-%d %H:%M:%S') if obj.last_alert_time else None
    
    class Meta:
        model = InstanceMapping
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'alert_count', 'last_alert_time']


class AlertRecordSerializer(serializers.ModelSerializer):
    """告警记录序列化器"""
    instance_name = serializers.CharField(source='instance_mapping.instance_name', read_only=True)
    alert_time = serializers.SerializerMethodField()

    def get_alert_time(self, obj):
        return obj.alert_time.strftime('%Y-%m-%d %H:%M:%S') if obj.alert_time else None
    
    class Meta:
        model = AlertRecord
        fields = '__all__'
        read_only_fields = ['alert_time']


class RuleTestSerializer(serializers.Serializer):
    """规则测试序列化器"""
    type = serializers.ChoiceField(choices=['json', 'string'])
    extract_path = serializers.CharField(required=False, allow_blank=True)
    extract_pattern = serializers.CharField(required=False, allow_blank=True)
    test_data = serializers.CharField()

    def validate(self, data):
        rule_type = data.get('type')
        if rule_type == 'json':
            if not data.get('extract_path'):
                raise serializers.ValidationError({'extract_path': 'JSON模式下必须指定提取路径'})
        elif rule_type == 'string':
            if not data.get('extract_pattern'):
                raise serializers.ValidationError({'extract_pattern': '字符串模式下必须指定提取模式'})
        return data

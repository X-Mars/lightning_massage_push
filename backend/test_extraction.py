#!/usr/bin/env python3
import sys
import os
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messagepush.settings')
django.setup()

from push.services import DistributionService
import json

# 测试数据
test_data = {
    'receiver': 'webhook',
    'status': 'firing',
    'alerts': [
        {
            'status': 'resolved',
            'labels': {
                'alertname': '虚机分区使用率超过 90%',
                'cluster': '地铁中兴测试',
                'department': '信息管理部',
                'environment': '测试',
                'group': 'zte',
                'id': '5ecbd4ec-bf5f-433c-8a2f-85ff0282ca08',
                'instance': '172.27.173.18:80',
                'ip': '172.27.174.19',
                'job': 'zte-exporter',
                'name': '虚机磁盘分区平均使用率',
                'partition': '/',
                'physical_server': 'host-172-27-32-68',
                'project_custom': '青岛地铁官网',
                'prometheus': 'monitoring/k8s',
                'severity': 'critical',
                'vim': 'QD-Metro-DC1',
                'vm': 'Dtgw-Web3-test'
            }
        }
    ]
}

# 测试提取不同字段
test_paths = [
    'alerts[].labels.instance',
    'alerts[].labels.project_custom',
    'alerts[].labels.cluster',
    'alerts[].labels.vm'
]

print('测试JSON字段提取:')
for path in test_paths:
    result = DistributionService.extract_json_values(test_data, path)
    print(f'Path: {path} -> Result: {result}')

print('\n测试字符串形式的JSON数据:')
json_string = json.dumps(test_data)
for path in test_paths:
    result = DistributionService.extract_json_values(json_string, path)
    print(f'Path: {path} -> Result: {result}')

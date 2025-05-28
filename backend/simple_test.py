import json

# 测试数据
test_data = {
    "receiver": "webhook",
    "status": "firing", 
    "alerts": [
        {
            "status": "resolved",
            "labels": {
                "instance": "172.27.173.18:80",
                "project_custom": "青岛地铁官网",
                "cluster": "地铁中兴测试",
                "vm": "Dtgw-Web3-test"
            }
        }
    ]
}

def extract_json_values(data, path):
    try:
        if isinstance(data, str):
            json_data = json.loads(data)
        else:
            json_data = data
        
        results = set()
        
        if "alerts[].labels." in path:
            field_name = path.split("alerts[].labels.")[-1]
            if "alerts" in json_data and isinstance(json_data["alerts"], list):
                for alert in json_data["alerts"]:
                    if "labels" in alert and field_name in alert["labels"]:
                        results.add(alert["labels"][field_name])
        
        return list(results)
    except Exception as e:
        print(f"Error: {e}")
        return []

# 测试
paths = ["alerts[].labels.instance", "alerts[].labels.project_custom", "alerts[].labels.cluster"]
for path in paths:
    result = extract_json_values(test_data, path)
    print(f"{path} -> {result}")

import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Загрузка конфигурации из YAML файла"""
    default_config = {
        'telegram': {
            'bot_token': os.getenv('BOT_TOKEN', ''),
            'admin_ids': [1085771559],
            'webhook_url': os.getenv('WEBHOOK_URL', '')
        },
        'redis': {
            'enabled': os.getenv('REDIS_ENABLED', 'false').lower() == 'true',
            'url': os.getenv('REDIS_URL', 'redis://localhost:6379')
        },
        'logging': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file_enabled': os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
        },
        'metrics': {
            'enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
        }
    }
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            file_config = yaml.safe_load(f) or {}
            # Рекурсивное обновление конфигурации
            def update_dict(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = update_dict(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            update_dict(default_config, file_config)
    
    return default_config

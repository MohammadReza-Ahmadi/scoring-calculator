# FastApi config
fastapi_url = '127.0.0.1'
fastapi_port = 8016
service_message_code = '009'

# MongoDB config
mongodb_host = '127.0.0.1'
mongodb_port = 27017
mongodb_user = 'admin'
mongodb_pass = 'admin'
mongodb_auth_source = 'admin'
mongodb_name = 'scoring-engine'
mongodb_alias = 'scoring-engine'

# Redis config
redis_host = '127.0.0.1'
redis_port = 6379
redis_pass = ''
redis_reset = False

# Import rules data config
import_rules_flag = True

# Scoring Config
min_score = 0
max_score = 1000
distribution_count = 30
initial_score_change_store_config = False

# max long value in java: 9223372036854775807

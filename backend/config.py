from pathlib import Path
import os
import secrets
import warnings

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR}/media_player.db"

# SECRET_KEY 安全配置：优先从环境变量读取
_secret_key = os.getenv("SECRET_KEY")
if _secret_key:
    SECRET_KEY = _secret_key
else:
    # 开发环境：生成随机密钥并发出警告
    SECRET_KEY = secrets.token_urlsafe(32)
    warnings.warn(
        "SECRET_KEY 环境变量未设置！已生成随机密钥用于开发环境。"
        "生产环境请设置 SECRET_KEY 环境变量。",
        RuntimeWarning
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

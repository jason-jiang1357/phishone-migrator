import asyncio
import logging
import os

import aiohttp

from load_template import LoadEmailTemplate
from utils import get_project_config, get_token

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])

def init_env(config: dict,token: str):
    """初始化环境"""
    return config | {"token":token}

async def main():
    """备份导出 数据脚本入口"""
    logging.warning("【恢复导入】 数据,执行中...")
    async with aiohttp.ClientSession() as session:
        # 解析配置
        config: dict = get_project_config()
        logging.info(config)

        # 登录
        token: str = await get_token(session,config)
        logging.info(token)

        # 初始化环境
        config = init_env(config,token)

        logger.warning("1.导入模版... ")
        load_template = LoadEmailTemplate(session,config)
        await load_template.load()
        logger.warning("1.导入模版... 完成")
        
asyncio.run(main())





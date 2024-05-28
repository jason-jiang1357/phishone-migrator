import asyncio
import logging
import os

import aiohttp

from backup_template import BackupEmailTemplate
from utils import backup_data_dir, get_project_config, get_token

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])


def init_env(config: dict,token: str):
    """初始化环境"""
    # 模版资源 封面图片
    images_dir = f"{backup_data_dir}/template_images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # 模版资源 附件
    files_dir = f"{backup_data_dir}/template_files"
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    return config | {"token":token}

async def main():
    """备份导出 数据脚本入口"""
    logger.warning("【备份导出】 数据,执行中... ")
    async with aiohttp.ClientSession() as session:
        # 解析配置
        config: dict = get_project_config()
        logger.info(config)

        # 登录
        token: str = await get_token(session,config)
        logger.info(token)

        # 初始化环境
        config = init_env(config,token)

        logger.warning("1.备份模版... ")
        backup = BackupEmailTemplate(session,config)
        await backup.backup()
        
asyncio.run(main())
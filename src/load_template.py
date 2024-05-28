import json
import logging
import os

import aiohttp

from utils import Base


class LoadTemplate(Base):
    
    async def load(self):
        with open("backup_data/backup_template.json","r") as f:
            self.templates: list[dict] = json.load(f)
        
        for template in self.tempaltes:
            # 1. 上传封面图片，修改cover字段
            cover_url = await self.upload_cover_image(template["cover"])
            template["cover"] = cover_url

            # 2. 给本地json文件增加:
            # attachment: {"id":xxx } 字段

            # 3. 上传template
            await self.upload_email_template(template)

        
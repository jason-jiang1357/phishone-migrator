import json
import logging
import os

from utils import Load, backup_data_dir

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])


class LoadEmailTemplate(Load):
    async def handle_load_template(self,templates):

        for template in templates:
            # 1. 上传封面图片，修改cover字段
            cover_url = await self.upload_image(template["cover"])
            template["cover"] = cover_url

            # 2. 给本地json文件增加:
            del template["attachment"]
            # attachment: {"id":xxx } 字段

            # 3. 上传template
            await self.upload_email_template(template)
        
    async def load(self):
        template_file = os.path.join(backup_data_dir,"template.json")
        with open(template_file,"r") as f:
            templates: list[dict] = json.load(f)
        logger.info(f"导入template.json数据成功,共{len(templates)}条数据")

        # 处理导入 本地temlate数据
        await self.handle_load_template(templates)

        

        
import json
import logging
import os

from utils import (Load, UploadAttachmentError, UploadImageError,
                   backup_data_dir)

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])


class LoadEmailTemplate(Load):
    async def handle_load_template(self, templates):

        for template in templates:
            try:
                # 1. 上传封面图片，修改cover字段
                cover_url = await self.upload_image(template["cover"])
                # 修改模版数据为上传后的封面信息
                template["cover"] = cover_url

                # 2. 上传附件
                if attachment := template.pop("attachment",None):
                    att_info = await self.upload_attachment(attachment["name"])
                    # 修改模版数据为上传后的附件信息
                    template["attachment"] = att_info
            except UploadImageError as e:
                logger.error(f"上传图片失败:{e}")
                continue
            except UploadAttachmentError as e:
                logger.error(f"上传附件失败:{e}")
                continue

            # 3. 上传template
            await self.upload_email_template(template)

    async def load(self):
        template_file = os.path.join(backup_data_dir, "template.json")
        with open(template_file, "r") as f:
            templates: list[dict] = json.load(f)
        logger.info(f"导入template.json数据成功,共{len(templates)}条数据")

        # 处理导入 本地temlate数据
        await self.handle_load_template(templates)

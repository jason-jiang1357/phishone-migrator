import json
import logging
import os

from utils import Backup, backup_data_dir

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])


class BackupEmailTemplate(Backup):
    """备份所有公共邮件模版"""

    async def get_email_template_detail(self, template_id: int):
        url = self.home_url + f"/api/templates/{template_id}/"
        response: dict = await self.send_get_request(url)
        return response

    def save_template_content(self, template_content: list[dict]):
        with open(f"{backup_data_dir}/template.json", "w") as f:
            json.dump(template_content, f, indent=4, ensure_ascii=False)

    async def handle_template_content(self, current_res: list[dict]):
        """处理当前页中，公共模版的数据"""
        current_page_template_res = []

        # 循环遍历公司模版
        for pub_template in [tem for tem in current_res if not tem["company"]]:
            template_id = pub_template["id"]

            # 获取模版详情
            pub_response = await self.get_email_template_detail(template_id)

            # 删除不需要的字段
            pub_response.pop("id")
            pub_response.pop("created_time")

            # 下载图片
            cover_url = pub_response["cover"]
            if cover_url:
                filename = await self.download_image(cover_url, "template_images")
                pub_response["cover"] = filename

            # 下载附件
            # attachment = pub_template["attachment"]
            """ 无法下载附件
            "attachment": {
            "id": 174,
            "name": "关于软件正版化说明文档.docx"
                },
            """
            current_page_template_res.append(pub_response)

        # 一次性写入当前页的模版数据
        self.save_template_content(current_page_template_res)

    async def backup(self):
        email_template_url = (
            self.home_url + "/api/templates/?page=1&pagesize=50&ttype=1"
        )
        while email_template_url:
            logger.info(f"当前页:{email_template_url}")
            current_res, is_next_page = await self.parse_response(email_template_url)

            # 处理模版详情
            await self.handle_template_content(current_res)

            # 获取下一页的url.
            # fix http -> https
            email_template_url = (
                is_next_page.replace("http", "https") if is_next_page else None
            )

        logger.warning("1.备份模版...完成")

import json
import logging
import os
import sys
import tomllib

import aiohttp
from aiohttp import ClientSession

# 数据备份的根目录
backup_data_dir = "/backup_data"


def get_project_config() -> dict:
    """获取项目配置"""
    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        logging.error("配置文件`config.toml`不存在")
        sys.exit(1)
    return config


# [settings配置相关]
# 设置debug模式为INFO级别
if get_project_config()["debug"]:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def get_token(session, config: dict) -> str:
    """使用`手机号`+`密码`登录,获取token"""
    url = config["home_url"] + "/api/token/obtain-by-password/"

    async with session.post(url, data=config["login_data"]) as resp:
        if resp.status != 200:
            logger.error(f"登录失败: {url} {await resp.text()}")
            sys.exit(1)
        response: dict = await resp.json()
        token = response["access"]
        return "Bearer " + token


class Base:
    def __init__(self, session: ClientSession, config: dict) -> None:
        self.session = session
        self.home_url = config["home_url"]
        self.headers = {"Authorization": config["token"]}


class Backup(Base):
    """备份数据基础类"""

    async def send_get_request(self, url: str) -> dict:
        """发送get请求,获取预期的响应数据"""
        async with self.session.get(url, headers=self.headers) as resp:

            if resp.status != 200:
                logger.error(f"get请求失败: {url} {self.headers} {await resp.text()}")
                sys.exit(1)
            response: dict = await resp.json()
            return response

    async def parse_response(self, url) -> tuple[list[dict], str]:
        """获取当前页的数据,返回当前页数据和下一页的url"""
        response: dict = await self.send_get_request(url)
        current_page_data: list[dict] = response["results"]
        is_next_page = response["next"]
        return current_page_data, is_next_page

    async def download_image(self, url: str, image_dir: str):
        """将指定url的图片下载到本地指定路径,返回文件路径"""
        async with self.session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"下载图片失败 {url} {await resp.text()}")
                return

            file_path_name = f"{backup_data_dir}/{image_dir}/{url.split('/')[-1]}"
            with open(file_path_name, "wb") as f:
                f.write(await resp.read())
            logger.info(f"下载图片成功 {file_path_name}")
            return file_path_name


class UploadAttachmentError(Exception):
    ...


class UploadImageError(Exception):
    ...


class Load(Base):
    """导入数据基础类"""

    async def send_post_request(
        self, url: str, data: dict, extend_headers: None | dict = None
    ) -> dict:
        """发送post请求"""

        headers = self.headers | extend_headers if extend_headers else self.headers

        async with self.session.post(url, data=data, headers=headers) as resp:
            if resp.status != 201:
                logger.error(f"post请求失败 {self.home_url} {await resp.text()}")
                return
            response: dict = await resp.json()
            return response

    async def upload_image(self, full_image_name: str) -> str:
        """上传图片,返回图片url"""
        url = self.home_url + "/api/images"
        image_name = os.path.basename(full_image_name)

        # 上传图片
        with open(full_image_name, "rb") as image_file:
            form = aiohttp.FormData()
            form.add_field(
                "upload", image_file, filename=image_name, content_type="image/png"
            )
            res = await self.send_post_request(url, data=form)
        try:
            image_url = res["url"]
        except Exception:
            raise UploadImageError(f"上传图片失败 {res}")
        logger.info(f"上传图片成功, {image_url}")
        return image_url

    async def upload_attachment(self, attachment_name: str) -> dict:
        """上传附件,返回附件的基本信息,id和name"""
        url = self.home_url + "/api/attachments"

        attachment_full_name = os.path.join(backup_data_dir,"template_files",attachment_name)

        # 上传附件
        with open(attachment_full_name, "rb") as attachment_file:
            form = aiohttp.FormData()
            form.add_field(
                "file",
                attachment_file,
                filename=attachment_name,
            )
            res = await self.send_post_request(url, data=form)
        try:
            logger.info(f"上传附件成功, {res['name']}")
        except Exception:
            raise UploadAttachmentError(f"上传附件失败 {res}")
        return res

    async def upload_email_template(self, template: dict):
        """上传邮件模板"""
        url = self.home_url + "/api/templates/"

        # 测试
        # import random
        # template["name"] = template["name"] + str(random.randint(1, 1000000))

        # 使用json.dump是为了将None转换为null
        if res := await self.send_post_request(
            url,
            data=json.dumps(template),
            extend_headers={"Content-Type": "application/json"},
        ):
            logger.info(f"上传邮件模板成功 {res['name']}")
        else:
            logger.error(f"上传邮件模板失败 {res}")

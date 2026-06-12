"""
Tempail.com 临时邮箱 API 客户端

这个模块提供了与 Tempail.com 临时邮箱服务交互的 Python 接口。

作者: API逆向工程
日期: 2026-05-19
版本: 1.0.0
"""

import requests
import time
import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime
import json


class TempailClient:
    """Tempail.com 临时邮箱客户端"""

    def __init__(self, language: str = "ru", base_url: str = "https://tempail.com"):
        """
        初始化客户端

        Args:
            language: 语言代码 (ru, en, etc.)
            base_url: 基础URL
        """
        self.base_url = base_url
        self.language = language
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": base_url,
                "Referer": f"{base_url}/{language}/",
            }
        )

        # 会话信息
        self.oturum: Optional[str] = None
        self.phpsessid: Optional[str] = None
        self.tarih: Optional[int] = None
        self.email_address: Optional[str] = None

        # API端点
        self.api_kontrol = f"{base_url}/{language}/api/kontrol/"
        self.api_oku = f"{base_url}/{language}/api/oku/"
        self.api_sil = f"{base_url}/{language}/api/sil/"
        self.api_yoket = f"{base_url}/{language}/api/yoket/"
        self.api_sifre = f"{base_url}/{language}/api/sifre/"
        self.api_iletisim = f"{base_url}/{language}/api/iletisim/"
        self.url_inbox = f"{base_url}/{language}/"

    def initialize(self) -> Dict[str, str]:
        """
        初始化会话并获取临时邮箱地址

        Returns:
            包含邮箱地址和会话信息的字典

        Raises:
            Exception: 初始化失败时抛出
        """
        try:
            response = self.session.get(self.url_inbox)
            response.raise_for_status()

            # 从Cookie获取会话信息
            self.oturum = self.session.cookies.get("oturum")
            self.phpsessid = self.session.cookies.get("PHPSESSID")

            if not self.oturum or not self.phpsessid:
                raise Exception("无法获取会话Cookie")

            # 从页面提取邮箱地址
            soup = BeautifulSoup(response.text, "html.parser")
            email_input = soup.find("input", {"id": "eposta_adres"})

            if email_input and email_input.get("value"):
                self.email_address = email_input["value"]
            else:
                # 尝试从其他位置提取
                email_elem = soup.find("input", {"readonly": True})
                if email_elem:
                    self.email_address = email_elem.get("value")

            if not self.email_address:
                raise Exception("无法从页面提取邮箱地址")

            # 提取时间戳
            script_content = response.text
            tarih_match = re.search(r'tarih\s*=\s*["\']?(\d+)["\']?', script_content)
            if tarih_match:
                self.tarih = int(tarih_match.group(1))
            else:
                self.tarih = int(time.time())

            return {
                "email": self.email_address,
                "oturum": self.oturum,
                "phpsessid": self.phpsessid,
                "tarih": str(self.tarih),
            }

        except Exception as e:
            raise Exception(f"初始化失败: {str(e)}")

    def check_inbox(self) -> List[Dict[str, str]]:
        """
        检查收件箱中的邮件

        Returns:
            邮件列表，每个邮件包含id, from, subject, time等字段

        Raises:
            Exception: 检查失败时抛出
        """
        if not self.oturum:
            raise Exception("会话未初始化，请先调用 initialize()")

        try:
            data = {
                "oturum": self.oturum,
                "tarih": str(self.tarih or int(time.time())),
                "geri_don": self.url_inbox,
            }

            response = self.session.post(
                self.api_kontrol,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )

            # 304表示没有新邮件
            if response.status_code == 304:
                return []

            response.raise_for_status()

            # 解析HTML响应
            soup = BeautifulSoup(response.text, "html.parser")
            emails = []

            # 查找邮件列表项
            mail_items = soup.find_all("li", class_=lambda x: x and "mail" in x.lower())

            for item in mail_items:
                mail_id = item.get("id", "")
                if mail_id.startswith("mail_"):
                    mail_index = mail_id.replace("mail_", "")

                    # 提取邮件信息
                    from_elem = item.find(
                        class_=lambda x: x and "gonderen" in x.lower()
                    )
                    subject_elem = item.find(
                        class_=lambda x: x and "baslik" in x.lower()
                    )
                    time_elem = item.find(class_=lambda x: x and "tarih" in x.lower())

                    email_data = {
                        "id": mail_index,
                        "from": from_elem.get_text(strip=True) if from_elem else "",
                        "subject": (
                            subject_elem.get_text(strip=True) if subject_elem else ""
                        ),
                        "time": time_elem.get_text(strip=True) if time_elem else "",
                        "raw_html": str(item),
                    }

                    emails.append(email_data)

            return emails

        except Exception as e:
            raise Exception(f"检查收件箱失败: {str(e)}")

    def read_email(self, mail_id: str, mail_index: str) -> Dict[str, str]:
        """
        读取指定邮件的内容

        Args:
            mail_id: 邮件ID
            mail_index: 邮件索引

        Returns:
            包含邮件详细信息的字典

        Raises:
            Exception: 读取失败时抛出
        """
        if not self.oturum:
            raise Exception("会话未初始化，请先调用 initialize()")

        try:
            data = {"oturum": self.oturum, "veri[0]": mail_id, "veri[1]": mail_index}

            response = self.session.post(
                self.api_oku,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )
            response.raise_for_status()

            # 解析HTML响应
            soup = BeautifulSoup(response.text, "html.parser")

            # 提取邮件头信息
            from_elem = soup.find(class_=lambda x: x and "from" in x.lower())
            subject_elem = soup.find(class_=lambda x: x and "subject" in x.lower())
            date_elem = soup.find(class_=lambda x: x and "date" in x.lower())

            # 提取邮件正文
            body_elem = soup.find(class_=lambda x: x and "body" in x.lower())

            email_content = {
                "from": from_elem.get_text(strip=True) if from_elem else "",
                "subject": subject_elem.get_text(strip=True) if subject_elem else "",
                "date": date_elem.get_text(strip=True) if date_elem else "",
                "body_html": str(body_elem) if body_elem else response.text,
                "body_text": (
                    body_elem.get_text(strip=True)
                    if body_elem
                    else soup.get_text(strip=True)
                ),
                "raw_html": response.text,
            }

            return email_content

        except Exception as e:
            raise Exception(f"读取邮件失败: {str(e)}")

    def delete_email(self, mail_id: str, mail_index: str) -> bool:
        """
        删除指定邮件

        Args:
            mail_id: 邮件ID
            mail_index: 邮件索引

        Returns:
            删除是否成功

        Raises:
            Exception: 删除失败时抛出
        """
        if not self.oturum:
            raise Exception("会话未初始化，请先调用 initialize()")

        try:
            data = {"oturum": self.oturum, "veri[0]": mail_id, "veri[1]": mail_index}

            response = self.session.post(
                self.api_sil,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )
            response.raise_for_status()

            return True

        except Exception as e:
            raise Exception(f"删除邮件失败: {str(e)}")

    def destroy_mailbox(self) -> bool:
        """
        永久销毁当前邮箱

        Returns:
            销毁是否成功

        Raises:
            Exception: 销毁失败时抛出
        """
        if not self.oturum:
            raise Exception("会话未初始化，请先调用 initialize()")

        try:
            data = {"oturum": self.oturum}

            response = self.session.post(
                self.api_yoket,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )
            response.raise_for_status()

            # 尝试解析JSON响应
            try:
                result = response.json()
                if result.get("hata") == "yok":
                    # 清除会话信息
                    self.oturum = None
                    self.phpsessid = None
                    self.email_address = None
                    return True
                return False
            except:
                # 如果不是JSON，检查状态码
                return response.status_code == 200

        except Exception as e:
            raise Exception(f"销毁邮箱失败: {str(e)}")

    def get_qr_code(self) -> Dict[str, str]:
        """
        获取邮箱地址的QR码

        Returns:
            包含QR码URL和邮箱URL的字典

        Raises:
            Exception: 获取失败时抛出
        """
        if not self.oturum:
            raise Exception("会话未初始化，请先调用 initialize()")

        try:
            data = {"oturum": self.oturum}

            response = self.session.post(
                self.api_sifre,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )
            response.raise_for_status()

            result = response.json()
            return {
                "qr_code_url": result.get("url_kare_kod", ""),
                "email_url": result.get("url", ""),
            }

        except Exception as e:
            raise Exception(f"获取QR码失败: {str(e)}")

    def wait_for_email(
        self, timeout: int = 300, interval: int = 10
    ) -> Optional[Dict[str, str]]:
        """
        等待新邮件到达

        Args:
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）

        Returns:
            第一封新邮件的信息，超时返回None
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            emails = self.check_inbox()
            if emails:
                return emails[0]
            time.sleep(interval)

        return None

    def monitor_inbox(
        self, callback, interval: int = 10, max_iterations: Optional[int] = None
    ):
        """
        持续监控收件箱

        Args:
            callback: 收到新邮件时的回调函数，接收邮件列表作为参数
            interval: 检查间隔（秒）
            max_iterations: 最大迭代次数，None表示无限循环
        """
        iteration = 0

        while max_iterations is None or iteration < max_iterations:
            try:
                emails = self.check_inbox()
                if emails:
                    callback(emails)

                time.sleep(interval)
                iteration += 1

            except KeyboardInterrupt:
                print("\n监控已停止")
                break
            except Exception as e:
                print(f"监控出错: {str(e)}")
                time.sleep(interval)

    def get_session_info(self) -> Dict[str, Optional[str]]:
        """
        获取当前会话信息

        Returns:
            包含会话详细信息的字典
        """
        return {
            "email": self.email_address,
            "oturum": self.oturum,
            "phpsessid": self.phpsessid,
            "tarih": str(self.tarih) if self.tarih else None,
            "language": self.language,
            "base_url": self.base_url,
        }


def main():
    """示例用法"""
    print("=== Tempail.com 临时邮箱客户端 ===\n")

    # 创建客户端
    client = TempailClient(language="ru")

    try:
        # 初始化并获取邮箱地址
        print("正在初始化...")
        info = client.initialize()
        print(f"✓ 邮箱地址: {info['email']}")
        print(f"✓ 会话ID: {info['oturum']}")
        print(f"✓ PHP会话: {info['phpsessid'][:20]}...")
        print()

        # 检查收件箱
        print("检查收件箱...")
        emails = client.check_inbox()

        if emails:
            print(f"✓ 找到 {len(emails)} 封邮件:\n")
            for i, email in enumerate(emails, 1):
                print(f"{i}. 发件人: {email['from']}")
                print(f"   主题: {email['subject']}")
                print(f"   时间: {email['time']}")
                print()

            # 读取第一封邮件
            if emails:
                print("读取第一封邮件...")
                first_email = emails[0]
                content = client.read_email(first_email["id"], first_email["id"])
                print(f"✓ 邮件内容:")
                print(f"   发件人: {content['from']}")
                print(f"   主题: {content['subject']}")
                print(f"   日期: {content['date']}")
                print(f"   正文预览: {content['body_text'][:200]}...")
                print()
        else:
            print("✓ 收件箱为空")
            print()

        # 获取QR码
        print("获取QR码...")
        qr_info = client.get_qr_code()
        print(f"✓ QR码URL: {qr_info['qr_code_url']}")
        print(f"✓ 邮箱URL: {qr_info['email_url']}")
        print()

        # 等待新邮件（可选）
        print("等待新邮件（30秒超时）...")
        new_email = client.wait_for_email(timeout=30, interval=5)
        if new_email:
            print(f"✓ 收到新邮件: {new_email['subject']}")
        else:
            print("✓ 超时，未收到新邮件")
        print()

        # 显示会话信息
        print("会话信息:")
        session_info = client.get_session_info()
        for key, value in session_info.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"✗ 错误: {str(e)}")

    finally:
        # 可选：销毁邮箱
        # print("\n销毁邮箱...")
        # if client.destroy_mailbox():
        #     print("✓ 邮箱已销毁")
        pass


if __name__ == "__main__":
    main()

# Made with Bob

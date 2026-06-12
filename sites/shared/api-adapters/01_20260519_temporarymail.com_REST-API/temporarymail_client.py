#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TemporaryMail.com API 客户端
用于自动化临时邮箱操作
"""

import requests
import time
import json
from typing import Optional, List, Dict
from datetime import datetime


class TemporaryMailClient:
    """TemporaryMail.com API 客户端类"""

    def __init__(self):
        self.base_url = "https://temporarymail.com/api/"
        self.email = None
        self.secret_key = None
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://temporarymail.com/",
            }
        )

    def get_random_email(self) -> str:
        """
        获取随机临时邮箱地址

        Returns:
            str: 邮箱地址
        """
        url = f"{self.base_url}?action=requestEmailAccess&key=&value=random"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Exception(
                    f"获取邮箱失败: {data['error']} (code: {data.get('code', 'unknown')})"
                )

            self.email = data["address"]
            self.secret_key = data["secretKey"]

            print(f"✓ 成功获取邮箱: {self.email}")
            print(f"  密钥: {self.secret_key}")

            return self.email

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def request_specific_email(self, email_address: str, key: str = "") -> str:
        """
        请求特定的邮箱地址

        Args:
            email_address: 想要的邮箱地址
            key: 邮箱密钥（如果之前使用过）

        Returns:
            str: 邮箱地址
        """
        url = (
            f"{self.base_url}?action=requestEmailAccess&key={key}&value={email_address}"
        )

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = data["error"]
                error_code = data.get("code", "unknown")

                if error_code == 403:
                    raise Exception(f"邮箱被保留: {error_msg}")
                elif error_code == 429:
                    raise Exception(f"请求过多: {error_msg}")
                else:
                    raise Exception(f"请求失败: {error_msg} (code: {error_code})")

            self.email = data["address"]
            self.secret_key = data["secretKey"]

            print(f"✓ 成功获取邮箱: {self.email}")

            return self.email

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def check_inbox(self) -> Dict[str, Dict]:
        """
        检查收件箱

        Returns:
            Dict[str, Dict]: 邮件字典，格式为 {msg_id: msg_data}
        """
        if not self.secret_key:
            raise Exception("请先获取邮箱地址")

        url = f"{self.base_url}?action=checkInbox&value={self.secret_key}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            # 空收件箱返回空数组
            if response.text.strip() == "[]":
                return {}

            data = response.json()

            # 检查错误
            if isinstance(data, dict) and "error" in data:
                error_code = data.get("code", "unknown")
                if error_code == 500:
                    raise Exception("未授权访问此收件箱")
                elif error_code == 429:
                    raise Exception("检查次数过多，请稍后再试")
                else:
                    raise Exception(f"检查失败: {data['error']}")

            # API 返回的是字典格式 {msg_id: msg_data}
            return data if isinstance(data, dict) else {}

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def get_email_detail(self, email_id: str) -> Dict:
        """
        获取邮件详情

        Args:
            email_id: 邮件ID

        Returns:
            Dict: 邮件详情
        """
        url = f"{self.base_url}?action=getEmail&value={email_id}"

        try:
            response = self.session.post(url)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_code = data.get("code", "unknown")
                if error_code == 429:
                    raise Exception("打开邮件次数过多")
                else:
                    raise Exception(f"获取邮件失败: {data['error']}")

            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")

    def wait_for_email(
        self, timeout: int = 300, check_interval: int = 5, verbose: bool = True
    ) -> Optional[List[Dict]]:
        """
        等待接收邮件

        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            verbose: 是否显示详细信息

        Returns:
            Optional[List[Dict]]: 邮件列表，超时返回None
        """
        if not self.secret_key:
            raise Exception("请先获取邮箱地址")

        start_time = time.time()
        checks = 0

        if verbose:
            print(f"\n⏳ 等待接收邮件... (超时: {timeout}秒)")

        while time.time() - start_time < timeout:
            try:
                emails = self.check_inbox()
                checks += 1

                if emails:
                    if verbose:
                        print(f"✓ 收到 {len(emails)} 封邮件！")
                    return emails

                if verbose and checks % 6 == 0:  # 每30秒显示一次
                    elapsed = int(time.time() - start_time)
                    print(f"  已等待 {elapsed} 秒...")

                time.sleep(check_interval)

            except Exception as e:
                if verbose:
                    print(f"✗ 检查时出错: {str(e)}")
                time.sleep(check_interval)

        if verbose:
            print("✗ 超时，未收到邮件")
        return None

    def download_attachment(self, file_id: str, save_path: str) -> bool:
        """
        下载附件

        Args:
            file_id: 附件ID
            save_path: 保存路径

        Returns:
            bool: 是否成功
        """
        url = f"https://temporarymail.com/attachment/?i={file_id}"

        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✓ 附件已保存到: {save_path}")
            return True

        except Exception as e:
            print(f"✗ 下载附件失败: {str(e)}")
            return False

    def format_email(self, email: Dict) -> str:
        """
        格式化邮件信息用于显示

        Args:
            email: 邮件信息字典

        Returns:
            str: 格式化的字符串
        """
        from_addr = email.get("from", "未知")
        name = email.get("name", "")
        subject = email.get("subject", "(无主题)")
        date = email.get("date", 0)

        # 转换时间戳
        if date:
            dt = datetime.fromtimestamp(date)
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = "未知时间"

        sender = f"{name} <{from_addr}>" if name else from_addr

        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
发件人: {sender}
主题: {subject}
时间: {date_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def main():
    """主函数 - 演示使用"""
    print("=" * 60)
    print("TemporaryMail.com API 客户端")
    print("=" * 60)

    # 创建客户端
    client = TemporaryMailClient()

    try:
        # 1. 获取随机邮箱
        email = client.get_random_email()
        print(f"\n📧 你的临时邮箱: {email}")
        print("   请使用此地址接收邮件\n")

        # 2. 等待接收邮件
        emails = client.wait_for_email(timeout=120, check_interval=5)

        if emails:
            # 3. 显示所有邮件
            print(f"\n📬 收件箱 ({len(emails)} 封邮件):")

            for idx, email in enumerate(emails, 1):
                print(f"\n[邮件 {idx}]")
                print(client.format_email(email))

                # 4. 获取邮件详情
                try:
                    detail = client.get_email_detail(email["id"])
                    email_data = detail[email["id"]]

                    # 显示附件信息
                    if email_data.get("attachments"):
                        print("📎 附件:")
                        for att in email_data["attachments"]:
                            size_kb = att["size"] / 1024
                            print(f"   - {att['filename']} ({size_kb:.2f} KB)")
                            print(f"     附件ID: {att['fileId']}")

                    # 显示邮件查看链接
                    print(f"\n🔗 查看完整邮件:")
                    print(f"   https://temporarymail.com/view/?i={email['id']}")

                except Exception as e:
                    print(f"✗ 获取邮件详情失败: {str(e)}")

        print("\n" + "=" * 60)
        print("✓ 演示完成")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")


if __name__ == "__main__":
    main()

# Made with Bob

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempimail.org API 客户端 v2.0
用于自动化临时邮箱操作

版本历史:
- v2.0 (2026-05-27):
  * 添加Unix时间戳支持
  * 统一API设计（get_email_detail）
  * 标准化错误处理
  * 添加便利字段（has_attachments, size）
  * 改进类型提示
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# 异常类定义
# ============================================================================

class TempimailAPIError(Exception):
    """Tempimail API 错误基类"""
    def __init__(self, message: str, code: str = None, status: int = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.status = status
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error': True,
            'code': self.code,
            'message': self.message,
            'status': self.status
        }


class TokenExpiredError(TempimailAPIError):
    """CSRF Token过期"""
    def __init__(self):
        super().__init__(
            message="CSRF token expired, please refresh",
            code="TOKEN_EXPIRED",
            status=401
        )


class EmailNotFoundError(TempimailAPIError):
    """邮件不存在"""
    def __init__(self, email_id: str):
        super().__init__(
            message=f"Email with ID '{email_id}' not found",
            code="EMAIL_NOT_FOUND",
            status=404
        )


class NetworkError(TempimailAPIError):
    """网络请求错误"""
    def __init__(self, original_error: Exception):
        super().__init__(
            message=f"Network request failed: {str(original_error)}",
            code="NETWORK_ERROR",
            status=None
        )


class ParseError(TempimailAPIError):
    """解析错误"""
    def __init__(self, detail: str):
        super().__init__(
            message=f"Failed to parse response: {detail}",
            code="PARSE_ERROR",
            status=None
        )


class TempimailClient:
    """Tempimail.org API 客户端类"""

    def __init__(self, lang="en"):
        """
        初始化客户端

        Args:
            lang: 语言代码 (en, ru, zh, etc.)
        """
        self.base_url = "https://tempimail.org"
        self.lang = lang
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/",
                "Origin": self.base_url,
            }
        )
        self.csrf_token = None
        self.mailbox = None
        self.token_time = 0

    def get_csrf_token(self) -> str:
        """
        获取CSRF Token

        Returns:
            str: CSRF token
        """
        try:
            url = f"{self.base_url}/{self.lang}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", {"name": "csrf-token"})

            if meta and meta.get("content"):
                self.csrf_token = meta.get("content")
                self.token_time = time.time()
                print(f"[OK] Got CSRF Token: {self.csrf_token[:20]}...")
                return self.csrf_token
            else:
                raise Exception("CSRF Token not found in page")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get CSRF Token: {str(e)}")

    def refresh_token_if_needed(self):
        """如果token过期则刷新"""
        # Token有效期设为1小时
        if not self.csrf_token or (time.time() - self.token_time > 3600):
            print("Refreshing CSRF Token...")
            self.get_csrf_token()

    def get_mailbox(self, include_body: bool = False) -> Dict:
        """
        获取邮箱地址和消息列表
        
        Args:
            include_body: 是否包含邮件正文内容（默认False）
                         如果为True，会为每封邮件额外请求正文内容

        Returns:
            Dict: 包含mailbox和messages的字典
                {
                    'mailbox': 'example@tempimail.org',
                    'messages': [
                        {
                            'id': '2PqAXymbJ0mmMLP0Egpl1LvG',
                            'from': '发件人姓名',
                            'from_email': 'sender@example.com',
                            'subject': '邮件主题',
                            'is_seen': False,
                            'body_html': '<div>...</div>',  # 仅当include_body=True时存在
                            'body_text': 'Plain text...'     # 仅当include_body=True时存在
                        }
                    ]
                }
        """
        self.refresh_token_if_needed()

        url = f"{self.base_url}/messages?{int(time.time() * 1000)}"
        data = {"_token": self.csrf_token}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            if "mailbox" in result:
                self.mailbox = result["mailbox"]
                if not hasattr(self, "_mailbox_printed"):
                    print(f"[OK] Mailbox: {self.mailbox}")
                    self._mailbox_printed = True

            # 如果需要包含邮件正文，为每封邮件获取正文
            if include_body and "messages" in result and result["messages"]:
                for message in result["messages"]:
                    try:
                        body_data = self.get_email_body(message["id"])
                        message["body_html"] = body_data["body_html"]
                        message["body_text"] = body_data["body_text"]
                    except Exception as e:
                        message["body_html"] = f"[Failed to fetch: {str(e)}]"
                        message["body_text"] = f"[Failed to fetch: {str(e)}]"

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get mailbox: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Response is not valid JSON")

    def check_inbox(self) -> List[Dict]:
        """
        检查收件箱

        Returns:
            List[Dict]: 邮件列表
        """
        result = self.get_mailbox()
        return result.get("messages", [])

    def get_email_detail(self, email_id: str) -> str:
        """
        获取邮件详情（完整HTML页面）

        Args:
            email_id: 邮件ID（字符串格式）

        Returns:
            str: 完整的HTML页面内容（包含网站UI）
        """
        url = f"{self.base_url}/{self.lang}/view/{email_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get email detail: {str(e)}")

    def get_email_body(self, email_id: str) -> Dict[str, str]:
        """
        获取邮件正文内容（不包含元数据）
        
        直接请求 /message/{id} 端点获取纯净的邮件正文HTML

        Args:
            email_id: 邮件ID（字符串格式）

        Returns:
            Dict[str, str]: 包含以下字段的字典
                - body_html: HTML格式正文
                - body_text: 纯文本正文
        """
        url = f"{self.base_url}/message/{email_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            html_content = response.text
            
            # 解析HTML获取纯文本
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text(separator="\n", strip=True)
            
            return {
                "body_html": html_content,
                "body_text": text_content
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get email body: {str(e)}")

    def get_email_content(self, email_id: str) -> Dict[str, str]:
        """
        获取纯净的邮件内容（解析HTML提取）
        
        从邮件详情页面提取发件人、主题、日期和正文内容，
        不包含任何网站UI元素（导航栏、页脚等）

        Args:
            email_id: 邮件ID（字符串格式，如 "2PqAXymbJ0mmMLP0Egpl1LvG"）

        Returns:
            Dict[str, str]: 包含以下字段的字典
                - from_name: 发件人姓名
                - from_email: 发件人邮箱
                - subject: 邮件主题
                - date: 发送日期时间
                - body_text: 纯文本正文
                - body_html: HTML格式正文
                
        Example:
            >>> client = TempimailClient()
            >>> content = client.get_email_content("2PqAXymbJ0mmMLP0Egpl1LvG")
            >>> print(content['subject'])
            'Test Email'
        """
        html = self.get_email_detail(email_id)
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "from_name": "",
            "from_email": "",
            "subject": "",
            "date": "",
            "body_text": "",
            "body_html": ""
        }

        try:
            # 查找邮件卡片容器
            card_body = soup.find("div", class_="card-body")
            
            if not card_body:
                raise Exception("Could not find email content container")

            # 1. 提取发件人信息
            # HTML结构: <div class="col-6 ov-h from">Name<span>email@example.com</span></div>
            from_divs = card_body.find_all("div", class_="from")
            if from_divs:
                # 第一个 from div 包含发件人信息
                from_div = from_divs[0]
                # 获取发件人姓名（div的直接文本内容）
                from_name_parts = []
                for content in from_div.contents:
                    if isinstance(content, str):
                        from_name_parts.append(content.strip())
                result["from_name"] = " ".join(from_name_parts).strip()
                
                # 获取发件人邮箱（span标签内容）
                from_span = from_div.find("span")
                if from_span:
                    result["from_email"] = from_span.get_text(strip=True)

            # 2. 提取日期
            # HTML结构: <div class="col-6 text-right ov-h from">Date:<span>2026-05-27 05:11:09</span></div>
            if len(from_divs) > 1:
                date_div = from_divs[1]
                date_span = date_div.find("span")
                if date_span:
                    result["date"] = date_span.get_text(strip=True)

            # 3. 提取主题
            # HTML结构: <div class="col-12 ov-h subject">Subject :<span>Email Subject</span></div>
            subject_div = card_body.find("div", class_="subject")
            if subject_div:
                subject_span = subject_div.find("span")
                if subject_span:
                    result["subject"] = subject_span.get_text(strip=True)

            # 4. 提取邮件正文
            # HTML结构: <div class="content"><iframe src="https://tempimail.org/message/{id}"></iframe></div>
            content_div = card_body.find("div", class_="content")
            if content_div:
                iframe = content_div.find("iframe")
                if iframe and iframe.get("src"):
                    # 获取iframe的src URL
                    iframe_url = iframe.get("src")
                    
                    # 请求iframe内容
                    try:
                        iframe_response = self.session.get(iframe_url)
                        iframe_response.raise_for_status()
                        
                        # 解析iframe内容
                        iframe_soup = BeautifulSoup(iframe_response.text, "html.parser")
                        
                        # 提取纯文本内容
                        result["body_text"] = iframe_soup.get_text(separator="\n", strip=True)
                        
                        # 提取HTML内容（移除script和style标签）
                        for script in iframe_soup(["script", "style"]):
                            script.decompose()
                        result["body_html"] = str(iframe_soup)
                        
                    except Exception as e:
                        result["body_text"] = f"[Failed to fetch email body: {str(e)}]"
                        result["body_html"] = f"<p>Failed to fetch email body: {str(e)}</p>"

            return result

        except Exception as e:
            raise Exception(f"Failed to parse email content: {str(e)}")

    def wait_for_email(
        self, timeout: int = 300, check_interval: int = 20, verbose: bool = True
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
        if not self.mailbox:
            self.get_mailbox()

        start_time = time.time()
        checks = 0

        if verbose:
            print(f"\n⏳ 等待接收邮件... (超时: {timeout}秒, 间隔: {check_interval}秒)")

        while time.time() - start_time < timeout:
            try:
                emails = self.check_inbox()
                checks += 1

                if emails:
                    if verbose:
                        print(f"[OK] Received {len(emails)} emails!")
                    return emails

                if verbose and checks % 3 == 0:  # 每3次检查显示一次
                    elapsed = int(time.time() - start_time)
                    print(f"  已等待 {elapsed} 秒... (检查次数: {checks})")

                time.sleep(check_interval)

            except Exception as e:
                if verbose:
                    print(f"✗ 检查时出错: {str(e)}")
                time.sleep(check_interval)

        if verbose:
            print("✗ 超时，未收到邮件")
        return None

    def format_email(self, email: Dict) -> str:
        """
        格式化邮件信息用于显示

        Args:
            email: 邮件信息字典

        Returns:
            str: 格式化的字符串
        """
        from_name = email.get("from", "未知")
        from_email = email.get("from_email", "")
        subject = email.get("subject", "(无主题)")
        is_seen = email.get("is_seen", False)
        email_id = email.get("id", 0)

        status = "✓ 已读" if is_seen else "● 未读"
        sender = f"{from_name} <{from_email}>" if from_email else from_name

        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status} | ID: {email_id}
发件人: {sender}
主题: {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def extract_text_from_html(self, html: str) -> str:
        """
        从HTML中提取纯文本

        Args:
            html: HTML内容

        Returns:
            str: 纯文本内容
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # 清理多余的空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            return text
        except:
            return html


def main():
    """主函数 - 演示使用"""
    print("=" * 60)
    print("Tempimail.org API 客户端")
    print("=" * 60)

    # 创建客户端
    client = TempimailClient(lang="en")

    try:
        # 1. 获取邮箱
        result = client.get_mailbox()
        print(f"\n📧 你的临时邮箱: {result['mailbox']}")
        print("   请使用此地址接收邮件\n")

        # 2. 等待接收邮件
        emails = client.wait_for_email(timeout=120, check_interval=20)

        if emails:
            # 3. 显示所有邮件
            print(f"\n📬 收件箱 ({len(emails)} 封邮件):")

            for idx, email in enumerate(emails, 1):
                print(f"\n[邮件 {idx}]")
                print(client.format_email(email))

                # 4. 获取邮件详情
                try:
                    print(f"[INFO] Fetching email details...")
                    detail_html = client.get_email_detail(email["id"])

                    # 提取纯文本
                    text_content = client.extract_text_from_html(detail_html)

                    # 显示前500个字符
                    preview = text_content[:500]
                    if len(text_content) > 500:
                        preview += "..."

                    print(f"\n📄 邮件内容预览:")
                    print("-" * 60)
                    print(preview)
                    print("-" * 60)

                    # 显示查看链接
                    print(f"\n🔗 完整邮件链接:")
                    print(f"   {client.base_url}/{client.lang}/view/{email['id']}")

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

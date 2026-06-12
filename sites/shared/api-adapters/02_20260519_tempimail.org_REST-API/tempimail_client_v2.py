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
  * 客户端过滤功能
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
    def __init__(self, message: str, code: Optional[str] = None, status: Optional[int] = None):
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


# ============================================================================
# 主客户端类
# ============================================================================

class TempimailClient:
    """Tempimail.org API 客户端类 v2.0"""

    def __init__(self, lang: str = "en"):
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
        self.csrf_token: Optional[str] = None
        self.mailbox: Optional[str] = None
        self.token_time: float = 0

    def get_csrf_token(self) -> str:
        """
        获取CSRF Token

        Returns:
            str: CSRF token
            
        Raises:
            NetworkError: 网络请求失败
            ParseError: 无法解析Token
        """
        try:
            url = f"{self.base_url}/{self.lang}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", {"name": "csrf-token"})

            if meta and hasattr(meta, 'get'):
                token = meta.get("content")
                if token:
                    self.csrf_token = str(token)
                    self.token_time = time.time()
                    print(f"[OK] Got CSRF Token: {self.csrf_token[:20]}...")
                    return self.csrf_token
            
            raise ParseError("CSRF Token not found in page")

        except requests.exceptions.RequestException as e:
            raise NetworkError(e)

    def refresh_token_if_needed(self) -> None:
        """如果token过期则刷新（有效期1小时）"""
        if not self.csrf_token or (time.time() - self.token_time > 3600):
            print("Refreshing CSRF Token...")
            self.get_csrf_token()

    def _add_timestamp(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        为邮件添加Unix时间戳
        
        Args:
            message: 邮件字典
            
        Returns:
            增强后的邮件字典
        """
        if 'receivedAt' in message:
            try:
                # 解析日期字符串: "2026-05-27 08:12:35"
                dt = datetime.strptime(message['receivedAt'], '%Y-%m-%d %H:%M:%S')
                message['timestamp'] = int(dt.timestamp())
            except (ValueError, TypeError):
                pass
        return message

    def _enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强邮件对象，添加便利字段
        
        Args:
            message: 原始邮件字典
            
        Returns:
            增强后的邮件字典
        """
        # 添加时间戳
        self._add_timestamp(message)
        
        # 添加附件标志
        attachments = message.get('attachments', [])
        message['has_attachments'] = len(attachments) > 0
        
        # 添加大小（基于content长度）
        content = message.get('content', '')
        message['size'] = len(content)
        
        return message

    def get_mailbox(self, include_body: bool = False) -> Dict[str, Any]:
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
                            'receivedAt': '2026-05-27 08:12:35',
                            'timestamp': 1779862355,  # v2.0新增
                            'has_attachments': False,  # v2.0新增
                            'size': 1234,              # v2.0新增
                            'attachments': [],
                            'content': '<div>...</div>',
                            'body_html': '<div>...</div>',  # 仅当include_body=True
                            'body_text': 'Plain text...'     # 仅当include_body=True
                        }
                    ]
                }
                
        Raises:
            NetworkError: 网络请求失败
            ParseError: 响应解析失败
            TokenExpiredError: Token过期
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

            # 增强所有邮件对象
            if "messages" in result and result["messages"]:
                for message in result["messages"]:
                    self._enhance_message(message)
                    
                    # 如果需要包含邮件正文
                    if include_body:
                        try:
                            body_data = self.get_email_body(message["id"])
                            message["body_html"] = body_data["body_html"]
                            message["body_text"] = body_data["body_text"]
                        except Exception as e:
                            message["body_html"] = f"[Failed to fetch: {str(e)}]"
                            message["body_text"] = f"[Failed to fetch: {str(e)}]"

            return result

        except requests.exceptions.RequestException as e:
            raise NetworkError(e)
        except json.JSONDecodeError:
            raise ParseError("Response is not valid JSON")

    def check_inbox(self) -> List[Dict[str, Any]]:
        """
        检查收件箱

        Returns:
            List[Dict]: 邮件列表
        """
        result = self.get_mailbox()
        return result.get("messages", [])

    def get_email_body(self, email_id: str) -> Dict[str, str]:
        """
        获取邮件正文内容（不包含元数据）
        
        直接请求 /message/{id} 端点获取纯净的邮件正文HTML
        
        注意：此方法已被 get_email_detail(include_metadata=False) 替代，
        但保留用于向后兼容。

        Args:
            email_id: 邮件ID（字符串格式）

        Returns:
            Dict[str, str]: 包含以下字段的字典
                - body_html: HTML格式正文
                - body_text: 纯文本正文
                
        Raises:
            NetworkError: 网络请求失败
            EmailNotFoundError: 邮件不存在
        """
        url = f"{self.base_url}/message/{email_id}"

        try:
            response = self.session.get(url)
            
            if response.status_code == 404:
                raise EmailNotFoundError(email_id)
                
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
            raise NetworkError(e)

    def get_email_detail(self, email_id: str, include_metadata: bool = True) -> Dict[str, Any]:
        """
        统一的邮件详情获取接口（v2.0新增）
        
        这是获取邮件详情的推荐方法，替代了旧的 get_email_body() 和 get_email_content()
        
        Args:
            email_id: 邮件ID（字符串格式）
            include_metadata: 是否包含元数据（发件人、主题、日期等）
                            - True: 返回完整信息（从 /view/{id} 获取）
                            - False: 只返回正文（从 /message/{id} 获取）
        
        Returns:
            Dict: 邮件详情
                当 include_metadata=True 时:
                {
                    'from_name': '发件人姓名',
                    'from_email': 'sender@example.com',
                    'subject': '邮件主题',
                    'date': '2026-05-27 08:12:35',
                    'timestamp': 1779862355,
                    'body_html': '<div>...</div>',
                    'body_text': 'Plain text...'
                }
                
                当 include_metadata=False 时:
                {
                    'body_html': '<div>...</div>',
                    'body_text': 'Plain text...'
                }
                
        Raises:
            NetworkError: 网络请求失败
            EmailNotFoundError: 邮件不存在
            ParseError: 解析失败
        """
        if not include_metadata:
            # 只获取正文
            return self.get_email_body(email_id)
        
        # 获取完整信息
        url = f"{self.base_url}/{self.lang}/view/{email_id}"

        try:
            response = self.session.get(url)
            
            if response.status_code == 404:
                raise EmailNotFoundError(email_id)
                
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            result: Dict[str, Any] = {
                "from_name": "",
                "from_email": "",
                "subject": "",
                "date": "",
                "timestamp": 0,
                "body_text": "",
                "body_html": ""
            }

            # 查找邮件卡片容器
            card_body = soup.find("div", class_="card-body")
            
            if not card_body:
                raise ParseError("Could not find email content container")

            # 1. 提取发件人信息
            from_divs = card_body.find_all("div", class_="from")
            if from_divs:
                from_div = from_divs[0]
                # 获取发件人姓名
                from_name_parts = []
                for content in from_div.contents:
                    if isinstance(content, str):
                        from_name_parts.append(content.strip())
                result["from_name"] = " ".join(from_name_parts).strip()
                
                # 获取发件人邮箱
                from_span = from_div.find("span")
                if from_span:
                    result["from_email"] = from_span.get_text(strip=True)

            # 2. 提取日期
            if len(from_divs) > 1:
                date_div = from_divs[1]
                date_span = date_div.find("span")
                if date_span:
                    date_str = date_span.get_text(strip=True)
                    result["date"] = date_str
                    
                    # 添加时间戳
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        result["timestamp"] = int(dt.timestamp())
                    except (ValueError, TypeError):
                        pass

            # 3. 提取主题
            subject_div = card_body.find("div", class_="subject")
            if subject_div:
                subject_span = subject_div.find("span")
                if subject_span:
                    result["subject"] = subject_span.get_text(strip=True)

            # 4. 提取邮件正文
            content_div = card_body.find("div", class_="content")
            if content_div:
                iframe = content_div.find("iframe")
                if iframe and hasattr(iframe, 'get'):
                    iframe_url = iframe.get("src")
                    if iframe_url:
                        try:
                            iframe_response = self.session.get(str(iframe_url))
                            iframe_response.raise_for_status()
                            
                            iframe_soup = BeautifulSoup(iframe_response.text, "html.parser")
                            
                            # 提取纯文本
                            result["body_text"] = iframe_soup.get_text(separator="\n", strip=True)
                            
                            # 提取HTML
                            for script in iframe_soup(["script", "style"]):
                                script.decompose()
                            result["body_html"] = str(iframe_soup)
                            
                        except Exception as e:
                            result["body_text"] = f"[Failed to fetch: {str(e)}]"
                            result["body_html"] = f"<p>Failed to fetch: {str(e)}</p>"

            return result

        except requests.exceptions.RequestException as e:
            raise NetworkError(e)

    # ========================================================================
    # 向后兼容的方法（已弃用）
    # ========================================================================

    def get_email_content(self, email_id: str) -> Dict[str, str]:
        """
        已弃用：请使用 get_email_detail(email_id, include_metadata=True)
        
        获取纯净的邮件内容（解析HTML提取）
        """
        return self.get_email_detail(email_id, include_metadata=True)

    # ========================================================================
    # 客户端过滤功能（v2.0新增）
    # ========================================================================

    def filter_messages(self, 
                       messages: List[Dict[str, Any]],
                       from_email: Optional[str] = None,
                       subject_contains: Optional[str] = None,
                       after_timestamp: Optional[int] = None,
                       has_attachments: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        在客户端过滤邮件列表（v2.0新增）
        
        Args:
            messages: 邮件列表
            from_email: 按发件人邮箱过滤
            subject_contains: 主题包含关键词（不区分大小写）
            after_timestamp: 在指定时间戳之后
            has_attachments: 是否有附件
        
        Returns:
            过滤后的邮件列表
            
        Example:
            >>> client = TempimailClient()
            >>> result = client.get_mailbox()
            >>> # 过滤来自特定发件人的邮件
            >>> filtered = client.filter_messages(
            ...     result['messages'],
            ...     from_email='test@example.com'
            ... )
        """
        filtered = messages
        
        if from_email:
            filtered = [m for m in filtered if m.get('from_email') == from_email]
        
        if subject_contains:
            keyword = subject_contains.lower()
            filtered = [m for m in filtered 
                       if keyword in m.get('subject', '').lower()]
        
        if after_timestamp is not None:
            filtered = [m for m in filtered 
                       if m.get('timestamp', 0) > after_timestamp]
        
        if has_attachments is not None:
            filtered = [m for m in filtered 
                       if m.get('has_attachments', False) == has_attachments]
        
        return filtered

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def wait_for_email(
        self, timeout: int = 300, check_interval: int = 20, verbose: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
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

                if verbose and checks % 3 == 0:
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

    def format_email(self, email: Dict[str, Any]) -> str:
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
        email_id = email.get("id", "")
        
        # v2.0新增字段
        timestamp = email.get("timestamp", 0)
        has_attachments = email.get("has_attachments", False)
        size = email.get("size", 0)

        status = "✓ 已读" if is_seen else "● 未读"
        sender = f"{from_name} <{from_email}>" if from_email else from_name
        
        # 格式化时间
        time_str = ""
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            time_str = f"\n时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 附件和大小信息
        extra_info = []
        if has_attachments:
            extra_info.append("📎 有附件")
        if size > 0:
            extra_info.append(f"大小: {size} bytes")
        
        extra_str = " | ".join(extra_info)
        if extra_str:
            extra_str = f"\n{extra_str}"

        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status} | ID: {email_id}
发件人: {sender}
主题: {subject}{time_str}{extra_str}
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
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            return text
        except:
            return html


def main():
    """主函数 - 演示v2.0新功能"""
    print("=" * 60)
    print("Tempimail.org API 客户端 v2.0")
    print("=" * 60)

    client = TempimailClient(lang="en")

    try:
        # 1. 获取邮箱
        result = client.get_mailbox()
        print(f"\n📧 你的临时邮箱: {result['mailbox']}")
        print("   请使用此地址接收邮件\n")

        # 2. 等待接收邮件
        emails = client.wait_for_email(timeout=120, check_interval=20)

        if emails:
            print(f"\n📬 收件箱 ({len(emails)} 封邮件):")

            for idx, email in enumerate(emails, 1):
                print(f"\n[邮件 {idx}]")
                print(client.format_email(email))

                # 演示v2.0新功能
                print(f"[v2.0] Unix时间戳: {email.get('timestamp', 'N/A')}")
                print(f"[v2.0] 有附件: {email.get('has_attachments', False)}")
                print(f"[v2.0] 大小: {email.get('size', 0)} bytes")

                # 使用新的统一API获取详情
                try:
                    print(f"\n[INFO] 使用 get_email_detail() 获取完整信息...")
                    detail = client.get_email_detail(email["id"], include_metadata=True)
                    
                    print(f"\n📄 邮件详情:")
                    print(f"  发件人: {detail['from_name']} <{detail['from_email']}>")
                    print(f"  主题: {detail['subject']}")
                    print(f"  日期: {detail['date']}")
                    print(f"  时间戳: {detail['timestamp']}")
                    
                    preview = detail['body_text'][:200]
                    if len(detail['body_text']) > 200:
                        preview += "..."
                    print(f"\n  正文预览:\n  {preview}")

                except Exception as e:
                    print(f"✗ 获取详情失败: {str(e)}")

            # 演示过滤功能
            print(f"\n[v2.0] 演示过滤功能:")
            filtered = client.filter_messages(
                emails,
                subject_contains="test"
            )
            print(f"  包含'test'的邮件: {len(filtered)} 封")

        print("\n" + "=" * 60)
        print("✓ 演示完成")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except TempimailAPIError as e:
        print(f"\n✗ API错误: {e.to_dict()}")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")


if __name__ == "__main__":
    main()

# Made with Bob - v2.0 (2026-05-27)
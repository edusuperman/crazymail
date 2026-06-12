#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TemporaryMail.com API 客户端 v2.0
增强版本，包含以下改进：
- 统一API设计（智能获取完整详情）
- 标准化错误处理（异常类层次结构）
- 自定义邮箱功能（用户名+域名）
- 增强消息字段（timestamp, datetime, has_attachments）
- 客户端过滤功能
"""

import random
import requests
import time
import json
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime


# ============================================================================
# 异常类层次结构
# ============================================================================

class TemporaryMailAPIError(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(f"{message} (code: {code})" if code else message)


class TemporaryMailAuthError(TemporaryMailAPIError):
    """认证错误（code: 500）"""
    pass


class TemporaryMailRateLimitError(TemporaryMailAPIError):
    """速率限制错误（code: 429）"""
    pass


class TemporaryMailReservedError(TemporaryMailAPIError):
    """邮箱被保留错误（code: 403）"""
    pass


class TemporaryMailNetworkError(TemporaryMailAPIError):
    """网络错误"""
    pass


# ============================================================================
# 客户端类
# ============================================================================

class TemporaryMailClient:
    """TemporaryMail.com API 客户端类 v2.0"""

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

    # ========================================================================
    # 错误处理
    # ========================================================================

    def _handle_error(self, data: Dict) -> None:
        """
        统一错误处理
        
        Args:
            data: API响应数据
        
        Raises:
            TemporaryMailAPIError: 各种API错误
        """
        if "error" not in data:
            return
        
        error_msg = data.get("error", "Unknown error")
        error_code = data.get("code")
        
        if error_code == 500:
            raise TemporaryMailAuthError(error_msg, error_code)
        elif error_code == 429:
            raise TemporaryMailRateLimitError(error_msg, error_code)
        elif error_code == 403:
            raise TemporaryMailReservedError(error_msg, error_code)
        else:
            raise TemporaryMailAPIError(error_msg, error_code)

    # ========================================================================
    # 邮箱创建（增强版）
    # ========================================================================

    def get_random_email(self) -> str:
        """
        获取随机临时邮箱地址
        
        Returns:
            str: 邮箱地址
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        """
        url = f"{self.base_url}?action=requestEmailAccess&key=&value=random"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            self._handle_error(data)

            self.email = data["address"]
            self.secret_key = data["secretKey"]

            print(f"✓ 成功获取邮箱: {self.email}")
            print(f"  密钥: {self.secret_key}")

            return self.email

        except requests.exceptions.RequestException as e:
            raise TemporaryMailNetworkError(f"网络请求失败: {str(e)}")

    def get_available_domains(self) -> List[str]:
        """
        获取可用的邮箱域名列表
        
        Returns:
            List[str]: 域名列表（如 ["AllfreeMail.net", "EasyMailer.live"]）
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        
        Example:
            >>> client = TemporaryMailClient()
            >>> domains = client.get_available_domains()
            >>> print(domains)
            ['AllfreeMail.net', 'AllWebEmails.com', 'EasyMailer.live', ...]
        """
        url = f"{self.base_url}?action=getDomains"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            # API返回格式为列表
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return list(data.keys())
            else:
                return []
        
        except requests.exceptions.RequestException as e:
            raise TemporaryMailNetworkError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise TemporaryMailAPIError(f"获取域名列表失败: {str(e)}")

    def create_custom_email(self, username: str, domain: Optional[str] = None) -> str:
        """
        创建自定义邮箱（用户名+域名）
        
        Args:
            username: 用户名（如 "myname"）
            domain: 域名（如 "@AllfreeMail.net" 或 "AllfreeMail.net"）
                    如果为None，使用随机域名
        
        Returns:
            str: 完整邮箱地址
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        
        Example:
            >>> client = TemporaryMailClient()
            >>> # 指定域名
            >>> email = client.create_custom_email("myname", "@AllfreeMail.net")
            >>> print(email)  # myname@AllfreeMail.net
            >>> 
            >>> # 随机域名
            >>> email = client.create_custom_email("myname")
            >>> print(email)  # myname@RandomDomain.com
        """
        # 标准化域名格式
        if domain:
            domain = domain.lstrip('@')  # 移除开头的@
            email_address = f"{username}@{domain}"
        else:
            # 如果未指定域名，获取可用域名列表并随机选择
            domains = self.get_available_domains()
            if not domains:
                raise TemporaryMailAPIError("无法获取可用域名列表")
            
            domain = random.choice(domains).lstrip('@')
            email_address = f"{username}@{domain}"
        
        # 使用现有的request_specific_email方法
        return self.request_specific_email(email_address)

    def request_specific_email(self,
                              email_address: Optional[str] = None,
                              username: Optional[str] = None,
                              domain: Optional[str] = None,
                              key: str = "") -> str:
        """
        请求特定的邮箱地址（增强版，支持多种参数组合）
        
        Args:
            email_address: 完整邮箱地址（如 "test@example.com"）
            username: 用户名（如 "test"）
            domain: 域名（如 "@example.com" 或 "example.com"）
            key: 邮箱密钥（如果之前使用过）
        
        Returns:
            str: 邮箱地址
        
        Raises:
            ValueError: 参数错误
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        
        Note:
            - 如果提供email_address，直接使用
            - 如果提供username和domain，组合成邮箱地址
            - 如果只提供username，使用随机域名
        
        Example:
            >>> # 方式1：完整邮箱地址
            >>> client.request_specific_email("test@example.com")
            >>> 
            >>> # 方式2：用户名+域名
            >>> client.request_specific_email(username="test", domain="@example.com")
            >>> 
            >>> # 方式3：只提供用户名（随机域名）
            >>> client.request_specific_email(username="test")
        """
        # 参数验证
        if not email_address and not username:
            raise ValueError("必须提供email_address或username")
        
        # 构建邮箱地址
        if email_address:
            # 使用完整邮箱地址
            pass
        elif username and domain:
            # 组合用户名和域名
            domain = domain.lstrip('@')
            email_address = f"{username}@{domain}"
        elif username:
            # 只有用户名，获取随机域名
            domains = self.get_available_domains()
            if not domains:
                raise TemporaryMailAPIError("无法获取可用域名列表")
            
            domain = random.choice(domains).lstrip('@')
            email_address = f"{username}@{domain}"
        
        # API请求
        url = f"{self.base_url}?action=requestEmailAccess&key={key}&value={email_address}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            self._handle_error(data)
            
            self.email = data["address"]
            self.secret_key = data["secretKey"]
            
            print(f"✓ 成功获取邮箱: {self.email}")
            
            return self.email
        
        except requests.exceptions.RequestException as e:
            raise TemporaryMailNetworkError(f"网络请求失败: {str(e)}")

    # ========================================================================
    # 邮件检查（增强版）
    # ========================================================================

    def _enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强消息字段
        
        Args:
            message: 原始消息数据
        
        Returns:
            Dict[str, Any]: 增强后的消息数据
        """
        # 1. 添加timestamp别名（向后兼容）
        message['timestamp'] = message.get('date', 0)
        
        # 2. 添加datetime对象
        if message.get('date'):
            try:
                message['datetime'] = datetime.fromtimestamp(message['date'])
            except (ValueError, OSError):
                message['datetime'] = None
        else:
            message['datetime'] = None
        
        # 3. 添加has_attachments便利字段
        attachments = message.get('attachments', [])
        message['has_attachments'] = len(attachments) > 0
        
        return message

    def _check_inbox_raw(self) -> Dict[str, Dict]:
        """
        检查收件箱（原始API调用）
        
        Returns:
            Dict[str, Dict]: 邮件字典，格式为 {msg_id: msg_data}
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        """
        if not self.secret_key:
            raise TemporaryMailAPIError("请先获取邮箱地址")

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
                self._handle_error(data)

            # API 返回的是字典格式 {msg_id: msg_data}
            return data if isinstance(data, dict) else {}

        except requests.exceptions.RequestException as e:
            raise TemporaryMailNetworkError(f"网络请求失败: {str(e)}")

    def check_inbox(self, fetch_full_details: bool = False, enhance: bool = True) -> Dict[str, Dict]:
        """
        检查收件箱（增强版）
        
        Args:
            fetch_full_details: 是否自动获取完整详情（默认False）
            enhance: 是否增强消息字段（默认True）
        
        Returns:
            Dict[str, Dict]: 邮件字典
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        
        Example:
            >>> # 快速检查（只获取列表）
            >>> messages = client.check_inbox()
            >>> 
            >>> # 获取完整详情
            >>> messages = client.check_inbox(fetch_full_details=True)
        """
        messages = self._check_inbox_raw()
        
        if fetch_full_details and messages:
            # 自动获取所有邮件的完整详情
            for msg_id in list(messages.keys()):
                try:
                    full_detail = self.get_email_detail(msg_id)
                    messages[msg_id] = full_detail[msg_id]
                except Exception as e:
                    print(f"⚠ 获取邮件 {msg_id} 详情失败: {str(e)}")
        
        if enhance:
            # 增强所有消息字段
            for msg_id in messages:
                messages[msg_id] = self._enhance_message(messages[msg_id])
        
        return messages

    def get_messages(self, include_full_details: bool = True, enhance: bool = True) -> Dict[str, Dict]:
        """
        获取邮件列表（统一接口）
        
        Args:
            include_full_details: 是否包含完整详情（默认True）
            enhance: 是否增强消息字段（默认True）
        
        Returns:
            Dict[str, Dict]: 邮件字典
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        
        Example:
            >>> # 推荐用法：获取完整详情
            >>> messages = client.get_messages()
            >>> 
            >>> # 快速检查
            >>> messages = client.get_messages(include_full_details=False)
        """
        return self.check_inbox(fetch_full_details=include_full_details, enhance=enhance)

    def get_email_detail(self, email_id: str) -> Dict:
        """
        获取邮件详情
        
        Args:
            email_id: 邮件ID
        
        Returns:
            Dict: 邮件详情
        
        Raises:
            TemporaryMailAPIError: API错误
            TemporaryMailNetworkError: 网络错误
        """
        url = f"{self.base_url}?action=getEmail&value={email_id}"

        try:
            response = self.session.post(url)
            response.raise_for_status()
            data = response.json()

            self._handle_error(data)

            return data

        except requests.exceptions.RequestException as e:
            raise TemporaryMailNetworkError(f"网络请求失败: {str(e)}")

    # ========================================================================
    # 客户端过滤功能
    # ========================================================================

    def filter_messages(self, 
                       messages: Dict[str, Dict],
                       sender: Optional[str] = None,
                       subject_contains: Optional[str] = None,
                       has_attachments: Optional[bool] = None,
                       after_timestamp: Optional[int] = None,
                       custom_filter: Optional[Callable[[Dict], bool]] = None) -> Dict[str, Dict]:
        """
        客户端过滤邮件
        
        Args:
            messages: 邮件字典
            sender: 发件人邮箱（精确匹配）
            subject_contains: 主题包含的文本（不区分大小写）
            has_attachments: 是否有附件
            after_timestamp: 时间戳之后的邮件
            custom_filter: 自定义过滤函数
        
        Returns:
            Dict[str, Dict]: 过滤后的邮件字典
        
        Example:
            >>> # 过滤特定发件人
            >>> filtered = client.filter_messages(messages, sender="test@example.com")
            >>> 
            >>> # 过滤主题包含"验证"的邮件
            >>> filtered = client.filter_messages(messages, subject_contains="验证")
            >>> 
            >>> # 过滤有附件的邮件
            >>> filtered = client.filter_messages(messages, has_attachments=True)
            >>> 
            >>> # 自定义过滤
            >>> filtered = client.filter_messages(
            ...     messages,
            ...     custom_filter=lambda msg: len(msg.get('subject', '')) > 10
            ... )
        """
        filtered = {}
        
        for msg_id, msg_data in messages.items():
            # 发件人过滤
            if sender and msg_data.get('from') != sender:
                continue
            
            # 主题过滤
            if subject_contains:
                subject = msg_data.get('subject', '').lower()
                if subject_contains.lower() not in subject:
                    continue
            
            # 附件过滤
            if has_attachments is not None:
                msg_has_att = msg_data.get('has_attachments', False)
                if msg_has_att != has_attachments:
                    continue
            
            # 时间戳过滤
            if after_timestamp:
                msg_timestamp = msg_data.get('timestamp', 0)
                if msg_timestamp <= after_timestamp:
                    continue
            
            # 自定义过滤
            if custom_filter and not custom_filter(msg_data):
                continue
            
            filtered[msg_id] = msg_data
        
        return filtered

    # ========================================================================
    # 等待和轮询
    # ========================================================================

    def wait_for_email(
        self, 
        timeout: int = 300, 
        check_interval: int = 5, 
        verbose: bool = True,
        fetch_full_details: bool = False,
        filter_func: Optional[Callable[[Dict[str, Dict]], Dict[str, Dict]]] = None
    ) -> Optional[Dict[str, Dict]]:
        """
        等待接收邮件
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            verbose: 是否显示详细信息
            fetch_full_details: 是否获取完整详情
            filter_func: 过滤函数（可选）
        
        Returns:
            Optional[Dict[str, Dict]]: 邮件字典，超时返回None
        
        Raises:
            TemporaryMailAPIError: API错误
        
        Example:
            >>> # 基本用法
            >>> emails = client.wait_for_email(timeout=120)
            >>> 
            >>> # 等待特定邮件
            >>> emails = client.wait_for_email(
            ...     timeout=120,
            ...     filter_func=lambda msgs: client.filter_messages(
            ...         msgs, subject_contains="验证"
            ...     )
            ... )
        """
        if not self.secret_key:
            raise TemporaryMailAPIError("请先获取邮箱地址")

        start_time = time.time()
        checks = 0

        if verbose:
            print(f"\n⏳ 等待接收邮件... (超时: {timeout}秒)")

        while time.time() - start_time < timeout:
            try:
                emails = self.check_inbox(fetch_full_details=fetch_full_details)
                checks += 1

                # 应用过滤函数
                if filter_func and emails:
                    emails = filter_func(emails)

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

    # ========================================================================
    # 附件下载
    # ========================================================================

    def download_attachment(self, file_id: str, save_path: str) -> bool:
        """
        下载附件
        
        Args:
            file_id: 附件ID
            save_path: 保存路径
        
        Returns:
            bool: 是否成功
        
        Raises:
            TemporaryMailNetworkError: 网络错误
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
            raise TemporaryMailNetworkError(f"下载附件失败: {str(e)}")

    # ========================================================================
    # 格式化和显示
    # ========================================================================

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
        
        # 优先使用datetime对象，否则使用timestamp
        if email.get('datetime'):
            date_str = email['datetime'].strftime("%Y-%m-%d %H:%M:%S")
        elif email.get('timestamp'):
            dt = datetime.fromtimestamp(email['timestamp'])
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


# ============================================================================
# 向后兼容（通过继承实现）
# ============================================================================

# 注意：向后兼容别名已通过方法实现，无需额外赋值


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数 - 演示v2.0新功能"""
    print("=" * 60)
    print("TemporaryMail.com API 客户端 v2.0")
    print("=" * 60)

    # 创建客户端
    client = TemporaryMailClient()

    try:
        # 演示1：获取可用域名
        print("\n【演示1：获取可用域名】")
        domains = client.get_available_domains()
        print(f"✓ 可用域名数量: {len(domains)}")
        print(f"  前3个域名: {domains[:3]}")

        # 演示2：创建自定义邮箱
        print("\n【演示2：创建自定义邮箱】")
        username = f"testuser{int(time.time())}"
        email = client.create_custom_email(username, domains[0])
        print(f"✓ 自定义邮箱: {email}")

        # 演示3：等待接收邮件（获取完整详情）
        print("\n【演示3：等待接收邮件】")
        emails = client.wait_for_email(
            timeout=120, 
            check_interval=5,
            fetch_full_details=True
        )

        if emails:
            # 演示4：显示所有邮件
            print(f"\n【演示4：显示邮件】")
            print(f"📬 收件箱 ({len(emails)} 封邮件):")

            for idx, (msg_id, email_data) in enumerate(emails.items(), 1):
                print(f"\n[邮件 {idx}]")
                print(client.format_email(email_data))
                
                # 显示增强字段
                print(f"📊 增强字段:")
                print(f"   - timestamp: {email_data.get('timestamp')}")
                print(f"   - datetime: {email_data.get('datetime')}")
                print(f"   - has_attachments: {email_data.get('has_attachments')}")

                # 显示附件信息
                if email_data.get("attachments"):
                    print("📎 附件:")
                    for att in email_data["attachments"]:
                        size_kb = att["size"] / 1024
                        print(f"   - {att['filename']} ({size_kb:.2f} KB)")

            # 演示5：过滤功能
            print(f"\n【演示5：过滤功能】")
            filtered = client.filter_messages(
                emails,
                subject_contains="test"
            )
            print(f"✓ 主题包含'test'的邮件: {len(filtered)} 封")

        print("\n" + "=" * 60)
        print("✓ 演示完成")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except TemporaryMailAPIError as e:
        print(f"\n✗ API错误: {str(e)}")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")


if __name__ == "__main__":
    main()

# Made with Bob
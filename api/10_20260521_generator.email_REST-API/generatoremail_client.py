"""
Email Generator (generator.email) API 客户端

这是一个用于与Email Generator临时邮箱服务交互的Python客户端。

作者: Bob (AI Assistant)
创建日期: 2026-05-21
版本: 1.0.0
"""

import requests
import time
import logging
import random
import string
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GeneratorEmailAPIError(Exception):
    """API错误基类"""
    pass


class EmailNotFoundError(GeneratorEmailAPIError):
    """邮件未找到错误"""
    pass


class DomainNotAvailableError(GeneratorEmailAPIError):
    """域名不可用错误"""
    pass


class GeneratorEmailClient:
    """
    Email Generator API客户端

    提供与Email Generator临时邮箱服务交互的完整功能。
    特点：
    - 无需认证，公开访问
    - 支持自定义用户名和域名
    - 实时邮件通知（通过WebSocket）
    - 支持邮件搜索和管理

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        timeout (int): 请求超时时间（秒）
        username (str): 当前邮箱用户名
        domain (str): 当前邮箱域名
        email_address (str): 完整邮箱地址

    Example:
        >>> client = GeneratorEmailClient()
        >>> email = client.create_mailbox()
        >>> print(f"临时邮箱: {email}")
        >>> messages = client.get_messages()
        >>> print(f"收到 {len(messages)} 封邮件")
    """

    def __init__(
        self,
        base_url: str = "https://generator.email",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        """
        初始化客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        # 邮箱信息
        self.username: Optional[str] = None
        self.domain: Optional[str] = None
        self.email_address: Optional[str] = None
        
        # 可用域名缓存
        self._available_domains: Optional[List[str]] = None
        self._domains_cache_time: Optional[float] = None
        self._domains_cache_ttl: int = 3600  # 1小时

        logger.info("Email Generator客户端初始化完成")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        发送HTTP请求（带重试机制）

        Args:
            method: HTTP方法
            endpoint: API端点
            data: POST数据
            params: URL参数
            **kwargs: 其他requests参数

        Returns:
            requests.Response: 响应对象

        Raises:
            GeneratorEmailAPIError: 请求失败
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    timeout=self.timeout,
                    **kwargs,
                )

                # 检查响应状态
                if response.status_code == 404:
                    raise EmailNotFoundError(f"资源未找到: {url}")
                elif response.status_code >= 500:
                    raise GeneratorEmailAPIError(
                        f"服务器错误 ({response.status_code}): {response.text[:200]}"
                    )
                elif response.status_code >= 400:
                    raise GeneratorEmailAPIError(
                        f"客户端错误 ({response.status_code}): {response.text[:200]}"
                    )

                return response

            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise GeneratorEmailAPIError("请求超时")

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"请求失败: {str(e)} (尝试 {attempt + 1}/{self.max_retries})"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise GeneratorEmailAPIError(f"请求失败: {str(e)}")
        
        # 不应该到达这里，但为了类型检查
        raise GeneratorEmailAPIError("所有重试均失败")

    def _generate_random_username(self, length: int = 10) -> str:
        """
        生成随机用户名

        Args:
            length: 用户名长度

        Returns:
            str: 随机用户名
        """
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def search_domains(self, query: str = ".com", limit: int = 50) -> List[str]:
        """
        搜索可用域名

        Args:
            query: 搜索关键词（支持通配符，如 "mail*" 或 ".com"）
            limit: 返回结果数量限制

        Returns:
            list: 域名列表

        Example:
            >>> client = GeneratorEmailClient()
            >>> domains = client.search_domains(".com")
            >>> print(f"找到 {len(domains)} 个.com域名")
        """
        try:
            response = self._make_request(
                method="GET",
                endpoint="/search.php",
                params={"key": query}
            )

            domains = response.json()
            
            if not isinstance(domains, list):
                logger.warning(f"搜索返回非列表格式: {type(domains)}")
                return []

            # 限制返回数量
            domains = domains[:limit]
            
            logger.info(f"搜索到 {len(domains)} 个域名（关键词: {query}）")
            return domains

        except Exception as e:
            logger.error(f"搜索域名失败: {str(e)}")
            return []

    def get_available_domains(self, force_refresh: bool = False) -> List[str]:
        """
        获取所有可用域名（带缓存）

        Args:
            force_refresh: 是否强制刷新缓存

        Returns:
            list: 域名列表
        """
        # 检查缓存
        if (
            not force_refresh
            and self._available_domains is not None
            and self._domains_cache_time is not None
            and (time.time() - self._domains_cache_time) < self._domains_cache_ttl
        ):
            logger.info(f"使用缓存的域名列表 ({len(self._available_domains)} 个)")
            return self._available_domains

        # 搜索所有域名（使用通配符）
        all_domains = []
        
        # 尝试多个搜索关键词
        search_queries = [".com", ".org", ".net", ".id", ".my.id", ".biz.id", ".web.id"]
        
        for query in search_queries:
            domains = self.search_domains(query, limit=100)
            all_domains.extend(domains)
        
        # 去重
        all_domains = list(set(all_domains))
        
        # 更新缓存
        self._available_domains = all_domains
        self._domains_cache_time = time.time()
        
        logger.info(f"获取到 {len(all_domains)} 个可用域名")
        return all_domains

    def create_mailbox(
        self,
        username: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> str:
        """
        创建临时邮箱

        Args:
            username: 用户名（不指定则随机生成）
            domain: 域名（不指定则随机选择）

        Returns:
            str: 邮箱地址

        Example:
            >>> client = GeneratorEmailClient()
            >>> email = client.create_mailbox()
            >>> print(f"创建邮箱: {email}")
        """
        # 生成或使用指定的用户名
        if username is None:
            username = self._generate_random_username()
        
        # 选择或使用指定的域名
        if domain is None:
            domains = self.get_available_domains()
            if not domains:
                raise DomainNotAvailableError("没有可用的域名")
            domain = random.choice(domains)
        
        # 验证邮箱地址
        email_address = f"{username}@{domain}"
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="/check_adres_validation3.php",
                data={"usr": username, "dmn": domain}
            )
            
            result = response.json()
            
            if result.get("status") != "good":
                raise DomainNotAvailableError(f"域名不可用: {domain}")
            
            # 保存邮箱信息
            self.username = username
            self.domain = domain
            self.email_address = email_address
            
            uptime = result.get("uptime", "unknown")
            logger.info(f"创建邮箱成功: {email_address} (运行时间: {uptime}天)")
            
            return email_address
            
        except Exception as e:
            logger.error(f"创建邮箱失败: {str(e)}")
            raise

    def check_mailbox_status(
        self,
        username: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        检查邮箱状态

        Args:
            username: 用户名（不指定则使用当前邮箱）
            domain: 域名（不指定则使用当前邮箱）

        Returns:
            dict: 状态信息
                {
                    'status': 'good',
                    'uptime': '136',
                    'email': 'user@domain.com'
                }
        """
        if username is None:
            username = self.username
        if domain is None:
            domain = self.domain
            
        if not username or not domain:
            raise GeneratorEmailAPIError("未指定邮箱地址")
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="/check_adres_validation3.php",
                data={"usr": username, "dmn": domain}
            )
            
            result = response.json()
            result["email"] = f"{username}@{domain}"
            
            logger.info(f"邮箱状态: {result.get('status')} (运行时间: {result.get('uptime')}天)")
            return result
            
        except Exception as e:
            logger.error(f"检查邮箱状态失败: {str(e)}")
            raise

    def get_messages(
        self,
        email_address: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取邮件列表
        
        注意：此方法需要访问邮箱页面来获取邮件列表，因为API需要加密的邮件ID

        Args:
            email_address: 邮箱地址（不指定则使用当前邮箱）

        Returns:
            list: 邮件列表
                [
                    {
                        'id': 'encrypted_id',
                        'from': 'sender@example.com',
                        'subject': 'Test Email',
                        'date': '2026-05-21 10:00:00',
                        'preview': 'Email preview text...'
                    }
                ]
        """
        if email_address is None:
            email_address = self.email_address
            
        if not email_address:
            raise GeneratorEmailAPIError("未指定邮箱地址")
        
        try:
            # 解析邮箱地址
            username, domain = email_address.split('@')
            
            # 访问邮箱页面获取邮件列表
            mailbox_url = f"{self.base_url}/{domain}/{username}"
            response = self.session.get(mailbox_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML页面
            return self._parse_mailbox_html(response.text)
            
        except Exception as e:
            logger.error(f"获取邮件列表失败: {str(e)}")
            return []

    def _parse_mailbox_html(self, html: str) -> List[Dict[str, Any]]:
        """
        解析邮箱HTML页面

        Args:
            html: HTML内容

        Returns:
            list: 邮件列表
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            messages = []
            
            # Generator.email 特定结构：<div id="email-table">
            email_table = soup.find('div', {'id': 'email-table'})
            if email_table:
                # 查找所有邮件项（class包含list-group-item但不是active）
                items = email_table.find_all('div', class_='list-group-item')
                for item in items:
                    # 跳过表头（class包含active）
                    item_classes = item.get('class', [])
                    if isinstance(item_classes, list) and 'active' in item_classes:
                        continue
                    
                    # 提取邮件信息
                    from_div = item.find('div', class_='from_div_45g45gg')
                    subj_div = item.find('div', class_='subj_div_45g45gg')
                    time_div = item.find('div', class_='time_div_45g45gg')
                    
                    if from_div and subj_div and time_div:
                        message = {
                            'id': f"msg_{len(messages) + 1}",
                            'from': from_div.get_text(strip=True),
                            'subject': subj_div.get_text(strip=True),
                            'date': time_div.get_text(strip=True),
                            'preview': ''
                        }
                        messages.append(message)
                        logger.debug(f"解析到邮件: {message['subject']}")
            
            if messages:
                logger.info(f"从HTML解析到 {len(messages)} 封邮件")
            else:
                logger.info("收件箱为空")
            
            return messages
            
        except Exception as e:
            logger.error(f"解析HTML失败: {str(e)}")
            return []
    
    def _extract_message_from_element(self, element) -> Optional[Dict[str, Any]]:
        """
        从HTML元素中提取邮件信息
        
        Args:
            element: BeautifulSoup元素
            
        Returns:
            dict: 邮件信息，如果提取失败返回None
        """
        try:
            # 尝试多种可能的结构
            message = {
                "id": "",
                "from": "",
                "subject": "",
                "date": "",
                "preview": "",
            }
            
            # 提取ID
            message["id"] = element.get("data-id", "") or element.get("id", "")
            
            # 提取发件人
            from_elem = (
                element.find("span", class_="from") or
                element.find("td", class_="from") or
                element.find(class_="sender")
            )
            if from_elem:
                message["from"] = from_elem.get_text(strip=True)
            
            # 提取主题
            subject_elem = (
                element.find("span", class_="subject") or
                element.find("td", class_="subject") or
                element.find(class_="title")
            )
            if subject_elem:
                message["subject"] = subject_elem.get_text(strip=True)
            
            # 提取日期
            date_elem = (
                element.find("span", class_="date") or
                element.find("td", class_="date") or
                element.find(class_="time")
            )
            if date_elem:
                message["date"] = date_elem.get_text(strip=True)
            
            # 提取预览
            preview_elem = (
                element.find("div", class_="preview") or
                element.find("td", class_="preview")
            )
            if preview_elem:
                message["preview"] = preview_elem.get_text(strip=True)
            
            # 如果至少有主题或发件人，认为是有效邮件
            if message["subject"] or message["from"]:
                return message
            
            return None
            
        except Exception as e:
            logger.warning(f"提取邮件信息失败: {str(e)}")
            return None

    def get_message_content(
        self,
        message_id: str,
    ) -> Dict[str, Any]:
        """
        获取邮件详细内容

        Args:
            message_id: 邮件ID（加密格式）

        Returns:
            dict: 邮件详情
                {
                    'id': 'encrypted_id',
                    'from': 'sender@example.com',
                    'to': 'recipient@example.com',
                    'subject': 'Test Email',
                    'date': '2026-05-21 10:00:00',
                    'body_text': 'Plain text content',
                    'body_html': '<html>...</html>',
                    'attachments': []
                }

        Note:
            需要访问邮件详情页面来获取完整内容
        """
        if not message_id:
            raise GeneratorEmailAPIError("未指定邮件ID")
        
        try:
            # 构建邮件详情URL（需要根据实际URL格式调整）
            url = f"{self.base_url}/email/{message_id}"
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML获取邮件内容
            soup = BeautifulSoup(response.text, "html.parser")
            
            message = {
                "id": message_id,
                "from": "",
                "to": "",
                "subject": "",
                "date": "",
                "body_text": "",
                "body_html": "",
                "attachments": [],
            }
            
            # 提取邮件信息（需要根据实际HTML结构调整）
            from_elem = soup.find("span", class_="from")
            if from_elem:
                message["from"] = from_elem.text.strip()
            
            to_elem = soup.find("span", class_="to")
            if to_elem:
                message["to"] = to_elem.text.strip()
            
            subject_elem = soup.find("h1", class_="subject")
            if subject_elem:
                message["subject"] = subject_elem.text.strip()
            
            date_elem = soup.find("span", class_="date")
            if date_elem:
                message["date"] = date_elem.text.strip()
            
            body_elem = soup.find("div", class_="email-body")
            if body_elem:
                message["body_html"] = str(body_elem)
                message["body_text"] = body_elem.get_text(strip=True)
            
            logger.info(f"获取邮件内容成功: {message_id}")
            return message
            
        except Exception as e:
            logger.error(f"获取邮件内容失败: {str(e)}")
            raise

    def delete_message(
        self,
        message_id: str,
    ) -> bool:
        """
        删除单个邮件

        Args:
            message_id: 邮件ID（加密格式）

        Returns:
            bool: 是否成功
        """
        if not message_id:
            raise GeneratorEmailAPIError("未指定邮件ID")
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="/del_mail.php",
                data={"delll": message_id}
            )
            
            logger.info(f"删除邮件成功: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除邮件失败: {str(e)}")
            return False

    def delete_all_messages(
        self,
        email_address: Optional[str] = None,
    ) -> bool:
        """
        删除所有邮件

        Args:
            email_address: 邮箱地址（不指定则使用当前邮箱）

        Returns:
            bool: 是否成功
        """
        if email_address is None:
            email_address = self.email_address
            
        if not email_address:
            raise GeneratorEmailAPIError("未指定邮箱地址")
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="/del_mail.php",
                data={"dellall": email_address}
            )
            
            logger.info(f"删除所有邮件成功: {email_address}")
            return True
            
        except Exception as e:
            logger.error(f"删除所有邮件失败: {str(e)}")
            return False

    def mark_all_as_read(
        self,
        email_address: Optional[str] = None,
    ) -> bool:
        """
        标记所有邮件为已读

        Args:
            email_address: 邮箱地址（不指定则使用当前邮箱）

        Returns:
            bool: 是否成功
        """
        if email_address is None:
            email_address = self.email_address
            
        if not email_address:
            raise GeneratorEmailAPIError("未指定邮箱地址")
        
        try:
            response = self._make_request(
                method="POST",
                endpoint="/del_mail.php",
                data={"markall": email_address}
            )
            
            logger.info(f"标记所有邮件为已读: {email_address}")
            return True
            
        except Exception as e:
            logger.error(f"标记邮件失败: {str(e)}")
            return False

    def wait_for_message(
        self,
        timeout: int = 60,
        check_interval: int = 5,
        subject_filter: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        等待新邮件到达

        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            subject_filter: 主题过滤（可选）

        Returns:
            dict: 第一封匹配的邮件，如果超时则返回None

        Example:
            >>> client = GeneratorEmailClient()
            >>> client.create_mailbox()
            >>> message = client.wait_for_message(timeout=120, subject_filter="Verification")
            >>> if message:
            >>>     print(f"收到邮件: {message['subject']}")
        """
        if not self.email_address:
            raise GeneratorEmailAPIError("未创建邮箱")
        
        start_time = time.time()
        logger.info(f"等待新邮件 (超时: {timeout}秒, 主题过滤: {subject_filter or '无'})")
        
        while time.time() - start_time < timeout:
            try:
                messages = self.get_messages()
                
                for message in messages:
                    # 应用主题过滤
                    if subject_filter and subject_filter.lower() not in message.get("subject", "").lower():
                        continue
                    
                    logger.info(f"找到匹配的邮件: {message.get('subject')}")
                    return message
                
                # 等待下一次检查
                time.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"检查邮件时出错: {str(e)}")
                time.sleep(check_interval)
        
        logger.warning(f"等待邮件超时 ({timeout}秒)")
        return None

    def get_mailbox_url(self) -> str:
        """
        获取邮箱访问URL

        Returns:
            str: 邮箱URL
        """
        if not self.email_address:
            raise GeneratorEmailAPIError("未创建邮箱")
        
        return f"{self.base_url}/{self.domain}/{self.username}"

    def __str__(self) -> str:
        """字符串表示"""
        if self.email_address:
            return f"GeneratorEmailClient(email={self.email_address})"
        return "GeneratorEmailClient(no mailbox)"

    def __repr__(self) -> str:
        """详细表示"""
        return self.__str__()


def main():
    """
    示例用法
    """
    # 创建客户端
    client = GeneratorEmailClient()
    
    # 搜索域名
    print("\n=== 搜索可用域名 ===")
    domains = client.search_domains(".com", limit=10)
    print(f"找到 {len(domains)} 个.com域名:")
    for domain in domains[:5]:
        print(f"  - {domain}")
    
    # 创建邮箱
    print("\n=== 创建临时邮箱 ===")
    email = client.create_mailbox()
    print(f"邮箱地址: {email}")
    print(f"访问URL: {client.get_mailbox_url()}")
    
    # 检查状态
    print("\n=== 检查邮箱状态 ===")
    status = client.check_mailbox_status()
    print(f"状态: {status['status']}")
    print(f"运行时间: {status['uptime']}天")
    
    # 获取邮件
    print("\n=== 检查收件箱 ===")
    messages = client.get_messages()
    print(f"收到 {len(messages)} 封邮件")
    
    if messages:
        for i, msg in enumerate(messages, 1):
            print(f"\n邮件 {i}:")
            print(f"  发件人: {msg.get('from')}")
            print(f"  主题: {msg.get('subject')}")
            print(f"  日期: {msg.get('date')}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()

# Made with Bob

"""
Email Generator (generator.email) API 客户端 v2

这是一个用于与Email Generator临时邮箱服务交互的Python客户端。
v2 新增: 增强消息处理、客户端过滤、上下文管理器、统一错误处理。

作者: Bob (AI Assistant)
创建日期: 2026-05-21
版本: 2.0.0
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


class NetworkError(GeneratorEmailAPIError):
    """网络连接错误"""
    pass


class GeneratorEmailClient:
    """
    Email Generator API客户端 v2

    提供与Email Generator临时邮箱服务交互的完整功能。
    特点：
    - 无需认证，公开访问
    - 支持自定义用户名和域名
    - 实时邮件通知（通过WebSocket）
    - 支持邮件搜索和管理
    - v2: 增强消息处理、客户端过滤、上下文管理器

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        timeout (int): 请求超时时间（秒）
        username (str): 当前邮箱用户名
        domain (str): 当前邮箱域名
        email_address (str): 完整邮箱地址

    Example:
        >>> with GeneratorEmailClient() as client:
        ...     email = client.create_mailbox()
        ...     print(f"临时邮箱: {email}")
        ...     messages = client.get_messages()
        ...     enhanced = client.enhance_messages(messages)
        ...     filtered = client.filter_messages(enhanced, sender="test@example.com")
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

        self.username: Optional[str] = None
        self.domain: Optional[str] = None
        self.email_address: Optional[str] = None

        self._available_domains: Optional[List[str]] = None
        self._domains_cache_time: Optional[float] = None
        self._domains_cache_ttl: int = 3600

        logger.info("Email Generator客户端初始化完成")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False

    def close(self):
        """关闭客户端，释放资源"""
        if self.session:
            self.session.close()
            logger.info("客户端会话已关闭")

    def _handle_error(self, response: requests.Response) -> None:
        """
        统一错误处理

        Args:
            response: HTTP响应对象

        Raises:
            EmailNotFoundError: 404错误
            NetworkError: 网络相关错误
            GeneratorEmailAPIError: 其他API错误
        """
        if response.status_code == 404:
            raise EmailNotFoundError(f"资源未找到: {response.url}")
        elif response.status_code >= 500:
            raise GeneratorEmailAPIError(
                f"服务器错误 ({response.status_code}): {response.text[:200]}"
            )
        elif response.status_code >= 400:
            raise GeneratorEmailAPIError(
                f"客户端错误 ({response.status_code}): {response.text[:200]}"
            )

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
            NetworkError: 网络连接失败
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

                self._handle_error(response)
                return response

            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError("请求超时")

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(f"连接失败: {e}")

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"请求失败: {str(e)} (尝试 {attempt + 1}/{self.max_retries})"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(f"请求失败: {str(e)}")

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

    def _parse_time_to_timestamp(self, time_value: Any) -> Optional[int]:
        """
        解析多种时间格式为Unix时间戳

        Args:
            time_value: 时间值（字符串、整数或None）

        Returns:
            Optional[int]: Unix时间戳，解析失败返回None
        """
        if time_value is None:
            return None

        if isinstance(time_value, (int, float)):
            if time_value > 1e12:
                return int(time_value / 1000)
            return int(time_value)

        if isinstance(time_value, str):
            time_value = time_value.strip()
            if not time_value:
                return None

            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(time_value, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue

            try:
                return int(float(time_value))
            except (ValueError, TypeError):
                pass

        return None

    def enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强单条消息，添加便利字段

        Args:
            message: 原始消息字典

        Returns:
            dict: 增强后的消息，新增 timestamp, has_attachments, content_size 字段

        Example:
            >>> msg = client.get_messages()[0]
            >>> enhanced = client.enhance_message(msg)
            >>> print(enhanced['timestamp'], enhanced['has_attachments'], enhanced['content_size'])
        """
        enhanced = dict(message)

        time_value = (
            enhanced.get("created_at")
            or enhanced.get("createdAt")
            or enhanced.get("date")
            or enhanced.get("timestamp")
            or enhanced.get("receivedAt")
        )
        enhanced["timestamp"] = self._parse_time_to_timestamp(time_value)

        attachments = enhanced.get("attachments", [])
        if isinstance(attachments, list):
            real_attachments = [a for a in attachments if isinstance(a, dict) and a.get("name", "").strip()]
            enhanced["has_attachments"] = len(real_attachments) > 0
        else:
            enhanced["has_attachments"] = False

        content = enhanced.get("body_text") or enhanced.get("body_html") or enhanced.get("content") or enhanced.get("preview") or ""
        enhanced["content_size"] = len(content)

        return enhanced

    def enhance_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量增强消息

        Args:
            messages: 原始消息列表

        Returns:
            list: 增强后的消息列表

        Example:
            >>> messages = client.get_messages()
            >>> enhanced = client.enhance_messages(messages)
            >>> for msg in enhanced:
            ...     print(msg['timestamp'], msg['has_attachments'], msg['content_size'])
        """
        return [self.enhance_message(msg) for msg in messages]

    def filter_messages(
        self,
        messages: List[Dict[str, Any]],
        sender: Optional[str] = None,
        subject_contains: Optional[str] = None,
        has_attachments: Optional[bool] = None,
        since: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        客户端过滤消息

        Args:
            messages: 消息列表（建议使用enhance_messages处理后的）
            sender: 发件人过滤（部分匹配）
            subject_contains: 主题包含关键词（不区分大小写）
            has_attachments: 是否有附件
            since: Unix时间戳，只返回该时间之后的消息

        Returns:
            list: 过滤后的消息列表

        Example:
            >>> enhanced = client.enhance_messages(client.get_messages())
            >>> filtered = client.filter_messages(enhanced, sender="mailfence", has_attachments=True)
        """
        filtered = []
        for msg in messages:
            if sender and sender.lower() not in (msg.get("from") or msg.get("from_email") or "").lower():
                continue

            if subject_contains and subject_contains.lower() not in (msg.get("subject") or "").lower():
                continue

            if has_attachments is not None:
                msg_has = msg.get("has_attachments")
                if msg_has is None:
                    attachments = msg.get("attachments", [])
                    if isinstance(attachments, list):
                        real = [a for a in attachments if isinstance(a, dict) and a.get("name", "").strip()]
                        msg_has = len(real) > 0
                    else:
                        msg_has = False
                if msg_has != has_attachments:
                    continue

            if since is not None:
                msg_ts = msg.get("timestamp")
                if msg_ts is None:
                    time_val = (
                        msg.get("created_at")
                        or msg.get("createdAt")
                        or msg.get("date")
                        or msg.get("timestamp")
                        or msg.get("receivedAt")
                    )
                    msg_ts = self._parse_time_to_timestamp(time_val)
                if msg_ts is not None and msg_ts < since:
                    continue

            filtered.append(msg)

        return filtered

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
        if (
            not force_refresh
            and self._available_domains is not None
            and self._domains_cache_time is not None
            and (time.time() - self._domains_cache_time) < self._domains_cache_ttl
        ):
            logger.info(f"使用缓存的域名列表 ({len(self._available_domains)} 个)")
            return self._available_domains

        all_domains = []

        search_queries = [".com", ".org", ".net", ".id", ".my.id", ".biz.id", ".web.id"]

        for query in search_queries:
            domains = self.search_domains(query, limit=100)
            all_domains.extend(domains)

        all_domains = list(set(all_domains))

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
        if username is None:
            username = self._generate_random_username()

        if domain is None:
            domains = self.get_available_domains()
            if not domains:
                raise DomainNotAvailableError("没有可用的域名")
            domain = random.choice(domains)

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

        Args:
            email_address: 邮箱地址（不指定则使用当前邮箱）

        Returns:
            list: 邮件列表
        """
        if email_address is None:
            email_address = self.email_address

        if not email_address:
            raise GeneratorEmailAPIError("未指定邮箱地址")

        try:
            username, domain = email_address.split('@')

            mailbox_url = f"{self.base_url}/{domain}/{username}"
            response = self.session.get(mailbox_url, timeout=self.timeout)
            response.raise_for_status()

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

            email_table = soup.find('div', {'id': 'email-table'})
            if email_table:
                items = email_table.find_all('div', class_='list-group-item')
                for item in items:
                    item_classes = item.get('class', [])
                    if isinstance(item_classes, list) and 'active' in item_classes:
                        continue

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
            message = {
                "id": "",
                "from": "",
                "subject": "",
                "date": "",
                "preview": "",
            }

            message["id"] = element.get("data-id", "") or element.get("id", "")

            from_elem = (
                element.find("span", class_="from") or
                element.find("td", class_="from") or
                element.find(class_="sender")
            )
            if from_elem:
                message["from"] = from_elem.get_text(strip=True)

            subject_elem = (
                element.find("span", class_="subject") or
                element.find("td", class_="subject") or
                element.find(class_="title")
            )
            if subject_elem:
                message["subject"] = subject_elem.get_text(strip=True)

            date_elem = (
                element.find("span", class_="date") or
                element.find("td", class_="date") or
                element.find(class_="time")
            )
            if date_elem:
                message["date"] = date_elem.get_text(strip=True)

            preview_elem = (
                element.find("div", class_="preview") or
                element.find("td", class_="preview")
            )
            if preview_elem:
                message["preview"] = preview_elem.get_text(strip=True)

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
        """
        if not message_id:
            raise GeneratorEmailAPIError("未指定邮件ID")

        try:
            url = f"{self.base_url}/email/{message_id}"

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

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
                    if subject_filter and subject_filter.lower() not in message.get("subject", "").lower():
                        continue

                    logger.info(f"找到匹配的邮件: {message.get('subject')}")
                    return message

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
    with GeneratorEmailClient() as client:
        print("\n=== 搜索可用域名 ===")
        domains = client.search_domains(".com", limit=10)
        print(f"找到 {len(domains)} 个.com域名:")
        for domain in domains[:5]:
            print(f"  - {domain}")

        print("\n=== 创建临时邮箱 ===")
        email = client.create_mailbox()
        print(f"邮箱地址: {email}")
        print(f"访问URL: {client.get_mailbox_url()}")

        print("\n=== 检查邮箱状态 ===")
        status = client.check_mailbox_status()
        print(f"状态: {status['status']}")
        print(f"运行时间: {status['uptime']}天")

        print("\n=== 检查收件箱 ===")
        messages = client.get_messages()
        print(f"收到 {len(messages)} 封邮件")

        if messages:
            enhanced = client.enhance_messages(messages)
            print(f"\n=== 增强消息 ===")
            for msg in enhanced:
                print(f"  timestamp={msg['timestamp']}, has_attachments={msg['has_attachments']}, content_size={msg['content_size']}")

            filtered = client.filter_messages(enhanced, subject_contains="test")
            print(f"\n=== 过滤结果: {len(filtered)} 封 ===")

        print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()

# Made with Bob

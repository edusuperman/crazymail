"""
Guerrilla Mail API 客户端 v2.0.0

这是一个用于与Guerrilla Mail临时邮箱服务交互的Python客户端。
v2.0.0 新增：增强消息处理、客户端过滤、统一错误处理。

作者: IBM CrazyMail Project
创建日期: 2026-05-20
版本: 2.0.0
"""

import requests
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import html

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GuerrillaMailAPIError(Exception):
    """API错误基类"""
    pass


class AuthenticationError(GuerrillaMailAPIError):
    """认证错误"""
    pass


class RateLimitError(GuerrillaMailAPIError):
    """速率限制错误"""
    pass


class NetworkError(GuerrillaMailAPIError):
    """网络连接错误（DNS解析失败、连接拒绝、超时等）"""
    pass


class GuerrillaMailClient:
    """
    Guerrilla Mail API客户端 v2.0.0

    提供与Guerrilla Mail临时邮箱服务交互的完整功能。
    v2新增：消息增强、批量处理、客户端过滤、统一错误处理。

    Attributes:
        base_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        timeout (int): 请求超时时间（秒）
        max_retries (int): 最大重试次数
        retry_delay (int): 重试延迟（秒）

    Example:
        >>> client = GuerrillaMailClient()
        >>> email_info = client.get_email_address()
        >>> print(f"临时邮箱: {email_info['email_addr']}")
        >>> messages = client.check_email()
        >>> enhanced = client.enhance_messages(messages['list'])
        >>> filtered = client.filter_messages(enhanced, subject_contains="test")
    """

    def __init__(
        self,
        base_url: str = "http://api.guerrillamail.com",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
        lang: str = "en",
    ):
        """
        初始化客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            lang: 语言代码 (en, fr, nl, ru, tr, uk, ar, ko, jp, zh, zh-hant)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.lang = lang

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        self.sid_token: Optional[str] = None
        self.email_address: Optional[str] = None
        self.email_timestamp: Optional[int] = None
        self.alias: Optional[str] = None

        logger.info(f"Guerrilla Mail客户端初始化完成 (语言: {lang})")

    def _handle_error(self, response: requests.Response) -> None:
        """
        统一错误处理：检查HTTP响应状态并抛出适当的异常

        Args:
            response: requests.Response对象

        Raises:
            RateLimitError: 429状态码
            AuthenticationError: 401/403状态码
            NetworkError: 网络相关错误
            GuerrillaMailAPIError: 其他HTTP错误
        """
        if response.status_code == 429:
            raise RateLimitError("超过API速率限制，请稍后再试")
        elif response.status_code in (401, 403):
            raise AuthenticationError(f"认证失败: HTTP {response.status_code}")
        elif response.status_code >= 500:
            raise GuerrillaMailAPIError(f"服务器错误: HTTP {response.status_code}")
        elif response.status_code >= 400:
            raise GuerrillaMailAPIError(f"客户端错误: HTTP {response.status_code}")

    def _make_request(
        self,
        function: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """
        发送API请求

        Args:
            function: API函数名
            params: 请求参数
            method: HTTP方法 (GET/POST)

        Returns:
            dict: API响应数据

        Raises:
            GuerrillaMailAPIError: API请求失败
            NetworkError: 网络连接错误
            RateLimitError: 超过速率限制
        """
        url = f"{self.base_url}/ajax.php"

        request_params = {
            "f": function,
            "ip": "127.0.0.1",
            "agent": "Mozilla",
        }

        if params:
            request_params.update(params)

        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, params=request_params, timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url, data=request_params, timeout=self.timeout
                    )

                self._handle_error(response)
                response.raise_for_status()

                if "PHPSESSID" in response.cookies:
                    self.sid_token = response.cookies["PHPSESSID"]
                    logger.debug(f"会话ID已更新: {self.sid_token}")

                data = response.json()

                if "auth" in data and not data["auth"].get("success", True):
                    error_codes = data["auth"].get("error_codes", [])
                    raise AuthenticationError(f"认证失败: {error_codes}")

                logger.debug(f"API请求成功: {function}")
                return data

            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError("请求超时，网络连接可能不稳定")

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(f"网络连接失败: {e}")

            except requests.exceptions.HTTPError as e:
                if e.response is not None:
                    self._handle_error(e.response)
                logger.error(f"HTTP错误: {e}")
                raise GuerrillaMailAPIError(f"HTTP错误: {e}")

            except (GuerrillaMailAPIError, AuthenticationError, RateLimitError, NetworkError):
                raise

            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise NetworkError(f"网络请求失败: {e}")

        raise GuerrillaMailAPIError("达到最大重试次数")

    def enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强单条消息：添加便利计算字段

        添加的字段:
            - timestamp (int): Unix时间戳（从mail_timestamp或mail_date解析）
            - has_attachments (bool): 是否有附件（基于att字段）
            - content_size (int): 邮件正文大小（字节）

        Args:
            message: 原始消息字典

        Returns:
            dict: 增强后的消息（原地修改并返回）

        Example:
            >>> raw = client.fetch_email(123)
            >>> enhanced = client.enhance_message(raw)
            >>> print(enhanced['timestamp'], enhanced['has_attachments'])
        """
        enhanced = dict(message)

        # timestamp: 优先使用mail_timestamp，否则尝试解析mail_date
        if "mail_timestamp" in enhanced and enhanced["mail_timestamp"]:
            enhanced["timestamp"] = int(enhanced["mail_timestamp"])
        elif "mail_date" in enhanced and enhanced["mail_date"]:
            try:
                dt = datetime.strptime(str(enhanced["mail_date"]), "%Y-%m-%d %H:%M:%S")
                enhanced["timestamp"] = int(dt.timestamp())
            except (ValueError, TypeError):
                enhanced["timestamp"] = None
        else:
            enhanced["timestamp"] = None

        # has_attachments: 基于att字段（>0表示有附件）
        att = enhanced.get("att", 0)
        enhanced["has_attachments"] = bool(att and int(att) > 0)

        # content_size: 邮件正文大小
        body = enhanced.get("mail_body", "")
        enhanced["content_size"] = len(str(body)) if body else 0

        return enhanced

    def enhance_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量增强消息列表

        Args:
            messages: 原始消息列表

        Returns:
            list: 增强后的消息列表

        Example:
            >>> result = client.check_email()
            >>> enhanced = client.enhance_messages(result['list'])
            >>> for msg in enhanced:
            ...     print(f"{msg['mail_from']}: {msg['timestamp']}")
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
        客户端侧消息过滤

        支持按发件人、主题关键词、附件状态、时间范围过滤。
        消息应先经过enhance_messages()处理以获得最佳过滤效果。

        Args:
            messages: 消息列表（建议使用enhance_messages增强后的）
            sender: 发件人邮箱地址（精确匹配，大小写不敏感）
            subject_contains: 主题包含的关键词（大小写不敏感）
            has_attachments: 是否有过滤器
            since: Unix时间戳，只返回此时间之后的消息

        Returns:
            list: 过滤后的消息列表

        Example:
            >>> enhanced = client.enhance_messages(result['list'])
            >>> with_attachments = client.filter_messages(enhanced, has_attachments=True)
            >>> recent = client.filter_messages(enhanced, since=int(time.time()) - 3600)
            >>> from_admin = client.filter_messages(enhanced, sender="admin@example.com")
        """
        filtered = []
        for msg in messages:
            # 发件人过滤
            if sender is not None:
                msg_from = str(msg.get("mail_from", "")).lower()
                if sender.lower() not in msg_from:
                    continue

            # 主题过滤
            if subject_contains is not None:
                msg_subject = str(msg.get("mail_subject", "")).lower()
                if subject_contains.lower() not in msg_subject:
                    continue

            # 附件过滤
            if has_attachments is not None:
                msg_has_att = msg.get("has_attachments", False)
                # 兼容原始字段
                if "has_attachments" not in msg:
                    att = msg.get("att", 0)
                    msg_has_att = bool(att and int(att) > 0)
                if msg_has_att != has_attachments:
                    continue

            # 时间过滤
            if since is not None:
                ts = msg.get("timestamp")
                if ts is None:
                    # 尝试从原始字段获取
                    ts = msg.get("mail_timestamp")
                if ts is None or int(ts) < since:
                    continue

            filtered.append(msg)

        return filtered

    def get_email_address(self, subscr: Optional[str] = None) -> Dict[str, Any]:
        """
        获取或创建临时邮箱地址

        Args:
            subscr: 订阅cookie数据（可选）

        Returns:
            dict: 邮箱信息
        """
        params = {"lang": self.lang}
        if subscr:
            params["SUBSCR"] = subscr

        data = self._make_request("get_email_address", params)

        self.email_address = data.get("email_addr")
        self.email_timestamp = data.get("email_timestamp")
        self.alias = data.get("alias")
        self.sid_token = data.get("sid_token")

        logger.info(f"获取邮箱地址: {self.email_address}")
        return data

    def set_email_user(self, email_user: str) -> Dict[str, Any]:
        """
        设置自定义邮箱用户名

        Args:
            email_user: 邮箱用户名部分（@符号前的部分）

        Returns:
            dict: 更新后的邮箱信息
        """
        params = {"email_user": email_user, "lang": self.lang}

        data = self._make_request("set_email_user", params, method="POST")

        self.email_address = data.get("email_addr")
        self.email_timestamp = data.get("email_timestamp")

        logger.info(f"邮箱地址已更新: {self.email_address}")
        return data

    def check_email(self, seq: int = 0) -> Dict[str, Any]:
        """
        检查新邮件

        Args:
            seq: 最旧邮件的序列号（默认0表示检查所有新邮件）

        Returns:
            dict: 邮件列表和统计信息
        """
        params = {"seq": seq}
        data = self._make_request("check_email", params)

        logger.info(f"检查邮件: 找到 {data.get('count', 0)} 封新邮件")
        return data

    def get_email_list(
        self, offset: int = 0, seq: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取邮件列表

        Args:
            offset: 跳过的邮件数量（用于分页）
            seq: 第一封邮件的序列号（可选）

        Returns:
            dict: 邮件列表
        """
        params = {"offset": offset}
        if seq is not None:
            params["seq"] = seq

        data = self._make_request("get_email_list", params)

        logger.info(
            f"获取邮件列表: offset={offset}, 返回 {len(data.get('list', []))} 封邮件"
        )
        return data

    def fetch_email(self, email_id: int) -> Dict[str, Any]:
        """
        获取邮件完整内容

        Args:
            email_id: 邮件ID

        Returns:
            dict: 邮件详细信息
        """
        params = {"email_id": email_id}
        data = self._make_request("fetch_email", params)

        logger.info(f"获取邮件内容: ID={email_id}")
        return data

    def forget_me(self, email_addr: Optional[str] = None) -> bool:
        """
        忘记当前邮箱地址

        Args:
            email_addr: 要忘记的邮箱地址（可选，默认当前邮箱）

        Returns:
            bool: 是否成功
        """
        params = {}
        if email_addr:
            params["email_addr"] = email_addr
        elif self.email_address:
            params["email_addr"] = self.email_address

        data = self._make_request("forget_me", params, method="POST")

        self.email_address = None
        self.email_timestamp = None
        self.alias = None

        logger.info("已忘记当前邮箱地址")
        return True

    def del_email(self, email_ids: List[int]) -> Dict[str, Any]:
        """
        删除邮件

        Args:
            email_ids: 要删除的邮件ID列表

        Returns:
            dict: 删除结果
        """
        params = {}
        for i, email_id in enumerate(email_ids):
            params[f"email_ids[{i}]"] = email_id

        data = self._make_request("del_email", params, method="POST")

        logger.info(f"删除邮件: {len(email_ids)} 封")
        return data

    def get_older_list(self, seq: int) -> Dict[str, Any]:
        """
        获取更早的邮件列表

        Args:
            seq: 起始序列号

        Returns:
            dict: 邮件列表
        """
        params = {"seq": seq}
        data = self._make_request("get_older_list", params)

        logger.info(f"获取更早的邮件: seq={seq}")
        return data

    def get_email_timestamp(self) -> Optional[int]:
        """
        获取当前邮箱的创建时间戳

        Returns:
            int: Unix时间戳，如果未初始化则返回None
        """
        return self.email_timestamp

    def get_remaining_time(self) -> Optional[int]:
        """
        获取邮箱剩余有效时间（秒）

        Returns:
            int: 剩余秒数，如果未初始化则返回None
        """
        if self.email_timestamp is None:
            return None

        current_time = int(time.time())
        elapsed = current_time - self.email_timestamp
        remaining = 3600 - elapsed

        return max(0, remaining)

    def is_expired(self) -> bool:
        """
        检查邮箱是否已过期

        Returns:
            bool: True表示已过期
        """
        remaining = self.get_remaining_time()
        if remaining is None:
            return True
        return remaining <= 0

    def wait_for_email(
        self, timeout: int = 60, check_interval: int = 5, min_count: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        等待新邮件到达

        Args:
            timeout: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
            min_count: 最少邮件数量

        Returns:
            list: 邮件列表，超时返回None
        """
        start_time = time.time()
        seq = 0

        while time.time() - start_time < timeout:
            if self.is_expired():
                logger.warning("邮箱已过期")
                return None

            result = self.check_email(seq=seq)
            mail_list = result.get("list", [])

            if len(mail_list) >= min_count:
                logger.info(f"收到 {len(mail_list)} 封新邮件")
                return mail_list

            time.sleep(check_interval)

        logger.warning(f"等待邮件超时 ({timeout}秒)")
        return None

    def close(self):
        """关闭客户端会话"""
        if self.session:
            self.session.close()
            logger.info("客户端会话已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        """字符串表示"""
        if self.email_address:
            remaining = self.get_remaining_time()
            if remaining:
                return f"<GuerrillaMailClient v2 email={self.email_address} remaining={remaining}s>"
            return f"<GuerrillaMailClient v2 email={self.email_address} (expired)>"
        return f"<GuerrillaMailClient v2 (未初始化)>"


if __name__ == "__main__":
    client = GuerrillaMailClient()

    info = client.get_email_address()
    print(f"临时邮箱: {info['email_addr']}")
    print(f"别名: {info['alias']}")

    result = client.check_email()
    print(f"\n收件箱: {len(result['list'])} 封邮件")

    # v2: 增强消息
    enhanced = client.enhance_messages(result["list"])
    for mail in enhanced:
        print(f"  - {mail['mail_from']}: {mail['mail_subject']}")
        print(f"    timestamp={mail['timestamp']} attachments={mail['has_attachments']} size={mail['content_size']}")

    # v2: 过滤示例
    with_att = client.filter_messages(enhanced, has_attachments=True)
    print(f"\n有附件的邮件: {len(with_att)} 封")

    remaining = client.get_remaining_time()
    if remaining is not None:
        print(f"\n邮箱剩余时间: {remaining // 60} 分钟 {remaining % 60} 秒")
    else:
        print("\n邮箱未初始化")

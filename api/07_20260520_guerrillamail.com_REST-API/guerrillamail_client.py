"""
Guerrilla Mail API 客户端

这是一个用于与Guerrilla Mail临时邮箱服务交互的Python客户端。

作者: IBM CrazyMail Project
创建日期: 2026-05-20
版本: 1.0.0
"""

import requests
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import html

# 配置日志
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


class GuerrillaMailClient:
    """
    Guerrilla Mail API客户端

    提供与Guerrilla Mail临时邮箱服务交互的完整功能。

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
        >>> print(f"收到 {len(messages['list'])} 封邮件")
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

        # 初始化会话
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

        # 会话相关
        self.sid_token: Optional[str] = None

        # 邮箱相关
        self.email_address: Optional[str] = None
        self.email_timestamp: Optional[int] = None
        self.alias: Optional[str] = None

        logger.info(f"Guerrilla Mail客户端初始化完成 (语言: {lang})")

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
            RateLimitError: 超过速率限制
        """
        url = f"{self.base_url}/ajax.php"

        # 准备参数
        request_params = {
            "f": function,
            "ip": "127.0.0.1",  # 客户端IP
            "agent": "Mozilla",  # 用户代理简称
        }

        if params:
            request_params.update(params)

        # 重试逻辑
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

                response.raise_for_status()

                # 更新会话cookie
                if "PHPSESSID" in response.cookies:
                    self.sid_token = response.cookies["PHPSESSID"]
                    logger.debug(f"会话ID已更新: {self.sid_token}")

                data = response.json()

                # 检查认证状态
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
                    raise GuerrillaMailAPIError("请求超时")

            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    raise RateLimitError("超过API速率限制，请稍后再试")
                logger.error(f"HTTP错误: {e}")
                raise GuerrillaMailAPIError(f"HTTP错误: {e}")

            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise GuerrillaMailAPIError(f"请求失败: {e}")

        raise GuerrillaMailAPIError("达到最大重试次数")

    def get_email_address(self, subscr: Optional[str] = None) -> Dict[str, Any]:
        """
        获取或创建临时邮箱地址

        初始化会话并获取邮箱地址。如果会话已存在，返回现有邮箱地址。

        Args:
            subscr: 订阅cookie数据（可选）

        Returns:
            dict: 邮箱信息
                {
                    'email_addr': str,  # 完整邮箱地址
                    'email_timestamp': int,  # Unix时间戳
                    'alias': str,  # 邮箱别名
                    'sid_token': str  # 会话ID
                }

        Example:
            >>> client = GuerrillaMailClient()
            >>> info = client.get_email_address()
            >>> print(info['email_addr'])
            'abc123@guerrillamailblock.com'
        """
        params = {"lang": self.lang}
        if subscr:
            params["SUBSCR"] = subscr

        data = self._make_request("get_email_address", params)

        # 保存邮箱信息
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

        Example:
            >>> client.set_email_user('myname')
            >>> print(client.email_address)
            'myname@guerrillamailblock.com'
        """
        params = {"email_user": email_user, "lang": self.lang}

        data = self._make_request("set_email_user", params, method="POST")

        # 更新邮箱信息
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
                {
                    'list': List[Dict],  # 邮件列表（最多20封）
                    'count': str,  # 新邮件总数
                    'email': str,  # 当前邮箱地址
                    'ts': int,  # 邮箱时间戳
                    'sid_token': str  # 会话ID
                }

        Example:
            >>> result = client.check_email()
            >>> for mail in result['list']:
            ...     print(f"{mail['mail_from']}: {mail['mail_subject']}")
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
            dict: 邮件列表（格式同check_email）

        Example:
            >>> # 获取前20封邮件
            >>> result = client.get_email_list(offset=0)
            >>> # 获取接下来的20封
            >>> result = client.get_email_list(offset=20)
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
                {
                    'mail_id': int,
                    'mail_from': str,
                    'mail_subject': str,
                    'mail_body': str,  # 邮件正文（HTML已过滤）
                    'mail_timestamp': int,
                    'mail_date': str,
                    'mail_read': int,  # 0=未读, 1=已读
                    'att': int,  # 附件数量
                    'size': int  # 邮件大小（字节）
                }

        Example:
            >>> mail = client.fetch_email(1)
            >>> print(mail['mail_subject'])
            >>> print(mail['mail_body'])
        """
        params = {"email_id": email_id}
        data = self._make_request("fetch_email", params)

        logger.info(f"获取邮件内容: ID={email_id}")
        return data

    def forget_me(self, email_addr: Optional[str] = None) -> bool:
        """
        忘记当前邮箱地址

        不会删除邮箱，只是从当前会话中移除。

        Args:
            email_addr: 要忘记的邮箱地址（可选，默认当前邮箱）

        Returns:
            bool: 是否成功

        Example:
            >>> client.forget_me()
            True
        """
        params = {}
        if email_addr:
            params["email_addr"] = email_addr
        elif self.email_address:
            params["email_addr"] = self.email_address

        data = self._make_request("forget_me", params, method="POST")

        # 清除本地邮箱信息
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

        Example:
            >>> client.del_email([1, 2, 3])
            {'deleted_ids': [1, 2, 3]}
        """
        # 构建email_ids参数
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
            dict: 邮件列表（格式同check_email）
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

        邮箱有效期为60分钟（3600秒）

        Returns:
            int: 剩余秒数，如果未初始化则返回None

        Example:
            >>> remaining = client.get_remaining_time()
            >>> print(f"邮箱还有 {remaining // 60} 分钟过期")
        """
        if self.email_timestamp is None:
            return None

        current_time = int(time.time())
        elapsed = current_time - self.email_timestamp
        remaining = 3600 - elapsed  # 60分钟 = 3600秒

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

        Example:
            >>> # 等待至少1封新邮件，最多等60秒
            >>> mails = client.wait_for_email(timeout=60)
            >>> if mails:
            ...     print(f"收到 {len(mails)} 封邮件")
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

    def __repr__(self) -> str:
        """字符串表示"""
        if self.email_address:
            remaining = self.get_remaining_time()
            if remaining:
                return f"<GuerrillaMailClient email={self.email_address} remaining={remaining}s>"
            return f"<GuerrillaMailClient email={self.email_address} (expired)>"
        return f"<GuerrillaMailClient (未初始化)>"


if __name__ == "__main__":
    # 简单测试
    client = GuerrillaMailClient()

    # 获取邮箱地址
    info = client.get_email_address()
    print(f"临时邮箱: {info['email_addr']}")
    print(f"别名: {info['alias']}")

    # 检查邮件
    result = client.check_email()
    print(f"\n收件箱: {len(result['list'])} 封邮件")

    for mail in result["list"]:
        print(f"  - {mail['mail_from']}: {mail['mail_subject']}")

    # 显示剩余时间
    remaining = client.get_remaining_time()
    if remaining is not None:
        print(f"\n邮箱剩余时间: {remaining // 60} 分钟 {remaining % 60} 秒")
    else:
        print("\n邮箱未初始化")

# Made with Bob

"""
Maildrop.cc GraphQL API Client v2

这是一个用于与Maildrop.cc GraphQL API交互的Python客户端。
Maildrop是一个免费的临时邮箱服务，使用GraphQL API。

特点:
- GraphQL API（不是REST）
- 无需认证
- 支持查询邮箱列表、获取邮件、删除邮件等
- 邮箱临时性：24小时无邮件自动清空
- 最大容量：每个邮箱最多10封邮件
- v2新增：enhance_message、filter_messages、统一错误处理、上下文管理器

作者: Bob (AI Assistant)
日期: 2026-05-21
版本: 2.0.0
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MaildropError(Exception):
    """Maildrop API 基础异常"""
    pass


class MaildropNetworkError(MaildropError):
    """网络相关错误（连接失败、超时等）"""
    pass


class MaildropAPIError(MaildropError):
    """API返回的业务错误（GraphQL错误、HTTP错误等）"""
    pass


class MaildropClient:
    """
    Maildrop.cc GraphQL API 客户端 v2

    这个客户端提供了与Maildrop GraphQL API交互的方法。

    特点:
    - 无需认证
    - GraphQL查询和变更
    - 完整的类型提示
    - 详细的错误处理
    - 自动重试机制
    - v2: enhance_message/filter_messages/统一错误处理/上下文管理器

    示例:
        >>> with MaildropClient() as client:
        ...     response = client.ping("Hello")
        ...     print(response)  # "pong Hello"
        ...
        ...     messages = client.get_inbox("testmailbox")
        ...     enhanced = client.enhance_messages(messages)
        ...     filtered = client.filter_messages(enhanced, sender="someone@example.com")
    """

    def __init__(
        self,
        base_url: str = "https://api.maildrop.cc/graphql",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        初始化Maildrop客户端

        Args:
            base_url: GraphQL API端点URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "MaildropClient/2.0.0 (Python)",
            }
        )
        logger.info(f"Maildrop客户端已初始化: {base_url}")

    def _handle_error(self, response: requests.Response) -> Dict[str, Any]:
        """
        统一错误处理：检查HTTP状态码并解析JSON响应

        Args:
            response: requests.Response 对象

        Returns:
            dict: 解析后的JSON数据

        Raises:
            MaildropNetworkError: 网络/HTTP层错误
            MaildropAPIError: API返回的业务错误
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status = response.status_code
            try:
                body = response.text[:500]
            except Exception:
                body = "<unable to read response body>"
            raise MaildropNetworkError(
                f"HTTP {status}: {body}"
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise MaildropNetworkError(f"连接失败: {e}") from e
        except requests.exceptions.Timeout as e:
            raise MaildropNetworkError(f"请求超时: {e}") from e
        except requests.exceptions.RequestException as e:
            raise MaildropNetworkError(f"请求异常: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise MaildropAPIError(
                f"无法解析JSON响应: {response.text[:200]}"
            ) from e

        if "errors" in data:
            error_messages = [err.get("message", str(err)) for err in data["errors"]]
            raise MaildropAPIError(f"GraphQL错误: {', '.join(error_messages)}")

        return data

    def _execute_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行GraphQL查询或变更

        Args:
            query: GraphQL查询字符串
            variables: 查询变量（可选）

        Returns:
            dict: API响应数据

        Raises:
            MaildropNetworkError: 网络层错误
            MaildropAPIError: GraphQL业务错误
        """
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"执行GraphQL查询 (尝试 {attempt + 1}/{self.max_retries})")
                logger.debug(f"Query: {query[:100]}...")
                if variables:
                    logger.debug(f"Variables: {variables}")

                response = self.session.post(
                    self.base_url, json=payload, timeout=self.timeout
                )

                data = self._handle_error(response)

                logger.debug(f"查询成功: {str(data)[:200]}...")
                return data

            except MaildropNetworkError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

            except (MaildropAPIError, MaildropError):
                raise

            except Exception as e:
                logger.error(f"执行查询时出错: {e}")
                raise MaildropError(f"执行查询时出错: {e}") from e

        raise MaildropError("未知错误：超出最大重试次数")

    def ping(self, message: str = "hello") -> str:
        """
        测试API连接

        Args:
            message: 要回显的消息

        Returns:
            str: 服务器响应（"pong " + message）

        Example:
            >>> client.ping("test")
            'pong test'
        """
        query = """
        query Ping($message: String!) {
            ping(message: $message)
        }
        """
        variables = {"message": message}

        try:
            result = self._execute_query(query, variables)
            return result["data"]["ping"]
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"Ping失败: {e}")
            raise

    def get_inbox(self, mailbox: str) -> List[Dict[str, Any]]:
        """
        获取邮箱的邮件列表

        Args:
            mailbox: 邮箱名称（不含@maildrop.cc）

        Returns:
            list: 邮件列表，每个邮件包含id, subject, date, headerfrom

        Example:
            >>> messages = client.get_inbox("testmailbox")
            >>> for msg in messages:
            ...     print(f"{msg['id']}: {msg['subject']}")
        """
        query = """
        query GetInbox($mailbox: String!) {
            inbox(mailbox: $mailbox) {
                id
                subject
                date
                headerfrom
            }
        }
        """
        variables = {"mailbox": mailbox}

        try:
            result = self._execute_query(query, variables)
            messages = result["data"]["inbox"]
            logger.info(f"获取到 {len(messages)} 封邮件")
            return messages if messages else []
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"获取邮箱列表失败: {e}")
            raise

    def get_message(self, mailbox: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定邮件的完整内容

        Args:
            mailbox: 邮箱名称
            message_id: 邮件ID

        Returns:
            dict: 邮件详情，包含id, subject, date, headerfrom, data, html
            None: 如果邮件不存在

        Example:
            >>> message = client.get_message("testmailbox", "abc123")
            >>> print(message['subject'])
            >>> print(message['html'])
        """
        query = """
        query GetMessage($mailbox: String!, $id: String!) {
            message(mailbox: $mailbox, id: $id) {
                id
                subject
                date
                headerfrom
                data
                html
            }
        }
        """
        variables = {"mailbox": mailbox, "id": message_id}

        try:
            result = self._execute_query(query, variables)
            message = result["data"]["message"]
            if message:
                logger.info(f"获取邮件成功: {message_id}")
            else:
                logger.warning(f"邮件不存在: {message_id}")
            return message
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"获取邮件失败: {e}")
            raise

    def delete_message(self, mailbox: str, message_id: str) -> bool:
        """
        删除特定邮件

        Args:
            mailbox: 邮箱名称
            message_id: 邮件ID

        Returns:
            bool: 删除是否成功

        Example:
            >>> success = client.delete_message("testmailbox", "abc123")
            >>> print(f"删除{'成功' if success else '失败'}")
        """
        mutation = """
        mutation DeleteMessage($mailbox: String!, $id: String!) {
            delete(mailbox: $mailbox, id: $id)
        }
        """
        variables = {"mailbox": mailbox, "id": message_id}

        try:
            result = self._execute_query(mutation, variables)
            success = result["data"]["delete"]
            if success:
                logger.info(f"删除邮件成功: {message_id}")
            else:
                logger.warning(f"删除邮件失败: {message_id}")
            return success
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"删除邮件失败: {e}")
            raise

    def get_mailbox_alias(self, mailbox: str) -> Optional[str]:
        """
        获取邮箱的别名

        Args:
            mailbox: 邮箱名称

        Returns:
            str: 邮箱别名
            None: 如果没有别名

        Example:
            >>> alias = client.get_mailbox_alias("testmailbox")
            >>> print(f"别名: {alias}")
        """
        query = """
        query GetAlias($mailbox: String!) {
            altinbox(mailbox: $mailbox)
        }
        """
        variables = {"mailbox": mailbox}

        try:
            result = self._execute_query(query, variables)
            alias = result["data"]["altinbox"]
            logger.info(f"获取别名成功: {alias}")
            return alias
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"获取别名失败: {e}")
            raise

    def get_statistics(self) -> Dict[str, int]:
        """
        获取Maildrop系统统计信息

        Returns:
            dict: 包含blocked和saved的统计信息
                - blocked: 被阻止的邮件数
                - saved: 保存的邮件数

        Example:
            >>> stats = client.get_statistics()
            >>> print(f"阻止: {stats['blocked']}, 保存: {stats['saved']}")
        """
        query = """
        query GetStats {
            statistics {
                blocked
                saved
            }
        }
        """

        try:
            result = self._execute_query(query)
            stats = result["data"]["statistics"]
            logger.info(f"统计信息: 阻止={stats['blocked']}, 保存={stats['saved']}")
            return stats
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise

    def get_status(self) -> str:
        """
        检查服务状态

        Returns:
            str: 服务状态（通常是"ok"）

        Example:
            >>> status = client.get_status()
            >>> print(f"服务状态: {status}")
        """
        query = """
        query CheckStatus {
            status
        }
        """

        try:
            result = self._execute_query(query)
            status = result["data"]["status"]
            logger.info(f"服务状态: {status}")
            return status
        except (MaildropNetworkError, MaildropAPIError):
            raise
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            raise

    def wait_for_message(
        self,
        mailbox: str,
        timeout: int = 60,
        check_interval: int = 5,
        subject_filter: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        等待新邮件到达

        Args:
            mailbox: 邮箱名称
            timeout: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
            subject_filter: 主题过滤器（可选）

        Returns:
            dict: 第一封匹配的邮件
            None: 超时未收到邮件

        Example:
            >>> message = client.wait_for_message("testmailbox", timeout=60)
            >>> if message:
            ...     print(f"收到邮件: {message['subject']}")
        """
        start_time = time.time()
        logger.info(f"开始等待邮件: {mailbox} (超时: {timeout}秒)")

        while time.time() - start_time < timeout:
            try:
                messages = self.get_inbox(mailbox)

                if messages:
                    if subject_filter:
                        for msg in messages:
                            if subject_filter.lower() in msg.get("subject", "").lower():
                                logger.info(f"找到匹配邮件: {msg['subject']}")
                                return msg
                    else:
                        logger.info(f"找到邮件: {messages[0]['subject']}")
                        return messages[0]

                logger.debug(f"未找到邮件，等待 {check_interval} 秒...")
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"检查邮件时出错: {e}")
                time.sleep(check_interval)

        logger.warning(f"等待超时: {timeout}秒内未收到邮件")
        return None

    def enhance_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强单条邮件消息，添加便利字段

        添加字段:
        - timestamp: Unix时间戳（int），从时间字段解析
        - has_attachments: 是否有真实附件（bool），过滤空名称附件
        - content_size: 内容大小（int，字节数）

        Args:
            message: 原始邮件字典

        Returns:
            dict: 增强后的邮件字典（原地修改并返回）

        Example:
            >>> msg = client.get_message("testmailbox", "abc123")
            >>> enhanced = client.enhance_message(msg)
            >>> print(enhanced["timestamp"], enhanced["has_attachments"])
        """
        enhanced = dict(message)

        # 解析时间字段 —— 兼容多种服务的字段命名
        time_str = (
            enhanced.get("created_at")
            or enhanced.get("createdAt")
            or enhanced.get("date")
            or enhanced.get("timestamp")
            or enhanced.get("receivedAt")
        )
        enhanced["timestamp"] = self._parse_timestamp(time_str)

        # 判断是否有真实附件（过滤空名称附件，如签名图片、追踪像素）
        attachments = enhanced.get("attachments", [])
        if isinstance(attachments, list):
            real_attachments = [
                a for a in attachments if isinstance(a, dict) and a.get("name", "").strip()
            ]
            enhanced["has_attachments"] = len(real_attachments) > 0
        else:
            enhanced["has_attachments"] = False

        # 计算内容大小
        content = enhanced.get("data") or enhanced.get("content") or enhanced.get("body") or enhanced.get("html") or ""
        enhanced["content_size"] = len(content) if isinstance(content, str) else 0

        return enhanced

    def enhance_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量增强邮件列表

        Args:
            messages: 原始邮件列表

        Returns:
            list: 增强后的邮件列表

        Example:
            >>> messages = client.get_inbox("testmailbox")
            >>> enhanced = client.enhance_messages(messages)
            >>> for msg in enhanced:
            ...     print(msg["timestamp"], msg["has_attachments"], msg["content_size"])
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
        客户端侧邮件过滤

        Args:
            messages: 邮件列表（建议先用enhance_messages增强）
            sender: 按发件人过滤（模糊匹配headerfrom字段）
            subject_contains: 按主题关键字过滤（不区分大小写）
            has_attachments: 按是否有附件过滤
            since: Unix时间戳，只返回该时间之后的邮件

        Returns:
            list: 过滤后的邮件列表

        Example:
            >>> messages = client.enhance_messages(client.get_inbox("test"))
            >>> recent = client.filter_messages(messages, since=1700000000)
            >>> with_attach = client.filter_messages(messages, has_attachments=True)
        """
        filtered = []
        for msg in messages:
            if sender is not None:
                headerfrom = msg.get("headerfrom", "")
                if sender.lower() not in headerfrom.lower():
                    continue

            if subject_contains is not None:
                subject = msg.get("subject", "")
                if subject_contains.lower() not in subject.lower():
                    continue

            if has_attachments is not None:
                if msg.get("has_attachments") != has_attachments:
                    continue

            if since is not None:
                msg_ts = msg.get("timestamp")
                if msg_ts is None or msg_ts < since:
                    continue

            filtered.append(msg)

        return filtered

    @staticmethod
    def _parse_timestamp(time_value: Any) -> Optional[int]:
        """
        将多种格式的时间值解析为Unix时间戳

        Args:
            time_value: 时间值（str、int、float或None）

        Returns:
            int: Unix时间戳，解析失败返回None
        """
        if time_value is None:
            return None

        # 已经是Unix时间戳（int或float）
        if isinstance(time_value, (int, float)):
            return int(time_value)

        if isinstance(time_value, str):
            time_str = time_value.strip()
            if not time_str:
                return None

            # 尝试纯数字字符串（Unix时间戳）
            try:
                return int(float(time_str))
            except ValueError:
                pass

            # 尝试常见日期格式
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y/%m/%d %H:%M:%S",
                "%d %b %Y %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S %z",
                "%a, %d %b %Y %H:%M:%S %Z",
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue

            # 最后尝试dateutil（如果可用）
            try:
                from dateutil import parser as dateutil_parser
                dt = dateutil_parser.parse(time_str)
                return int(dt.timestamp())
            except (ImportError, Exception):
                pass

        return None

    def close(self):
        """关闭客户端会话"""
        self.session.close()
        logger.info("Maildrop客户端已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def main():
    """
    示例用法
    """
    with MaildropClient() as client:
        try:
            # 1. 测试连接
            print("\n=== 测试连接 ===")
            response = client.ping("Hello, Maildrop!")
            print(f"Ping响应: {response}")

            # 2. 检查服务状态
            print("\n=== 服务状态 ===")
            status = client.get_status()
            print(f"服务状态: {status}")

            # 3. 获取统计信息
            print("\n=== 统计信息 ===")
            stats = client.get_statistics()
            print(f"阻止的邮件: {stats['blocked']:,}")
            print(f"保存的邮件: {stats['saved']:,}")

            # 4. 使用测试邮箱
            test_mailbox = "testing"
            print(f"\n=== 邮箱: {test_mailbox}@maildrop.cc ===")

            # 5. 获取邮件列表
            print("\n获取邮件列表...")
            messages = client.get_inbox(test_mailbox)
            print(f"找到 {len(messages)} 封邮件")

            if messages:
                # 6. 增强邮件列表（v2功能）
                print("\n=== 增强邮件（v2）===")
                enhanced = client.enhance_messages(messages)
                for i, msg in enumerate(enhanced[:3], 1):
                    print(f"\n邮件 {i}:")
                    print(f"  ID: {msg['id']}")
                    print(f"  主题: {msg['subject']}")
                    print(f"  发件人: {msg['headerfrom']}")
                    print(f"  日期: {msg['date']}")
                    print(f"  timestamp: {msg['timestamp']}")
                    print(f"  has_attachments: {msg['has_attachments']}")
                    print(f"  content_size: {msg['content_size']}")

                # 7. 过滤邮件（v2功能）
                print("\n=== 过滤邮件（v2）===")
                filtered = client.filter_messages(enhanced, subject_contains="test")
                print(f"主题包含'test'的邮件: {len(filtered)} 封")

                # 8. 获取第一封邮件的完整内容
                first_msg_id = messages[0]["id"]
                print(f"\n=== 获取邮件详情: {first_msg_id} ===")
                message = client.get_message(test_mailbox, first_msg_id)
                if message:
                    enhanced_detail = client.enhance_message(message)
                    print(f"主题: {enhanced_detail['subject']}")
                    print(f"纯文本内容: {enhanced_detail['data'][:200]}...")
                    print(f"content_size: {enhanced_detail['content_size']}")
                    if enhanced_detail.get("html"):
                        print(f"HTML内容长度: {len(enhanced_detail['html'])} 字符")
            else:
                print("邮箱为空")

            # 9. 获取邮箱别名
            print(f"\n=== 邮箱别名 ===")
            alias = client.get_mailbox_alias(test_mailbox)
            print(f"别名: {alias}")

        except MaildropNetworkError as e:
            print(f"\n网络错误: {e}")
            import traceback
            traceback.print_exc()
        except MaildropAPIError as e:
            print(f"\nAPI错误: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob

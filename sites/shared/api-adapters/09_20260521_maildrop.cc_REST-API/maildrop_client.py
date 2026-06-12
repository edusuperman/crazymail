"""
Maildrop.cc GraphQL API Client

这是一个用于与Maildrop.cc GraphQL API交互的Python客户端。
Maildrop是一个免费的临时邮箱服务，使用GraphQL API。

特点:
- GraphQL API（不是REST）
- 无需认证
- 支持查询邮箱列表、获取邮件、删除邮件等
- 邮箱临时性：24小时无邮件自动清空
- 最大容量：每个邮箱最多10封邮件

作者: Bob (AI Assistant)
日期: 2026-05-21
版本: 1.0.0
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any

import requests


# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MaildropClient:
    """
    Maildrop.cc GraphQL API 客户端
    
    这个客户端提供了与Maildrop GraphQL API交互的方法。
    
    特点:
    - 无需认证
    - GraphQL查询和变更
    - 完整的类型提示
    - 详细的错误处理
    - 自动重试机制
    
    示例:
        >>> client = MaildropClient()
        >>> # 测试连接
        >>> response = client.ping("Hello")
        >>> print(response)  # "pong Hello"
        >>> 
        >>> # 获取邮箱列表
        >>> messages = client.get_inbox("testmailbox")
        >>> for msg in messages:
        ...     print(f"{msg['subject']} from {msg['headerfrom']}")
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
                "User-Agent": "MaildropClient/1.0.0 (Python)",
            }
        )
        logger.info(f"Maildrop客户端已初始化: {base_url}")

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
            Exception: 当请求失败或返回错误时
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

                response.raise_for_status()
                data = response.json()

                # 检查GraphQL错误
                if "errors" in data:
                    error_messages = [err.get("message", str(err)) for err in data["errors"]]
                    raise Exception(f"GraphQL错误: {', '.join(error_messages)}")

                logger.debug(f"查询成功: {str(data)[:200]}...")
                return data

            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise Exception("请求超时，已达到最大重试次数")
                time.sleep(2 ** attempt)  # 指数退避

            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"请求失败: {e}")
                time.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"执行查询时出错: {e}")
                raise

        raise Exception("未知错误：超出最大重试次数")

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
                    # 如果有主题过滤器，查找匹配的邮件
                    if subject_filter:
                        for msg in messages:
                            if subject_filter.lower() in msg.get("subject", "").lower():
                                logger.info(f"找到匹配邮件: {msg['subject']}")
                                return msg
                    else:
                        # 返回第一封邮件
                        logger.info(f"找到邮件: {messages[0]['subject']}")
                        return messages[0]

                logger.debug(f"未找到邮件，等待 {check_interval} 秒...")
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"检查邮件时出错: {e}")
                time.sleep(check_interval)

        logger.warning(f"等待超时: {timeout}秒内未收到邮件")
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
    # 创建客户端
    client = MaildropClient()

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
            # 显示前3封邮件
            for i, msg in enumerate(messages[:3], 1):
                print(f"\n邮件 {i}:")
                print(f"  ID: {msg['id']}")
                print(f"  主题: {msg['subject']}")
                print(f"  发件人: {msg['headerfrom']}")
                print(f"  日期: {msg['date']}")

            # 6. 获取第一封邮件的完整内容
            first_msg_id = messages[0]["id"]
            print(f"\n=== 获取邮件详情: {first_msg_id} ===")
            message = client.get_message(test_mailbox, first_msg_id)
            if message:
                print(f"主题: {message['subject']}")
                print(f"纯文本内容: {message['data'][:200]}...")
                if message.get("html"):
                    print(f"HTML内容长度: {len(message['html'])} 字符")

        else:
            print("邮箱为空")

        # 7. 获取邮箱别名
        print(f"\n=== 邮箱别名 ===")
        alias = client.get_mailbox_alias(test_mailbox)
        print(f"别名: {alias}")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        client.close()


if __name__ == "__main__":
    main()

# Made with Bob

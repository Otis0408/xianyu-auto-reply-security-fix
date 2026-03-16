"""
自动免拼发货模块

[SECURITY FIX] 原文件包含多层混淆的代码（hex -> base64 -> zlib -> exec()），
通过 exec() 动态执行解码后的Python代码。这是一个严重的安全风险：
1. 无法审计实际执行的代码内容
2. 可能包含恶意后门或数据窃取逻辑
3. 混淆本身就是可疑行为的标志

已移除混淆代码，替换为安全的占位实现。
如需此功能，请联系原作者获取明文源码或自行实现。
"""
from loguru import logger


class SecureFreeshipping:
    """自动免拼发货（安全占位实现）"""

    def __init__(self, *args, **kwargs):
        logger.warning("SecureFreeshipping: 混淆代码已被移除（安全原因），此功能已禁用")

    async def freeship(self, *args, **kwargs):
        logger.warning("SecureFreeshipping.freeship(): 功能已禁用（混淆代码已移除）")
        return {"success": False, "message": "功能已禁用：原混淆代码已被移除（安全原因）"}

    def __getattr__(self, name):
        def _disabled(*args, **kwargs):
            logger.warning(f"SecureFreeshipping.{name}(): 功能已禁用（混淆代码已移除）")
            return None
        return _disabled

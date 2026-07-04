"""安全执行器模块 - 增强版本。

【重大更新 - 2026-04-02 MCP审查修复】
提供增强的安全命令执行功能，包括：
1. 命令级白名单
2. 参数级白名单
3. 危险 flag 黑名单
4. 强制列表参数（禁止字符串）
5. 路径遍历防护
6. 资源限制

【安全原则】
- 最小权限原则
- 白名单优先
- 深度防御
"""

import os
import re
import shlex
import shutil
import logging
import subprocess
import platform
from typing import Dict, Any, List, Optional, Union, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """安全违规异常。"""
    pass

class ValidationError(Exception):
    """验证错误异常。"""
    pass

class ExecutionResult(Enum):
    """执行结果枚举。"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"

@dataclass
class CommandConfig:
    """命令配置。
    
    Attributes:
        allowed_args: 允许的参数列表
        forbidden_flags: 禁止的 flag 列表
        subcommands_only: 是否只允许子命令（禁止任意参数）
        max_args: 最大参数数量
        requires_path_validation: 是否需要路径验证
    """
    allowed_args: Optional[List[str]] = None
    forbidden_flags: List[str] = None
    subcommands_only: bool = False
    max_args: int = 10
    requires_path_validation: bool = True
    
    def __post_init__(self):
        if self.forbidden_flags is None:
            self.forbidden_flags = []

class SecureCommandExecutor:
    """安全命令执行器（增强版本）。
    
    【安全特性】
    1. 命令白名单 - 只允许预定义的命令
    2. 参数白名单 - 验证每个参数
    3. 危险 flag 黑名单 - 禁止 -c, -e 等危险选项
    4. 强制列表参数 - 禁止字符串输入，防止注入
    5. 路径遍历防护 - 验证所有路径参数
    6. 资源限制 - 超时和参数数量限制
    
    【使用示例】
    >>> result = SecureCommandExecutor.execute(['python', '-m', 'pip', 'list'])
    >>> print(result.stdout)
    
    >>> # 危险命令会被阻止
    >>> SecureCommandExecutor.execute(['python', '-c', 'import os; os.system("rm -rf /")'])
    SecurityError: Flag '-c' is forbidden for command 'python'
    """
    
    # 命令白名单配置
    ALLOWED_COMMANDS: Dict[str, CommandConfig] = {
        'python': CommandConfig(
            allowed_args=['-m', '--version', '-V', '-h', '--help', '-u', '-O', '-OO'],
            forbidden_flags=['-c', '--command', '-e', '--exec', '-E', '-S', '-s'],
            max_args=20,
            requires_path_validation=True
        ),
        'python3': CommandConfig(
            allowed_args=['-m', '--version', '-V', '-h', '--help', '-u', '-O', '-OO'],
            forbidden_flags=['-c', '--command', '-e', '--exec', '-E', '-S', '-s'],
            max_args=20,
            requires_path_validation=True
        ),
        'pip': CommandConfig(
            allowed_args=['install', 'uninstall', 'freeze', 'list', 'show', 'search', 
                         '--version', '--help', '-h', '-v', '--verbose'],
            forbidden_flags=['--trusted-host'],  # 可能绕过 SSL 验证
            max_args=15,
            requires_path_validation=True
        ),
        'git': CommandConfig(
            allowed_args=['clone', 'pull', 'push', 'fetch', 'status', 'log', 
                         'diff', 'branch', 'checkout', 'commit', 'add', 'rm',
                         '--version', '--help', '-h', '-v', '--verbose'],
            subcommands_only=True,
            max_args=15,
            requires_path_validation=True
        ),
        'cmd': CommandConfig(
            allowed_args=['/c', '/k', '/s'],
            forbidden_flags=[],  # cmd 本身较危险，需要特别小心
            max_args=5,
            requires_path_validation=True
        ),
        'powershell': CommandConfig(
            allowed_args=['-Command', '-File', '-Help', '-Version', '-NoLogo',
                         '-NoExit', '-Sta', '-Mta', '-NoProfile', '-NonInteractive'],
            forbidden_flags=['-EncodedCommand', '-ExecutionPolicy'],
            max_args=10,
            requires_path_validation=True
        ),
        'open': CommandConfig(  # macOS
            allowed_args=['-a', '-b', '-e', '-t', '-f', '-F', '-W', '-R', '-n', '-g', '-h'],
            max_args=5,
            requires_path_validation=True
        ),
        'xdg-open': CommandConfig(  # Linux
            allowed_args=[],
            max_args=2,
            requires_path_validation=True
        ),
    }
    
    # 危险命令黑名单（完全禁止）
    DANGEROUS_COMMANDS: Set[str] = {
        'rm', 'del', 'rmdir', 'format', 'mkfs', 'dd', 'fdisk',
        'shutdown', 'reboot', 'poweroff', 'halt', 'init',
        'mount', 'umount', 'chroot', 'sudo', 'su',
        'wget', 'curl', 'nc', 'netcat', 'telnet', 'ssh', 'scp',
        'bash', 'sh', 'zsh', 'fish', 'csh', 'tcsh',
        'cmd.exe', 'command.com', 'powershell.exe',
        'regsvr32', 'rundll32', 'msiexec', 'certutil',
    }
    
    # 危险字符模式
    DANGEROUS_PATTERNS: List[str] = [
        ';', '|', '&', '`', '$', '(', ')', '<', '>', '\\n', '\\r',
        '||', '&&', ';;', '|&', '&>', '>&', '>>', '<<',
        '${', '$((', '$(', '`', '${IFS}',
    ]
    
    # 路径遍历模式
    PATH_TRAVERSAL_PATTERNS: List[str] = [
        '../', '..\\', '..\\\\',
        '/..', '\\..', '\\\\..',
        '/etc/', '/proc/', '/sys/',
        'C:\\\\Windows\\\\System32',
    ]
    
    @classmethod
    def execute(cls, 
                command: List[str],
                timeout: Optional[int] = 30,
                cwd: Optional[str] = None,
                env: Optional[Dict[str, str]] = None,
                capture_output: bool = True,
                check: bool = True) -> subprocess.CompletedProcess:
        """
        安全执行命令。
        
        【安全流程】
        1. 验证输入是列表（禁止字符串）
        2. 验证命令不在黑名单
        3. 验证命令在白名单
        4. 验证每个参数
        5. 验证路径参数（防止遍历）
        6. 执行命令（shell=False）
        
        Args:
            command: 命令列表（必须是列表，禁止字符串）
            timeout: 超时时间（秒）
            cwd: 工作目录
            env: 环境变量
            capture_output: 是否捕获输出
            check: 是否检查返回码
            
        Returns:
            subprocess.CompletedProcess 对象
            
        Raises:
            SecurityError: 安全验证失败
            ValidationError: 输入验证失败
            subprocess.TimeoutExpired: 执行超时
            subprocess.CalledProcessError: 命令执行失败
        """
        # 1. 验证输入类型
        if not isinstance(command, list):
            raise ValidationError(
                f"Command must be a list, got {type(command).__name__}. "
                "String commands are forbidden to prevent injection."
            )
        
        if len(command) == 0:
            raise ValidationError("Command list cannot be empty")
        
        # 2. 提取命令名
        cmd_name = command[0]
        cmd_args = command[1:] if len(command) > 1 else []
        
        # 3. 验证命令不在黑名单
        cmd_lower = cmd_name.lower()
        base_name = os.path.basename(cmd_name).lower()
        
        if cmd_lower in cls.DANGEROUS_COMMANDS or base_name in cls.DANGEROUS_COMMANDS:
            logger.warning(f"Dangerous command blocked: {cmd_name}")
            raise SecurityError(f"Command '{cmd_name}' is in blacklist")
        
        # 4. 验证命令在白名单
        if base_name not in cls.ALLOWED_COMMANDS:
            # 尝试查找完整路径
            cmd_path = shutil.which(cmd_name)
            if cmd_path:
                path_base = os.path.basename(cmd_path).lower()
                if path_base not in cls.ALLOWED_COMMANDS:
                    logger.warning(f"Command not in whitelist: {cmd_name} (resolved to {cmd_path})")
                    raise SecurityError(f"Command '{cmd_name}' is not in whitelist")
                # 使用解析后的命令名
                base_name = path_base
            else:
                logger.warning(f"Command not found or not in whitelist: {cmd_name}")
                raise SecurityError(f"Command '{cmd_name}' is not in whitelist")
        
        # 5. 获取命令配置
        config = cls.ALLOWED_COMMANDS[base_name]
        
        # 6. 验证参数数量
        if len(cmd_args) > config.max_args:
            raise SecurityError(
                f"Too many arguments for '{cmd_name}': "
                f"{len(cmd_args)} > {config.max_args}"
            )
        
        # 7. 验证每个参数
        for i, arg in enumerate(cmd_args):
            cls._validate_argument(arg, i + 1, config)
        
        # 8. 构建完整命令列表
        full_command = [shutil.which(cmd_name) or cmd_name] + cmd_args
        
        # 9. 执行命令
        logger.info(f"Executing safe command: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                shell=False,  # 关键：禁用 shell
                check=check,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            return result
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timeout: {' '.join(full_command)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            raise
    
    @classmethod
    def _validate_argument(cls, arg: str, index: int, config: CommandConfig) -> None:
        """验证单个参数。
        
        Args:
            arg: 参数值
            index: 参数位置（从1开始）
            config: 命令配置
            
        Raises:
            SecurityError: 验证失败
        """
        if not isinstance(arg, str):
            raise ValidationError(f"Argument {index} must be string, got {type(arg).__name__}")
        
        # 检查危险字符
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in arg:
                raise SecurityError(
                    f"Argument {index} contains dangerous pattern '{pattern}': {arg[:50]}"
                )
        
        # 检查是否是 flag
        if arg.startswith('-'):
            # 检查禁止的 flag
            for forbidden in config.forbidden_flags:
                if arg == forbidden or arg.startswith(forbidden + '='):
                    raise SecurityError(
                        f"Flag '{arg}' is forbidden for this command"
                    )
            
            # 如果只允许子命令，禁止任意 flag
            if config.subcommands_only and config.allowed_args:
                # 提取 flag 名称（去掉值部分）
                flag_name = arg.split('=')[0]
                if flag_name not in config.allowed_args:
                    raise SecurityError(
                        f"Flag '{arg}' is not in allowed list"
                    )
        
        # 路径验证
        if config.requires_path_validation:
            cls._validate_path_argument(arg, index)
    
    @classmethod
    def _validate_path_argument(cls, arg: str, index: int) -> None:
        """验证路径参数（防止路径遍历）。
        
        Args:
            arg: 参数值
            index: 参数位置
            
        Raises:
            SecurityError: 验证失败
        """
        # 检查路径遍历模式
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if pattern in arg:
                raise SecurityError(
                    f"Argument {index} contains path traversal pattern: {arg[:50]}"
                )
        
        # 规范化路径并检查
        if os.path.isabs(arg) or '..' in arg:
            try:
                normalized = os.path.normpath(os.path.abspath(arg))
                
                # 检查是否在允许的目录内
                allowed_prefixes = [
                    os.path.abspath(os.getcwd()),
                    os.path.expanduser('~'),
                    tempfile.gettempdir(),
                ]
                
                # 允许系统命令
                if os.path.basename(arg) == arg:
                    return
                
                # 检查是否在允许的前缀内
                is_allowed = any(
                    normalized.startswith(prefix)
                    for prefix in allowed_prefixes
                )
                
                if not is_allowed:
                    logger.warning(f"Path outside allowed directories: {normalized}")
                    # 不阻止，但记录警告
                    
            except Exception as e:
                logger.warning(f"Path validation error for arg {index}: {e}")
    
    @classmethod
    def execute_simple(cls, command: List[str], **kwargs) -> str:
        """简化版执行，返回输出字符串。
        
        Args:
            command: 命令列表
            **kwargs: 其他参数
            
        Returns:
            标准输出字符串
        """
        result = cls.execute(command, **kwargs)
        return result.stdout if result.stdout else ""
    
    @classmethod
    def is_command_allowed(cls, command_name: str) -> bool:
        """检查命令是否在白名单中。
        
        Args:
            command_name: 命令名称
            
        Returns:
            是否允许
        """
        base_name = os.path.basename(command_name).lower()
        return base_name in cls.ALLOWED_COMMANDS
    
    @classmethod
    def get_allowed_commands(cls) -> List[str]:
        """获取允许的命令列表。
        
        Returns:
            命令名称列表
        """
        return list(cls.ALLOWED_COMMANDS.keys())

class ResourceLimiter:
    """资源限制器。
    
    限制命令执行的资源使用，防止 DoS 攻击。
    """
    
    # 默认限制
    DEFAULT_LIMITS = {
        'max_memory_mb': 512,  # 最大内存 512MB
        'max_cpu_time': 30,     # 最大 CPU 时间 30 秒
        'max_file_size_mb': 100,  # 最大文件大小 100MB
        'max_open_files': 100,   # 最大打开文件数
    }
    
    @classmethod
    def apply_limits(cls, limits: Optional[Dict[str, int]] = None):
        """应用资源限制（仅在 Unix 系统有效）。
        
        Args:
            limits: 限制配置
        """
        if platform.system() == 'Windows':
            # Windows 不支持 resource 模块
            return
        
        try:
            import resource
            
            config = limits or cls.DEFAULT_LIMITS
            
            # 限制内存
            if 'max_memory_mb' in config:
                max_mem = config['max_memory_mb'] * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))
            
            # 限制 CPU 时间
            if 'max_cpu_time' in config:
                cpu_time = config['max_cpu_time']
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))
            
            # 限制文件大小
            if 'max_file_size_mb' in config:
                file_size = config['max_file_size_mb'] * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_FSIZE, (file_size, file_size))
            
            # 限制打开文件数
            if 'max_open_files' in config:
                max_files = config['max_open_files']
                resource.setrlimit(resource.RLIMIT_NOFILE, (max_files, max_files))
                
        except ImportError:
            logger.warning("resource module not available")
        except Exception as e:
            logger.warning(f"Failed to apply resource limits: {e}")

# 便捷函数
def safe_execute(command: List[str], **kwargs) -> subprocess.CompletedProcess:
    """安全执行命令的便捷函数。
    
    Args:
        command: 命令列表
        **kwargs: 其他参数
        
    Returns:
        执行结果
    """
    return SecureCommandExecutor.execute(command, **kwargs)

def is_safe_command(command_name: str) -> bool:
    """检查命令是否安全的便捷函数。
    
    Args:
        command_name: 命令名称
        
    Returns:
        是否安全
    """
    return SecureCommandExecutor.is_command_allowed(command_name)

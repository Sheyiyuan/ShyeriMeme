import logging
import os
import sys
import threading
import time
import signal
from io import StringIO
from typing import List, Optional

# 添加配置导入
from utils.conf import Config

# 日志级别优先级映射（数值越大，级别越高）
LOG_LEVEL_PRIORITY = {
    'DEBUG': 1,
    'INFO': 2,
    'WARNING': 3,
    'WARN': 3,  # 别名
    'ERROR': 4,
    'CRITICAL': 5,
    'FATAL': 5  # 别名
}

class LogBuffer:
    """全局日志缓冲区，用于收集所有输出"""
    def __init__(self, max_lines: int = 1000, log_file: str = None, flush_interval: float = 5.0):
        self.buffer: List[str] = []
        self.max_lines = max_lines
        self.lock = threading.RLock()
        self.last_write_time = time.time()
        # 添加需要过滤的模式
        self.filter_pattern = '"GET /logs HTTP/1.1" 200 OK'
        
        # 文件持久化相关配置
        self.log_file = log_file
        self.flush_interval = flush_interval
        self.running = True
        self.unwritten_lines = 0  # 记录未写入文件的行数
        self.rolled_over = False  # 添加滚动标志
        self.max_file_lines = 10000  # 最大文件行数
        
        # 初始化日志优先级属性
        config_level = self._get_config_log_level()
        self.current_priority = LOG_LEVEL_PRIORITY.get(config_level.upper(), 2)
        
        # 如果指定了日志文件路径，则启动异步写入线程
        if self.log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 启动异步写入线程
            self.flush_thread = threading.Thread(target=self._async_flush_loop, daemon=True)
            self.flush_thread.start()
    
    def _check_and_roll_over(self):
        """检查文件行数并在需要时进行滚动"""
        if self.rolled_over or not self.log_file or not os.path.exists(self.log_file):
            return False
        
        try:
            # 计算当前文件的行数
            with open(self.log_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            # 如果行数超过阈值，执行滚动
            if line_count >= self.max_file_lines:
                # 生成带时间戳的新文件名
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                base_name, ext = os.path.splitext(self.log_file)
                rolled_filename = f"{base_name}_{timestamp}{ext}"
                
                # 重命名文件
                os.rename(self.log_file, rolled_filename)
                self.rolled_over = True  # 标记已滚动
                return True
        except Exception as e:
            # 记录错误但不影响程序运行
            print(f"[ERROR] Failed to roll over log file in LogBuffer: {e}", file=sys.stderr)
        return False
    
    def _flush_to_file_safe(self):
        """安全地将日志写入文件"""
        if not self.log_file or self.rolled_over:
            return
            
        try:
            if self.lock.acquire(timeout=0.5):
                try:
                    if self.unwritten_lines <= 0:
                        return
                    
                    # 检查是否需要滚动文件
                    self._check_and_roll_over()
                    
                    # 如果文件已滚动，不再写入
                    if self.rolled_over:
                        self.unwritten_lines = 0
                        return
                    
                    # 获取需要写入的日志行
                    lines_to_write = self.buffer[-self.unwritten_lines:]
                    
                    # 将日志写入文件
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        for line in lines_to_write:
                            f.write(line + '\n')
                    
                    # 重置未写入行数
                    self.unwritten_lines = 0
                finally:
                    self.lock.release()
        except Exception as e:
            # 记录错误但不影响程序运行
            print(f"[ERROR] Failed to write logs to file: {e}", file=sys.stderr)

    def _get_config_log_level(self) -> str:
        """从配置文件读取日志级别"""
        try:
            config = Config()
            conf_data = config.get()
            if 'log' in conf_data and 'log_level' in conf_data['log']:
                return conf_data['log']['log_level']
        except Exception as e:
            # 配置读取失败时使用默认值
            print(f"[ERROR] Failed to read log level from config: {e}", file=sys.stderr)
        return 'INFO'  # 默认日志级别
    
    def add(self, message: str):
        """添加日志到缓冲区，过滤特定模式和低于配置级别的日志，并为非格式化日志添加时间戳"""
        with self.lock:
            # 按行分割消息
            lines = message.split('\n')
            new_lines_added = 0
            for line in lines:
                line = line.strip()
                # 过滤含有指定模式的日志行
                if line and self.filter_pattern not in line:
                    # 检查是否已经包含时间戳格式 (YYYY-MM-DD HH:MM:SS)
                    if not self._has_timestamp(line):
                        # 为没有时间戳的日志行添加时间戳
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        # 尝试检测日志级别并添加合适的格式
                        level = self._detect_log_level(line)
                        line = f"{timestamp}  | {line}"
                    
                    # 检查日志级别是否大于等于配置的级别
                    log_level = self._detect_log_level(line)
                    log_priority = LOG_LEVEL_PRIORITY.get(log_level.upper(), 2)
                    
                    # 只添加大于等于配置级别的日志
                    if log_priority >= self.current_priority:
                        self.buffer.append(line)
                        new_lines_added += 1
            
            # 保持缓冲区大小在限制内
            if len(self.buffer) > self.max_lines:
                self.buffer = self.buffer[-self.max_lines:]
            
            # 更新未写入行数
            self.unwritten_lines += new_lines_added
            self.last_write_time = time.time()
            
            # 如果未写入行数达到一定阈值，立即触发写入
            if self.log_file and self.unwritten_lines >= 50:  # 阈值可以根据需要调整
                self._flush_to_file_safe()
    
    def _has_timestamp(self, line: str) -> bool:
        """检查日志行是否已经包含时间戳格式"""
        import re
        # 简单的时间戳格式检测: YYYY-MM-DD HH:MM:SS
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        return bool(re.match(timestamp_pattern, line))
    
    def _detect_log_level(self, line: str) -> str:
        """尝试从日志行中检测日志级别"""
        line_upper = line.upper()
        if 'ERROR' in line_upper:
            return 'ERROR'
        elif 'WARNING' in line_upper or 'WARN' in line_upper:
            return 'WARNING'
        elif 'INFO' in line_upper:
            return 'INFO'
        elif 'DEBUG' in line_upper:
            return 'DEBUG'
        elif 'CRITICAL' in line_upper or 'FATAL' in line_upper:
            return 'CRITICAL'
        else:
            return 'INFO'  # 默认级别
    
    def _flush_to_file_safe(self):
        """安全地将日志写入文件"""
        if not self.log_file:
            return
            
        try:
            if self.lock.acquire(timeout=0.5):
                try:
                    if self.unwritten_lines <= 0:
                        return
                        
                    # 获取需要写入的日志行
                    lines_to_write = self.buffer[-self.unwritten_lines:]
                    
                    # 将日志写入文件
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        for line in lines_to_write:
                            f.write(line + '\n')
                    
                    # 重置未写入行数
                    self.unwritten_lines = 0
                finally:
                    self.lock.release()
        except Exception as e:
            # 记录错误但不影响程序运行
            # 注意：这里不能使用log.error，避免循环引用
            print(f"[ERROR] Failed to write logs to file: {e}", file=sys.stderr)
    
    def _async_flush_loop(self):
        """异步写入循环"""
        while self.running:
            time.sleep(self.flush_interval)
            self._flush_to_file_safe()
    
    def flush_now(self):
        """立即将所有日志写入文件"""
        self._flush_to_file_safe()
    
    def close(self):
        """关闭日志缓冲区，确保所有日志都被写入"""
        # 设置运行标志为False
        self.running = False
        
        # 尝试关闭线程
        try:
            if hasattr(self, 'flush_thread') and self.flush_thread.is_alive():
                # 使用join，但设置超时避免无限等待
                self.flush_thread.join(timeout=1.0)
        except Exception:
            pass
        
        # 最后一次刷新，确保所有日志都被写入
        self._flush_to_file_safe()
    
    def get_all(self) -> str:
        """获取缓冲区所有内容"""
        with self.lock:
            return '\n'.join(self.buffer)
    
    def get_last_n(self, n: int) -> str:
        """获取缓冲区最后n行"""
        with self.lock:
            return '\n'.join(self.buffer[-n:])
    
    def clear(self):
        """清空缓冲区"""
        with self.lock:
            self.buffer = []


class RedirectedStdout(StringIO):
    """重定向标准输出到日志缓冲区"""
    def __init__(self, buffer: LogBuffer, original_stdout):
        super().__init__()
        self.buffer = buffer
        self.original_stdout = original_stdout
    
    def write(self, s: str):
        self.buffer.add(s)
        self.original_stdout.write(s)
        return len(s)
    
    def flush(self):
        self.original_stdout.flush()


class RedirectedStderr(StringIO):
    """重定向标准错误到日志缓冲区"""
    def __init__(self, buffer: LogBuffer, original_stderr):
        super().__init__()
        self.buffer = buffer
        self.original_stderr = original_stderr
    
    def write(self, s: str):
        self.buffer.add(s)
        self.original_stderr.write(s)
        return len(s)
    
    def flush(self):
        self.original_stderr.flush()


class BufferedFileHandler(logging.Handler):
    """带缓冲区的文件处理器"""
    def __init__(self, filename: str, flush_interval: float = 5.0):  # 修改为5秒
        super().__init__()
        self.filename = filename
        self.flush_interval = flush_interval
        self.buffer = []
        # 使用RLock替代Lock，避免在同一线程内的死锁问题
        self.lock = threading.RLock()
        self.last_flush = time.time()
        self.running = True
        self.rolled_over = False  # 添加滚动标志，标记文件是否已滚动
        self.max_lines = 10000  # 设置最大行数阈值
        
        # 确保目录存在
        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 设置标准的日志格式化器，确保时间戳格式一致
        self.formatter = logging.Formatter('%(asctime)s  | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # 启动异步写入线程
        self.flush_thread = threading.Thread(target=self._async_flush_loop, daemon=True)
        self.flush_thread.start()
        
        # 注册信号处理
        self._register_signal_handlers()
    
    def _check_and_roll_over(self):
        """检查文件行数并在需要时进行滚动"""
        if self.rolled_over or not os.path.exists(self.filename):
            return False
        
        try:
            # 计算当前文件的行数
            with open(self.filename, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            # 如果行数超过阈值，执行滚动
            if line_count >= self.max_lines:
                # 生成带时间戳的新文件名
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                base_name, ext = os.path.splitext(self.filename)
                rolled_filename = f"{base_name}_{timestamp}{ext}"
                
                # 重命名文件
                os.rename(self.filename, rolled_filename)
                self.rolled_over = True  # 标记已滚动
                return True
        except Exception as e:
            # 记录错误但不影响程序运行
            error_msg = f"[ERROR] Failed to roll over log file: {e}"
            print(error_msg, file=sys.stderr)
        return False
    
    def emit(self, record):
        # 如果文件已滚动，不再添加新的日志到缓冲区
        if self.rolled_over:
            return
            
        try:
            with self.lock:
                msg = self.format(record)
                self.buffer.append(msg)
                
                # 如果距离上次刷新超过指定时间，立即刷新
                current_time = time.time()
                if current_time - self.last_flush > self.flush_interval:
                    self._flush_to_file_safe()
        except Exception:
            # 即使发生异常，也不能影响程序运行
            pass
    
    def _flush_to_file_safe(self):
        """安全版本的文件刷新方法，添加异常处理和文件滚动检查"""
        # 如果文件已滚动，不再写入
        if self.rolled_over:
            self.buffer = []  # 清空缓冲区
            return
            
        try:
            # 尝试获取锁，如果失败则跳过
            if self.lock.acquire(timeout=0.5):
                try:
                    if not self.buffer:
                        return
                    
                    # 写入前检查是否需要滚动文件
                    self._check_and_roll_over()
                    
                    # 如果文件已滚动，不再写入
                    if self.rolled_over:
                        self.buffer = []  # 清空缓冲区
                        return
                    
                    # 将缓冲区内容写入文件
                    try:
                        with open(self.filename, 'a', encoding='utf-8') as f:
                            for line in self.buffer:
                                # 确保每条日志都包含时间戳
                                formatted_line = self._ensure_timestamp(line)
                                f.write(formatted_line + '\n')
                        self.buffer = []
                        self.last_flush = time.time()
                    except Exception as e:
                        # 如果写入失败，重新添加到缓冲区
                        if hasattr(self, 'buffer'):
                            error_msg = f"[ERROR] Failed to write log: {e}"
                            # 为错误信息添加时间戳
                            error_msg = self._ensure_timestamp(error_msg)
                            self.buffer.insert(0, error_msg)
                finally:
                    self.lock.release()
        except Exception:
            # 如果锁操作失败，记录错误但不崩溃
            pass
    
    def _register_signal_handlers(self):
        """注册信号处理器"""
        try:
            # 为优雅退出信号注册处理函数
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, OSError):
            # 在非主线程中可能无法设置信号处理器
            pass
    
    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        # 安全刷新缓冲区到文件
        self._flush_to_file_safe()
        # 继续传递信号，允许程序正常退出
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    
    def _ensure_timestamp(self, line: str) -> str:
        """确保日志行包含时间戳"""
        import re
        # 简单的时间戳格式检测: YYYY-MM-DD HH:MM:SS
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        if not re.match(timestamp_pattern, line):
            # 如果没有时间戳，添加当前时间
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            # 尝试检测日志级别
            level = 'INFO'
            line_upper = line.upper()
            for lvl in ['ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'CRITICAL', 'FATAL']:
                if lvl in line_upper:
                    level = lvl if lvl != 'WARN' else 'WARNING'
                    level = level if lvl != 'FATAL' else 'CRITICAL'
                    break
            line = f"{timestamp} - app - {level} - {line}"
        return line
    
    def _flush_to_file(self):
        """原始的刷新方法，已改为调用安全版本"""
        self._flush_to_file_safe()
    
    def _async_flush_loop(self):
        """异步刷新循环"""
        while self.running:
            time.sleep(self.flush_interval)
            self._flush_to_file_safe()
    
    def close(self):
        # 设置运行标志为False
        if hasattr(self, 'running'):
            self.running = False
        
        # 尝试关闭线程
        try:
            if hasattr(self, 'flush_thread') and self.flush_thread.is_alive():
                # 使用join，但设置超时避免无限等待
                self.flush_thread.join(timeout=1.0)
        except Exception:
            pass
        
        # 安全地刷新缓冲区
        self._flush_to_file_safe()
        
        # 调用父类的close方法
        try:
            super().close()
        except Exception:
            pass


# 创建全局日志缓冲区实例，指定日志文件路径
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/log.txt")
global_log_buffer = LogBuffer(max_lines=2000, log_file=log_file_path, flush_interval=5.0)


class Logos:
    def __init__(self, name: str = "logos", output_path: str = "./data/",
                 output_file: str = "log.txt", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.output_path = output_path
        self.output_file = output_file
        
        # 正确拼接文件路径
        log_file_path = os.path.join(output_path, output_file)
        
        # 如果全局日志缓冲区还没有指定日志文件，则设置它
        global global_log_buffer
        if not hasattr(global_log_buffer, 'log_file') or not global_log_buffer.log_file:
            global_log_buffer.log_file = log_file_path
        
        self.formatter = logging.Formatter('%(asctime)s  | %(message)s')
        
        # 清除已存在的处理器（避免重复添加）
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 检查输出目录是否存在，如果不存在则创建
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 添加带缓冲的文件处理器
        self.file_handler = BufferedFileHandler(log_file_path)
        self.file_handler.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s  | %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        
        # 添加控制台处理器，方便调试
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    # 修改向global_log_buffer添加日志的方法
    def info(self, message: str):
        self.logger.info(message)
        global_log_buffer.add(f"INFO: {message}")
    
    def error(self, message: str):
        self.logger.error(message)
        global_log_buffer.add(f"ERROR: {message}")
    
    def warning(self, message: str):
        self.logger.warning(message)
        global_log_buffer.add(f"WARNING: {message}")
    
    def debug(self, message: str):
        self.logger.debug(message)
        global_log_buffer.add(f"DEBUG: {message}")
    
    def critical(self, message: str):
        self.logger.critical(message)
        global_log_buffer.add(f"CRITICAL: {message}")
    
    def get_buffer_content(self, last_n: Optional[int] = None) -> str:
        """获取全局日志缓冲区内容"""
        if last_n is not None:
            return global_log_buffer.get_last_n(last_n)
        return global_log_buffer.get_all()
    
    def close(self):
        """关闭日志处理器"""
        if hasattr(self, 'file_handler'):
            self.file_handler.close()
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


def setup_global_redirect():
    """设置全局输出重定向"""
    # 保存原始的stdout和stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # 创建重定向器
    sys.stdout = RedirectedStdout(global_log_buffer, original_stdout)
    sys.stderr = RedirectedStderr(global_log_buffer, original_stderr)
    
    return original_stdout, original_stderr


def restore_redirect(original_stdout, original_stderr):
    """恢复原始输出"""
    sys.stdout = original_stdout
    sys.stderr = original_stderr


def get_global_log_buffer() -> LogBuffer:
    """获取全局日志缓冲区"""
    return global_log_buffer
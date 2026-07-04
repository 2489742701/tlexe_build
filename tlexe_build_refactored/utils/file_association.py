"""Windows 文件关联工具模块。

本模块提供注册和注销 .py 项目文件关联的功能。
注册后，双击项目 .py 文件即可启动程序并加载项目。

注意：
- 开发模式：注册 Python 解释器路径
- 打包后的便携版：不建议注册文件关联，因为程序可能被移动
- 安装版：可以在安装时注册文件关联
"""

import os
import sys
import platform

def is_windows() -> bool:
    return platform.system() == 'Windows'

def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)

def get_exe_path() -> str:
    if is_frozen():
        return sys.executable
    else:
        main_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
        return f'"{sys.executable}" "{main_py}"'

def can_register_file_association() -> tuple:
    if not is_windows():
        return False, "文件关联仅支持 Windows 系统"
    if is_frozen():
        return False, "便携版程序不建议注册文件关联。\n\n原因：程序移动后文件关联会失效。\n\n如需文件关联功能，请使用安装版程序。"
    return True, "可以注册文件关联"

def register_file_association() -> tuple:
    """注册 .py 项目文件关联。"""
    if not is_windows():
        return False, "文件关联仅支持 Windows 系统"

    try:
        import winreg

        exe_path = get_exe_path()
        app_name = "FoolDesktopTool"
        prog_id = "FoolDesktopTool.Project"

        file_types_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".itexe")
        winreg.SetValue(file_types_key, None, winreg.REG_SZ, prog_id)
        winreg.CloseKey(file_types_key)

        prog_id_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id)
        winreg.SetValue(prog_id_key, None, winreg.REG_SZ, "傻瓜桌面开发工具项目")
        winreg.CloseKey(prog_id_key)

        shell_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell")
        winreg.SetValue(shell_key, None, winreg.REG_SZ, "open")
        winreg.CloseKey(shell_key)

        open_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open")
        winreg.CloseKey(open_key)

        command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command")
        winreg.SetValue(command_key, None, winreg.REG_SZ, f'{exe_path} "%1"')
        winreg.CloseKey(command_key)

        default_icon_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\DefaultIcon")
        icon_path = exe_path.strip('"')
        winreg.SetValue(default_icon_key, None, winreg.REG_SZ, f'{icon_path},0')
        winreg.CloseKey(default_icon_key)

        try:
            app_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}")
            winreg.CloseKey(app_key)
        except Exception:
            pass

        return True, "文件关联注册成功！\n\n现在双击项目 .py 文件即可启动程序并加载。"

    except PermissionError:
        return False, "权限不足，请以管理员身份运行程序。"
    except Exception as e:
        return False, f"注册失败：{str(e)}"

def unregister_file_association() -> tuple:
    """注销项目文件关联。"""
    if not is_windows():
        return False, "文件关联仅支持 Windows 系统"

    try:
        import winreg

        prog_id = "FoolDesktopTool.Project"

        def delete_key_recursive(key, sub_key):
            try:
                full_key = winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
                while True:
                    try:
                        child = winreg.EnumKey(full_key, 0)
                        delete_key_recursive(full_key, child)
                    except OSError:
                        break
                winreg.CloseKey(full_key)
                parent_key = winreg.OpenKey(key, "", 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
                winreg.DeleteKey(parent_key, sub_key.split('\\')[-1] if '\\' in sub_key else sub_key)
                winreg.CloseKey(parent_key)
            except FileNotFoundError:
                pass

        delete_key_recursive(winreg.HKEY_CLASSES_ROOT, ".itexe")
        delete_key_recursive(winreg.HKEY_CLASSES_ROOT, prog_id)

        return True, "文件关联已注销。"

    except PermissionError:
        return False, "权限不足，请以管理员身份运行程序。"
    except Exception as e:
        return False, f"注销失败：{str(e)}"

def is_file_association_registered() -> bool:
    if not is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ".itexe")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

"""主题配置模块。

定义应用程序的颜色、字体等主题相关常量。
所有颜色使用十六进制格式，便于在CSS中使用。

## 颜色规范
- 主色调: #1a56db (蓝色)
- 成功色: #4CAF50 (绿色)
- 警告色: #ff9800 (橙色)
- 错误色: #e94560 (红色)
- 中性色: #666666 (灰色)
"""

class Colors:
    """颜色常量定义。
    
    所有颜色使用十六进制格式，可直接用于CSS样式。
    """
    
    # 主色调
    PRIMARY: str = "#1a56db"
    PRIMARY_LIGHT: str = "#e0e7ff"
    PRIMARY_DARK: str = "#1e40af"
    
    # 功能色
    SUCCESS: str = "#4CAF50"
    SUCCESS_LIGHT: str = "#e8f5e9"
    SUCCESS_DARK: str = "#388e3c"
    
    WARNING: str = "#ff9800"
    WARNING_LIGHT: str = "#fff3e0"
    
    ERROR: str = "#e94560"
    ERROR_LIGHT: str = "#ffebee"
    
    # 中性色
    WHITE: str = "#ffffff"
    BLACK: str = "#333333"
    GRAY_100: str = "#f5f5f5"
    GRAY_200: str = "#e0e0e0"
    GRAY_300: str = "#cccccc"
    GRAY_400: str = "#999999"
    GRAY_500: str = "#666666"
    GRAY_600: str = "#555555"
    
    # 边框色
    BORDER_LIGHT: str = "#c0c0c0"
    BORDER_FOCUS: str = "#4f6df5"
    
    # 背景色
    BACKGROUND_PRIMARY: str = "#ffffff"
    BACKGROUND_SECONDARY: str = "#f5f5f5"
    BACKGROUND_HOVER: str = "#f0f4ff"

class Fonts:
    """字体配置。
    
    定义应用程序使用的字体家族和大小。
    """
    
    # 字体家族
    FAMILY_PRIMARY: str = "Microsoft YaHei"
    FAMILY_MONOSPACE: str = "Consolas"
    
    # 字体大小
    SIZE_XS: int = 10
    SIZE_SM: int = 11
    SIZE_MD: int = 12
    SIZE_LG: int = 14
    SIZE_XL: int = 16
    SIZE_XXL: int = 18
    SIZE_TITLE: int = 24
    
    # 字体粗细
    WEIGHT_NORMAL: str = "normal"
    WEIGHT_BOLD: str = "bold"

class Theme:
    """主题配置类。
    
    提供主题相关的配置方法和工具函数。
    """
    
    # 当前主题模式
    DARK_MODE: bool = False
    
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """根据名称获取颜色值。
        
        Args:
            color_name: 颜色名称，如 'PRIMARY', 'SUCCESS' 等
            
        Returns:
            十六进制颜色值
        """
        return getattr(Colors, color_name.upper(), Colors.GRAY_500)
    
    @classmethod
    def get_font_family(cls) -> str:
        """获取主字体家族。
        
        Returns:
            字体家族名称
        """
        return Fonts.FAMILY_PRIMARY
    
    @classmethod
    def get_font_size(cls, size_name: str) -> int:
        """根据名称获取字体大小。
        
        Args:
            size_name: 大小名称，如 'XS', 'SM', 'MD', 'LG', 'XL'
            
        Returns:
            字体大小（像素）
        """
        return getattr(Fonts, f'SIZE_{size_name.upper()}', Fonts.SIZE_MD)
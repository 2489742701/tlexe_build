"""组件样式和工厂模块。

本模块提供统一的样式计算和运行时组件创建逻辑，
确保画布绘制和运行时控件显示一致。
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QCheckBox, QComboBox, QListWidget, QGroupBox, QProgressBar,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics

from models.base import ComponentModel
from models.schemas import StyleConfig
from models.components import (
    ButtonModel, LabelModel, InputModel, ContainerModel,
    CheckBoxModel, ComboBoxModel, ProgressBarModel,
    HiddenButtonModel, ImageButtonModel, ImageCarouselModel
)

class StyleHelper:
    """样式辅助类。
    
    提供统一的样式计算方法，供画布绘制和运行时控件使用。
    """
    
    @staticmethod
    def get_stylesheet(style: StyleConfig, extra_styles: str = "") -> str:
        """生成样式表字符串。
        
        Args:
            style: 样式配置对象
            extra_styles: 额外的样式字符串
            
        Returns:
            样式表字符串
        """
        if style.use_native_style:
            return ""
        
        style_parts = []
        
        if style.background_color and style.background_color != "transparent":
            style_parts.append(f"background-color: {style.background_color};")
        else:
            style_parts.append("background-color: transparent;")
        
        if style.text_color:
            style_parts.append(f"color: {style.text_color};")
        
        if style.border_color:
            border_width = style.border_width
            if border_width > 0:
                style_parts.append(f"border: {border_width}px solid {style.border_color};")
            else:
                style_parts.append("border: none;")
        
        if style.border_radius > 0:
            style_parts.append(f"border-radius: {style.border_radius}px;")
        
        if style.font_size:
            style_parts.append(f"font-size: {style.font_size}pt;")
        
        if style.font_bold:
            style_parts.append("font-weight: bold;")
        
        if extra_styles:
            style_parts.append(extra_styles)
        
        return "".join(style_parts)
    
    @staticmethod
    def apply_style(widget: QWidget, style: StyleConfig, extra_styles: str = ""):
        """应用样式到控件。
        
        Args:
            widget: 要应用样式的控件
            style: 样式配置对象
            extra_styles: 额外的样式字符串
        """
        if not style.use_native_style:
            stylesheet = StyleHelper.get_stylesheet(style, extra_styles)
            if stylesheet:
                widget.setStyleSheet(stylesheet)
        
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        widget.setFont(font)
    
    @staticmethod
    def get_font(style: StyleConfig) -> QFont:
        """获取字体对象。
        
        Args:
            style: 样式配置对象
            
        Returns:
            QFont 对象
        """
        font = QFont(style.font_family, style.font_size)
        font.setBold(style.font_bold)
        return font
    
    @staticmethod
    def is_native_style(style: StyleConfig) -> bool:
        """检查是否使用原生样式。
        
        Args:
            style: 样式配置对象
            
        Returns:
            True 表示使用原生样式，False 表示使用自定义样式
        """
        return style.use_native_style

class ComponentFactory:
    """组件工厂类。
    
    提供统一的运行时组件创建方法。
    """
    
    TITLE_BAR_HEIGHT = 28
    
    @staticmethod
    def _detect_text_squeeze(model: LabelModel) -> tuple[bool, tuple[int, int]]:
        """检测文本是否被挤压（基于MCP建议的优化版）。
        
        Args:
            model: 标签模型
            
        Returns:
            tuple[bool, tuple[int, int]]: (是否被挤压, (文本所需宽度, 文本所需高度))
        """
        # 防御性检查：空文本或无效尺寸
        if not model.text or model.width <= 0 or model.height <= 0:
            return False, (0, 0)
        
        # 限制文本长度，防止性能问题（基于MCP建议）
        MAX_TEXT_LENGTH = 10000
        text = model.text[:MAX_TEXT_LENGTH] if len(model.text) > MAX_TEXT_LENGTH else model.text
        
        try:
            # 创建字体对象
            font = QFont(model.style.font_family, model.style.font_size)
            font.setBold(model.style.font_bold)
            
            # 创建字体度量对象
            font_metrics = QFontMetrics(font)
            
            # 计算文本所需尺寸（基于像素宽度而非字符数，解决多语言问题）
            padding = 8  # 基础边距
            available_width = max(5, model.width - padding * 2)  # 最小5px防止换行爆炸
            
            if model.word_wrap:
                # 启用自动换行时，计算多行文本尺寸
                text_rect = font_metrics.boundingRect(
                    0, 0, available_width, 0,
                    Qt.TextWordWrap,
                    text
                )
            else:
                # 单行文本，计算单行尺寸
                text_rect = font_metrics.boundingRect(text)
            
            # 基于像素宽度的边距计算（解决多语言问题）
            text_pixel_width = text_rect.width()
            padding = max(8, min(16, int(text_pixel_width * 0.1)))  # 10%像素宽度，限制范围
            
            text_width = text_rect.width() + padding * 2
            text_height = text_rect.height() + padding * 2
            
            # 修正的挤压检测逻辑（移除错误的height < 0.8条件）
            is_squeezed = (
                text_height > model.height * 1.05 or  # 高度不足（105%阈值）
                text_width > model.width * 0.95       # 宽度不足（95%阈值）
            )
            
            return is_squeezed, (text_width, text_height)
            
        except Exception as e:
            # 异常处理：字体创建失败等情况
            print(f"文本挤压检测异常: {e}")
            return False, (0, 0)
    
    @staticmethod
    def _auto_adjust_label_size(model: LabelModel, text_width: int, text_height: int) -> LabelModel:
        """自动调整标签尺寸以避免文本挤压（基于MCP建议的直接调整版）。
        
        Args:
            model: 标签模型
            text_width: 文本所需宽度
            text_height: 文本所需高度
            
        Returns:
            调整后的标签模型
        """
        # 直接调整到所需尺寸（基于MCP建议，避免渐进式调整的低效）
        min_width = 50
        min_height = 20
        
        # 计算新尺寸，确保满足最小尺寸要求
        new_width = max(text_width, min_width)
        new_height = max(text_height, min_height)
        
        # 应用新尺寸
        model.width = new_width
        model.height = new_height
        
        return model
    
    @staticmethod
    def create_widget(model: ComponentModel) -> Optional[QWidget]:
        """根据模型创建对应的 Qt 控件（用于运行时）。
        
        查询优先级：
        1. ComponentRegistry.factory_func — 注册的工厂函数（推荐路径）
        2. 内置 _CREATORS 字典 — 向后兼容的静态分派（用于未完成迁移的插件）
        3. 返回 None

        新增组件只需在 registry_init.py 中注册 factory_func 即可，
        无需再修改此方法。
        
        Args:
            model: 组件数据模型
            
        Returns:
            创建的 Qt 控件，如果类型不支持则返回 None
        """
        comp_type = model.type
        
        # ── 路径 1：从 Registry 查询 factory_func（推荐路径） ──
        from models.component_registry import ComponentRegistry
        meta = ComponentRegistry.get_meta(comp_type)
        if meta and meta.factory_func:
            widget = meta.factory_func(model)
            if widget:
                widget.setProperty("component_id", model.id)
                widget.setProperty("component_type", comp_type)
            return widget
        
        # ── 路径 2：向后兼容的内置分派（插件或旧版 Registry 注册未提供 factory_func 时） ──
        import logging
        logging.getLogger(__name__).debug(
            f"组件类型 {comp_type!r} 未在 Registry 中注册 factory_func，"
            f"回退到内置 _CREATORS 字典"
        )
        creator = ComponentFactory._CREATORS.get(comp_type)
        if creator:
            widget = creator(model)
            if widget:
                widget.setProperty("component_id", model.id)
                widget.setProperty("component_type", comp_type)
            return widget
        
        return None
    
    # ── 向后兼容的内置分派表 ──────────────────────────────────────────────
    # 当某个组件在 Registry 中没有注册 factory_func 时（例如旧插件、
    # 或尚未完成迁移的代码），ComponentFactory 会在此处查找。
    # 
    # 新增组件不应修改此字典；请在 registry_init.py 里注册 factory_func。
    # 此字典仅作向后兼容保留，未来可能被移除。
    _CREATORS: dict = {}  # 将在类定义完成后填充（见文件末尾）
    
    @staticmethod
    def _create_button(model: ButtonModel) -> QPushButton:
        """创建按钮控件。"""
        button = QPushButton()
        button.setText(model.text or "按钮")
        button.resize(model.width, model.height)
        
        alignment = getattr(model, 'alignment', 'center')
        if alignment == 'left':
            extra = "text-align: left; padding-left: 10px;"
        elif alignment == 'right':
            extra = "text-align: right; padding-right: 10px;"
        else:
            extra = "text-align: center;"
        
        StyleHelper.apply_style(button, model.style, extra)
        return button
    
    @staticmethod
    def _create_label(model: LabelModel) -> QLabel:
        """创建标签控件。"""
        label = QLabel()
        label.setText(model.text or "文本")
        
        alignment_map = {
            'left': Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            'center': Qt.AlignmentFlag.AlignCenter,
            'right': Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            'top': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            'bottom': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        }
        label.setAlignment(alignment_map.get(model.alignment, Qt.AlignmentFlag.AlignCenter))
        label.setWordWrap(model.word_wrap)
        
        # 自动挤压检测和修复（当auto_size为false时）
        if not model.auto_size and model.text:
            is_squeezed, (text_width, text_height) = ComponentFactory._detect_text_squeeze(model)
            if is_squeezed:
                # 自动调整尺寸以避免文本挤压
                model = ComponentFactory._auto_adjust_label_size(model, text_width, text_height)
        
        # 自动调整大小：根据文本内容计算合适的大小
        if model.auto_size:
            label.adjustSize()
            # 更新模型的宽高
            model.width = label.width()
            model.height = label.height()
        else:
            label.resize(model.width, model.height)
        
        extra = ""
        if model.style.background_color == "transparent":
            extra = "background-color: transparent;"
        
        StyleHelper.apply_style(label, model.style, extra)
        
        return label
    
    @staticmethod
    def _create_input(model: InputModel) -> QLineEdit:
        """创建输入框控件。"""
        line_edit = QLineEdit()
        line_edit.setText(model.text or "")
        line_edit.setPlaceholderText(model.placeholder or "")
        line_edit.setMaxLength(model.max_length)
        line_edit.resize(model.width, model.height)
        
        if model.is_password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        StyleHelper.apply_style(line_edit, model.style)
        return line_edit
    
    @staticmethod
    def _create_textarea(model: InputModel) -> QTextEdit:
        """创建多行文本框控件。"""
        text_edit = QTextEdit()
        text_edit.setPlainText(model.text or "")
        text_edit.setPlaceholderText(model.placeholder or "")
        text_edit.resize(model.width, model.height)
        StyleHelper.apply_style(text_edit, model.style)
        return text_edit
    
    @staticmethod
    def _create_checkbox(model: CheckBoxModel) -> QCheckBox:
        """创建复选框控件。"""
        checkbox = QCheckBox()
        checkbox.setText(model.text or "复选框")
        checkbox.setChecked(model.checked)
        checkbox.resize(model.width, model.height)
        
        alignment = getattr(model, 'alignment', 'left')
        if alignment == 'left':
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { padding-left: 5px; }")
        elif alignment == 'right':
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { padding-right: 5px; }")
        elif alignment == 'center':
            checkbox.setStyleSheet(checkbox.styleSheet() + "QCheckBox { padding-left: 0px; }")
        
        StyleHelper.apply_style(checkbox, model.style)
        return checkbox
    
    @staticmethod
    def _create_combobox(model: ComboBoxModel) -> QComboBox:
        """创建下拉框控件。"""
        combo = QComboBox()
        items = model.items or []
        combo.addItems(items)
        if model.current_index >= 0 and model.current_index < len(items):
            combo.setCurrentIndex(model.current_index)
        combo.resize(model.width, model.height)
        StyleHelper.apply_style(combo, model.style)
        return combo
    
    @staticmethod
    def _create_listwidget(model) -> QListWidget:
        """创建列表控件。"""
        list_widget = QListWidget()
        items = getattr(model, 'items', []) or []
        list_widget.addItems(items)
        list_widget.resize(model.width, model.height)
        StyleHelper.apply_style(list_widget, model.style)
        return list_widget
    
    @staticmethod
    def _create_groupbox(model) -> QGroupBox:
        """创建分组框控件。"""
        group_box = QGroupBox()
        group_box.setTitle(model.text or "")
        group_box.resize(model.width, model.height)
        StyleHelper.apply_style(group_box, model.style)
        return group_box
    
    @staticmethod
    def _create_container(model: ContainerModel) -> QWidget:
        """创建容器控件。"""
        from PySide6.QtWidgets import QFrame
        
        container = QFrame()
        container.resize(model.width, model.height)
        
        if model.style.use_native_style:
            container.setFrameStyle(QFrame.Shape.StyledPanel)
        else:
            style = model.style
            bg_color = style.background_color if style.background_color != "transparent" else "#ffffff"
            border_radius = style.border_radius
            
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid #cccccc;
                    border-radius: {border_radius}px;
                }}
            """)
        
        return container
    
    @staticmethod
    def _create_progressbar(model: ProgressBarModel) -> QProgressBar:
        """创建进度条控件。"""
        progressbar = QProgressBar()
        progressbar.resize(model.width, model.height)
        progressbar.setValue(model.value)
        
        if model.show_text:
            progressbar.setFormat("%p%")
        else:
            progressbar.setTextVisible(False)
        
        StyleHelper.apply_style(progressbar, model.style)
        return progressbar
    
    @staticmethod
    def _create_hidden_button(model: HiddenButtonModel) -> QPushButton:
        """创建隐藏按钮（透明但可点击）。"""
        button = QPushButton()
        button.setText("")
        button.resize(model.width, model.height)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.1);
            }
        """)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button
    
    @staticmethod
    def _create_image_button(model: ImageButtonModel) -> QPushButton:
        """创建图片按钮。"""
        from PySide6.QtGui import QIcon, QPixmap
        
        button = QPushButton()
        button.setText("")
        button.resize(model.width, model.height)
        
        image_path = getattr(model, 'image_path', '')
        if image_path:
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    button.setIcon(icon)
                    button.setIconSize(pixmap.size())
            except Exception:
                pass
        
        StyleHelper.apply_style(button, model.style)
        return button
    
    @staticmethod
    def _create_image_carousel(model: ImageCarouselModel) -> QWidget:
        """创建图片轮播控件。"""
        from PySide6.QtWidgets import QLabel, QVBoxLayout
        from PySide6.QtGui import QPixmap
        
        container = QWidget()
        container.resize(model.width, model.height)
        container.setProperty("component_model", model)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        images = getattr(model, 'images', [])
        current_index = getattr(model, 'current_index', 0)
        image_labels = getattr(model, 'image_labels', [])
        
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if images and 0 <= current_index < len(images):
            image_path = images[current_index]
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        model.width - 10, model.height - 30,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    label.setPixmap(scaled_pixmap)
                else:
                    display_text = image_labels[current_index] if current_index < len(image_labels) else f"图片{current_index + 1}"
                    label.setText(display_text)
            except Exception:
                display_text = image_labels[current_index] if current_index < len(image_labels) else "加载失败"
                label.setText(display_text)
        elif image_labels:
            label.setText(image_labels[0])
        else:
            label.setText("图片轮播")
        
        layout.addWidget(label)
        
        indicator_label = QLabel()
        indicator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if images:
            indicator_label.setText(f"{current_index + 1} / {len(images)}")
        layout.addWidget(indicator_label)
        
        StyleHelper.apply_style(container, model.style)
        
        return container
    
    @staticmethod
    def _create_image(model) -> QWidget:
        """创建图片控件。"""
        from PySide6.QtWidgets import QLabel
        from PySide6.QtGui import QPixmap
        
        label = QLabel()
        label.resize(model.width, model.height)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_path = getattr(model, 'image_path', '')
        if image_path:
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        model.width, model.height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    label.setPixmap(scaled_pixmap)
                else:
                    label.setText(getattr(model, 'placeholder_text', '') or "图片")
            except Exception:
                label.setText(getattr(model, 'placeholder_text', '') or "加载失败")
        else:
            label.setText(getattr(model, 'placeholder_text', '') or "图片")
        
        StyleHelper.apply_style(label, model.style)
        return label
    
    @staticmethod
    def _create_video(model) -> QWidget:
        """创建视频控件。"""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton
        from PySide6.QtMultimedia import QMediaPlayer
        from PySide6.QtMultimediaWidgets import QVideoWidget
        
        container = QWidget()
        container.resize(model.width, model.height)
        container.setProperty("component_model", model)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        video_widget = None
        media_player = None
        
        try:
            video_widget = QVideoWidget()
            video_widget.setMinimumSize(model.width, max(model.height - 40, 60))
            layout.addWidget(video_widget)
            
            media_player = QMediaPlayer()
            media_player.setVideoOutput(video_widget)
            
            video_path = getattr(model, 'video_path', '')
            if video_path:
                from PySide6.QtCore import QUrl
                media_player.setSource(QUrl.fromLocalFile(video_path))
            
            controls = QHBoxLayout()
            controls.setSpacing(10)
            
            play_btn = QPushButton("Play")
            play_btn.setFixedWidth(60)
            play_btn.clicked.connect(lambda: media_player.play() if media_player else None)
            controls.addWidget(play_btn)
            
            stop_btn = QPushButton("Stop")
            stop_btn.setFixedWidth(60)
            stop_btn.clicked.connect(lambda: media_player.pause() if media_player else None)
            controls.addWidget(stop_btn)
            
            controls.addStretch()
            layout.addLayout(controls)
            
            container._media_player = media_player
            
        except (ImportError, AttributeError) as e:
            fallback_label = QLabel("[Video requires PySide6 multimedia]")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_label.setStyleSheet("background-color: #1a1a1a; color: #fff; padding: 20px;")
            layout.addWidget(fallback_label)
        
        StyleHelper.apply_style(container, model.style)
        return container
    
    @staticmethod
    def _create_confirm_button(model) -> QWidget:
        """创建确认按钮控件。"""
        from PySide6.QtWidgets import QPushButton
        button = QPushButton()
        button.setText(model.text or "确认")
        button.resize(model.width, model.height)
        button.setProperty("component_model", model)
        
        is_confirmed = getattr(model, 'is_confirmed', False)
        if is_confirmed:
            button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px;")
        else:
            StyleHelper.apply_style(button, model.style)
        return button
    
    @staticmethod
    def _create_alternating(model) -> QWidget:
        """创建交替变换控件（文字/图片通用）。"""
        placeholder = "文字交替变换" if getattr(model, 'display_mode', 'text') == 'text' else "图片交替变换"
        return ComponentFactory._create_item_switcher(model, placeholder)

    @staticmethod
    def _create_group_node(model) -> 'QFrame':
        """创建组节点控件。"""
        from PySide6.QtWidgets import QFrame

        frame = QFrame()
        frame.resize(model.width, model.height)

        show_border = getattr(model, 'show_border', True)
        if show_border:
            border_style = getattr(model, 'border_style', 'dashed')
            border_map = {
                'solid': 'solid',
                'dashed': 'dashed',
                'dotted': 'dotted',
                'none': 'none',
            }
            bs = border_map.get(border_style, 'dashed')
            bg = getattr(model.style, 'background_color', 'transparent')
            br = getattr(model.style, 'border_radius', 5)
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px {bs} #999999;
                    border-radius: {br}px;
                }}
            """)
        else:
            frame.setStyleSheet("background-color: transparent; border: none;")

        return frame

    @staticmethod
    def _create_item_switcher(model, placeholder: str = "") -> QWidget:
        """创建候选项切换控件（交替变换/抽奖共用）。

        根据 display_mode 分派文字大字或图片显示，
        底部绘制指示器圆点。
        连接模型的 current_index_changed 信号实现动画时实时刷新。
        toggle_mode='same' 时开始/停止共用一个按钮。
        """
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton
        from PySide6.QtCore import Qt

        container = QWidget()
        container.resize(model.width, model.height)
        container.setProperty("component_model", model)

        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        display_container = QWidget()
        display_container.setProperty("component_model", model)
        display_layout = QVBoxLayout(display_container)
        display_layout.setContentsMargins(5, 5, 5, 5)

        display_label = QLabel()
        display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_label.setMinimumHeight(model.height - 40)

        display_mode = getattr(model, 'display_mode', 'text')
        items = getattr(model, 'items', [])
        item_labels = getattr(model, 'item_labels', [])
        current_index = getattr(model, 'current_index', 0)
        toggle_mode = getattr(model, 'toggle_mode', 'same')

        def _build_text_style(m) -> str:
            s = getattr(m, 'style', None)
            if s is None:
                return "font-size: 28pt; font-weight: bold; color: #333333;"
            bold = "bold" if s.font_bold else "normal"
            return f"font-size: {s.font_size}pt; font-weight: {bold}; color: {s.text_color};"

        def _update_display():
            idx = getattr(model, 'current_index', 0)
            itms = getattr(model, 'items', [])
            lbls = getattr(model, 'item_labels', [])
            dm = getattr(model, 'display_mode', 'text')
            running = getattr(model, 'is_running', False)
            if items and 0 <= idx < len(items):
                if dm == 'text':
                    text = lbls[idx] if idx < len(lbls) else str(itms[idx])
                    display_label.setText(text)
                    display_label.setStyleSheet(_build_text_style(model))
                else:
                    from PySide6.QtGui import QPixmap
                    pixmap = QPixmap(itms[idx])
                    if not pixmap.isNull():
                        display_label.setPixmap(pixmap.scaled(
                            display_container.width() - 2, display_container.height() - 2,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        ))
                    else:
                        text = lbls[idx] if idx < len(lbls) else "图片加载失败"
                        display_label.setText(text)

        if items and 0 <= current_index < len(items):
            if display_mode == 'text':
                text = item_labels[current_index] if current_index < len(item_labels) else str(items[current_index])
                display_label.setText(text)
                display_label.setStyleSheet(_build_text_style(model))
            else:
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap(items[current_index])
                if not pixmap.isNull():
                    display_label.setPixmap(pixmap.scaled(
                        model.width - 10, model.height - 40,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))
                else:
                    text = item_labels[current_index] if current_index < len(item_labels) else "图片加载失败"
                    display_label.setText(text)
        else:
            display_label.setText(placeholder or "候选项切换")
            if display_mode == 'text':
                display_label.setStyleSheet(_build_text_style(model))

        display_layout.addWidget(display_label)

        # 只需要一个边框描边
        display_container.setStyleSheet("border: 1px solid #999999; background-color: transparent;")

        StyleHelper.apply_style(display_container, model.style)

        outer_layout.addWidget(display_container, stretch=1)

        if hasattr(model, 'current_index_changed'):
            model.current_index_changed.connect(lambda: _update_display())

        container._display_label = display_label

        return container
    
    @staticmethod
    def update_widget(widget: QWidget, model: ComponentModel):
        """更新控件属性。
        
        查询优先级：
        1. ComponentRegistry.update_func — 注册的更新函数（推荐路径）
        2. 内置 elif 链 — 向后兼容（未注册 update_func 时）
        
        Args:
            widget: 要更新的控件
            model: 新的组件模型
        """
        comp_type = model.type
        
        # ── 路径 1：从 Registry 查询 update_func ──
        from models.component_registry import ComponentRegistry
        meta = ComponentRegistry.get_meta(comp_type)
        if meta and meta.update_func:
            meta.update_func(widget, model)
            widget.resize(model.width, model.height)
            return
        
        # ── 路径 2：内置 elif 链（向后兼容） ──
        if comp_type == 'button':
            widget.setText(model.text or "按钮")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'label':
            widget.setText(model.text or "文本")
            alignment_map = {
                'left': Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                'center': Qt.AlignmentFlag.AlignCenter,
                'right': Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                'top': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                'bottom': Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            }
            widget.setAlignment(alignment_map.get(model.alignment, Qt.AlignmentFlag.AlignCenter))
            widget.setWordWrap(model.word_wrap)
            
            extra = ""
            if model.style.background_color == "transparent":
                extra = "background-color: transparent;"
            
            StyleHelper.apply_style(widget, model.style, extra)
        elif comp_type == 'checkbox':
            widget.setText(model.text or "复选框")
            widget.setChecked(model.checked)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'combobox':
            widget.clear()
            items = model.items or []
            widget.addItems(items)
            if model.current_index >= 0 and model.current_index < len(items):
                widget.setCurrentIndex(model.current_index)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'progressbar':
            widget.setValue(model.value)
            widget.setTextVisible(model.show_text)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'input':
            widget.setText(model.text or "")
            widget.setPlaceholderText(model.placeholder or "")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'textarea':
            widget.setPlainText(model.text or "")
            widget.setPlaceholderText(model.placeholder or "")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'container':
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'listwidget':
            widget.clear()
            items = getattr(model, 'items', []) or []
            widget.addItems(items)
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'groupbox':
            widget.setTitle(getattr(model, 'text', "") or "")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'hidden_button':
            pass
        elif comp_type == 'image_button':
            from PySide6.QtGui import QIcon, QPixmap
            image_path = getattr(model, 'image_path', '')
            if image_path:
                try:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        widget.setIcon(QIcon(pixmap))
                except Exception:
                    pass
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'image':
            from PySide6.QtGui import QPixmap
            image_path = getattr(model, 'image_path', '')
            if image_path:
                try:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(
                            model.width, model.height,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        widget.setPixmap(scaled)
                except Exception:
                    widget.setText(getattr(model, 'placeholder_text', '') or "图片")
            else:
                widget.setText(getattr(model, 'placeholder_text', '') or "图片")
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'video':
            StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'image_carousel':
            StyleHelper.apply_style(widget, model.style)
        elif comp_type in ('lottery', 'text_alternating', 'image_alternating'):
            has_update = getattr(widget, '_update_display', None)
            if has_update:
                has_update()
        elif comp_type == 'confirm_button':
            is_confirmed = getattr(model, 'is_confirmed', False)
            if is_confirmed:
                widget.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px;")
            else:
                StyleHelper.apply_style(widget, model.style)
        elif comp_type == 'group_node':
            show_border = getattr(model, 'show_border', True)
            if show_border:
                border_style = getattr(model, 'border_style', 'dashed')
                bs_map = {'solid': 'solid', 'dashed': 'dashed', 'dotted': 'dotted', 'none': 'none'}
                bs = bs_map.get(border_style, 'dashed')
                bg = getattr(model.style, 'background_color', 'transparent')
                br = getattr(model.style, 'border_radius', 5)
                widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg};
                        border: 1px {bs} #999999;
                        border-radius: {br}px;
                    }}
                """)
            else:
                widget.setStyleSheet("background-color: transparent; border: none;")
        
        widget.resize(model.width, model.height)

def create_component_widget(model: ComponentModel) -> Optional[QWidget]:
    """便捷函数：创建运行时组件控件。
    
    Args:
        model: 组件数据模型
        
    Returns:
        创建的 Qt 控件
    """
    return ComponentFactory.create_widget(model)

def update_component_widget(widget: QWidget, model: ComponentModel):
    """便捷函数：更新组件控件。
    
    Args:
        widget: 要更新的控件
        model: 新的组件模型
    """
    ComponentFactory.update_widget(widget, model)

# ─────────────────────────────────────────────────────────────────────────────
# 向后兼容：填充 ComponentFactory._CREATORS
#
# 当组件在 ComponentRegistry 中没有注册 factory_func 时（例如旧插件），
# ComponentFactory.create_widget 会在这里查找。
# 新增内置组件请在 models/registry_init.py 里注册 factory_func，而不是修改这里。
# ─────────────────────────────────────────────────────────────────────────────
ComponentFactory._CREATORS = {
    'button':            ComponentFactory._create_button,
    'label':             ComponentFactory._create_label,
    'input':             ComponentFactory._create_input,
    'textarea':          ComponentFactory._create_textarea,
    'checkbox':          ComponentFactory._create_checkbox,
    'combobox':          ComponentFactory._create_combobox,
    'listwidget':        ComponentFactory._create_listwidget,
    'groupbox':          ComponentFactory._create_groupbox,
    'container':         ComponentFactory._create_container,
    'progressbar':       ComponentFactory._create_progressbar,
    'hidden_button':     ComponentFactory._create_hidden_button,
    'image_button':      ComponentFactory._create_image_button,
    'image_carousel':    ComponentFactory._create_image_carousel,
    'alternating':       ComponentFactory._create_alternating,
    'confirm_button':    ComponentFactory._create_confirm_button,
    'image':             ComponentFactory._create_image,
    'video':             ComponentFactory._create_video,
    'group_node':        ComponentFactory._create_group_node,
}

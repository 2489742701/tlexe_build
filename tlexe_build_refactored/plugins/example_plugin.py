# 这是一个示例插件文件，演示如何创建第三方组件扩展。
#
# 使用方式：
#   1. 将此文件复制并重命名（例如 my_rating_widget.py）
#   2. 删除示例代码，替换为你的组件定义
#   3. 将文件放入此 plugins/ 目录
#   4. 重启应用，组件将自动注册到 ComponentRegistry
#
# 无需修改任何主程序代码。

# 示例：一个五星评分组件
# （取消下面的注释并修改以创建真实组件）
#
# from models.component_registry import register_component
# from models.base import ComponentModel, SignalProperty
#
# @register_component(
#     'star_rating',
#     display_name='五星评分',
#     icon='⭐',
#     category='input',
#     description='可点击的五星评分组件',
#     default_props={'width': 150, 'height': 30},
# )
# class StarRatingModel(ComponentModel):
#     """五星评分组件模型。"""
#
#     max_stars: int = SignalProperty(5)
#     current_stars: int = SignalProperty(0)
#     allow_half: bool = SignalProperty(False)
#
#     def __init__(self, **kwargs):
#         kwargs.setdefault('comp_type', 'star_rating')
#         kwargs.setdefault('name', '星级评分')
#         kwargs.setdefault('width', 150)
#         kwargs.setdefault('height', 30)
#         super().__init__(**kwargs)

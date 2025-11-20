from PIL import Image, ImageDraw, ImageFont
import os

from utils.log import Logos
import hashlib


class CertificateGenerator:
    def __init__(self, log:Logos, resource_paths:dict[str, str], output_folder:str, chinese_font_path:str = "resource/fonts/FangSong.ttf", english_font_path:str = "resource/fonts/Times New Roman.ttf"):
        self.resource_paths = resource_paths
        self.chinese_font_path = chinese_font_path
        self.english_font_path = english_font_path
        self.output_folder = output_folder
        self.log = log
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    @staticmethod
    def _draw_bold_text(draw, position, text, font, fill=(0, 0, 0), bold_level=2):
        """绘制加粗文字
        Args:
            draw: ImageDraw对象
            position: (x, y) 文字位置
            text: 要绘制的文字
            font: 字体对象
            fill: 颜色
            bold_level: 加粗级别(1-3)
        """
        x, y = position
        for offset in range(1, bold_level+1):
            draw.text((x+offset, y+offset), text, fill=fill, font=font)
        draw.text((x, y), text, fill=fill, font=font)

    @staticmethod
    def _draw_centered_text(draw, x_range, y_pos, text, font, fill=(0, 0, 0),
                            bold=False, stroke_width=2, stroke_fill=(0, 0, 0)):
        """绘制居中对齐文字
        Args:
            x_range: (left, right) 左右边界坐标
            bold: 是否加粗
            stroke_width: 描边宽度
            stroke_fill: 描边颜色
        Raises:
            ValueError: 当文本过长且字体小于24时抛出
        """
        while True:
            text_width = draw.textlength(text, font=font)
            left, right = x_range
            x_pos = left + (right - left - text_width) // 2
            if text_width <= right - left:
                break
            # 缩小字体大小
            font_size = font.size - 1
            if font_size < 24:  # 添加最小字体检查
                raise ValueError(f"文本过长无法适应区域: '{text}' (最小字体24px)")
            font = ImageFont.truetype(font.path, font_size)
            y_pos = y_pos + 1

        # 绘制黑色描边
        if stroke_width > 0:
            for offset_x in range(-stroke_width, stroke_width + 1):
                for offset_y in range(-stroke_width, stroke_width + 1):
                    draw.text((x_pos + offset_x, y_pos + offset_y), text, fill=stroke_fill, font=font)
        
        if bold:
            for offset in range(1, 3):
                draw.text((x_pos + offset, y_pos + offset), text, fill=fill, font=font)
        draw.text((x_pos, y_pos), text, fill=fill, font=font)

    @staticmethod
    def _draw_text(draw, position, text, font, fill=(0, 0, 0), bold=False):
        x, y = position
        draw.text((x, y), text, fill=fill, font=font)

    def generate_meme(self, resource:str , text:str):
        # 对resource和text字段进行MD5哈希处理
        resource_hash = hashlib.md5(resource.encode('utf-8')).hexdigest()
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        # 使用哈希值作为文件名
        output_path = os.path.join(self.output_folder, f"shyeri_meme_{resource_hash}_{text_hash}.jpg")
        background_path = self.resource_paths.get(resource)
        if not background_path:
            self.log.error(f"资源{resource}不存在")
            raise ValueError(f"资源{resource}不存在")
        # 打开背景图片并转换为RGB模式
        background = Image.open(background_path).convert('RGB')
        draw = ImageDraw.Draw(background)

        # 修改字体设置
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_dir= os.path.dirname(script_dir)
            font_path = os.path.join(script_dir, self.chinese_font_path)
            font = ImageFont.truetype(font_path, size=90)
        except Exception as e:
            self.log.error(f"绘制meme {resource}_{text} 时加载字体失败: {e}; 使用默认字体")
            font = ImageFont.load_default(size=90)
        try:
            # 使用白色文字带黑色描边
            self._draw_centered_text(draw, (50, 750), 650, text, font, fill=(255, 255, 255), bold=False, stroke_width=6, stroke_fill=(0, 0, 0))
        except Exception as e:
            raise e

        # 保存为JPEG格式
        background.save(output_path, format='JPEG', quality=95)

        # 返回生成的文件名，以便在API中使用
        return f"shyeri_meme_{resource_hash}_{text_hash}.jpg"
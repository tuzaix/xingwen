import os
from io import BytesIO
from typing import Dict, Any, List
import logging
import markdown
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, Table, TableStyle, Image
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

# 获取中文字体路径
def get_chinese_font_path():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 优先使用更现代、具有苹果设计美感的 OPPOSans (苹果化、极简、高端)
    oppo_regular = os.path.join(current_dir, "assets", "fonts", "OPPOSans-Regular.ttf")
    oppo_bold = os.path.join(current_dir, "assets", "fonts", "OPPOSans-Bold.ttf")
    if os.path.exists(oppo_regular) and os.path.exists(oppo_bold):
        return (oppo_regular, oppo_bold), "OPPOSans"
    
    # 备选使用 文艺感较强的 霞鹜文楷
    lxgw_font = os.path.join(current_dir, "assets", "fonts", "LXGWWenKaiScreen.ttf")
    if os.path.exists(lxgw_font):
        return (lxgw_font, lxgw_font), "LXGWWenKai"
    
    # 最后备选 思源黑体
    source_han_font = os.path.join(current_dir, "assets", "fonts", "SourceHanSansSC-Regular.otf")
    if os.path.exists(source_han_font):
        return (source_han_font, source_han_font), "SourceHanSans"
    
    return None, None

# 注册字体
font_info, font_family_name = get_chinese_font_path()
CHINESE_FONT_NAME = 'STSong-Light'

try:
    if font_info and font_family_name:
        reg_font_path, bold_font_path = font_info
        pdfmetrics.registerFont(TTFont(font_family_name, reg_font_path))
        
        # 额外注册一个粗体别名
        bold_font_name = f"{font_family_name}-Bold"
        pdfmetrics.registerFont(TTFont(bold_font_name, bold_font_path))
        
        # 注册字体族
        pdfmetrics.registerFontFamily(font_family_name, normal=font_family_name, bold=bold_font_name, italic=font_family_name, boldItalic=bold_font_name)
        CHINESE_FONT_NAME = font_family_name
        logger.info(f"Successfully registered font family {font_family_name} with bold support")
    else:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        CHINESE_FONT_NAME = 'STSong-Light'
        logger.warning("Using fallback font STSong-Light")
except Exception as e:
    logger.error(f"Font registration failed: {e}")
    # 最后的兜底
    try:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        CHINESE_FONT_NAME = 'STSong-Light'
    except:
        CHINESE_FONT_NAME = 'Helvetica'

def draw_header_footer(canvas, doc, report_data):
    canvas.saveState()
    
    # 页脚
    canvas.setFont(CHINESE_FONT_NAME, 9)
    canvas.setStrokeColor(colors.lightgrey)
    canvas.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
    footer_text = "© 2024 星纹 AI · 本报告由星纹全息命理系统生成，仅供参考"
    canvas.drawCentredString(A4[0]/2, 1*cm, footer_text)
    
    # 页码
    page_num = canvas.getPageNumber()
    canvas.drawRightString(19*cm, 1*cm, f"第 {page_num} 页")
    
    canvas.restoreState()

def generate_report_pdf(report_data: Dict[str, Any]) -> BytesIO:
    """
    使用 ReportLab 直接生成 PDF，解决 CJK 换行和排版问题
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    
    # 定义样式
    def get_bold_font():
        if CHINESE_FONT_NAME in ['SourceHanSans', 'LXGWWenKai', 'OPPOSans']:
            return f"{CHINESE_FONT_NAME}-Bold"
        return CHINESE_FONT_NAME

    title_style = ParagraphStyle(
        'ReportTitle',
        fontName=get_bold_font(),
        fontSize=26,
        leading=32,
        alignment=1, # Center
        spaceAfter=10,
        textColor=colors.HexColor('#1e293b')
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        fontName=CHINESE_FONT_NAME,
        fontSize=11,
        leading=14,
        alignment=1, # Center
        spaceAfter=30,
        textColor=colors.HexColor('#64748b')
    )
    
    h2_style = ParagraphStyle(
        'ChapterTitle',
        fontName=get_bold_font(),
        fontSize=18,
        leading=24,
        leftIndent=0,
        firstLineIndent=0,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.HexColor('#1e293b'),
        borderPadding=(0, 0, 0, 10),
        borderLeftColor=colors.HexColor('#fbbf24'),
        borderLeftWidth=5
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        fontName=CHINESE_FONT_NAME,
        fontSize=11,
        leading=18,
        firstLineIndent=22, # 2em (approx for 11pt)
        alignment=0, # Left
        spaceAfter=12,
        wordWrap='CJK' # 核心设置：支持中文字符换行
    )
    
    info_style = ParagraphStyle(
        'InfoText',
        fontName=get_bold_font(),
        fontSize=10,
        leading=14,
        spaceAfter=5,
        textColor=colors.HexColor('#334155')
    )
    
    highlight_style = ParagraphStyle(
        'HighlightTag',
        fontName=CHINESE_FONT_NAME,
        fontSize=10,                           # 统一使用 9pt
        leading=12,
        textColor=colors.HexColor('#92400e'), # 沉稳的古铜金，更具高级感
        backColor=colors.HexColor('#fffbeb'), # 柔和的香槟底色
        borderPadding=(2, 7, 2, 7),           # 比例适中的内边距
        borderRadius=3,                       # 适度的微圆角
        spaceAfter=0,
        wordWrap=None,                        # 强制不换行
        splitLongWords=False,                 # 禁止拆分长单词/字符
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        alignment=0                           # 左对齐
    )

    elements = []

    # 1. 标题
    elements.append(Paragraph("<b>星纹全息命理深度解析报告</b>", title_style))
    elements.append(Paragraph("星纹 AI 手相命理解析系统", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#fbbf24'), spaceAfter=20))

    # 2. 用户信息与手相照片对照
    info_items = [
        f"<b>姓名：</b>{report_data.get('user_name', '未知')}",
        f"<b>性别：</b>{report_data.get('gender', '未知')}",
        f"<b>生日：</b>{report_data.get('birthday', '未知')}",
        f"<b>核心诉求：</b>{report_data.get('focus_area', '全面解析')}"
    ]
    
    # 准备左侧文字内容
    info_paragraphs = [Paragraph(f"<b>{item}</b>", info_style) for item in info_items]
    
    # 准备右侧图片内容
    hand_images = []
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
    
    for side in ['left', 'right']:
        img_path = report_data.get(f'{side}_hand_image')
        if img_path:
            # 转换为本地绝对路径
            full_path = os.path.join(os.path.dirname(current_dir), img_path.lstrip('/'))
            if os.path.exists(full_path):
                try:
                    img = Image(full_path, width=2.5*cm, height=3.5*cm)
                    hand_images.append(img)
                except Exception as e:
                    logger.error(f"Failed to load hand image {full_path}: {e}")

    # 使用表格布局：左侧文字，右侧图片
    # 构建表格数据
    text_col = info_paragraphs
    img_col = hand_images if hand_images else [Paragraph("", info_style)]
    
    # 左右手各占一个位置，如果只有一个手则只展示一个
    img_table_data = []
    if len(hand_images) >= 2:
        img_table_data = [[hand_images[0], hand_images[1]]]
    elif len(hand_images) == 1:
        img_table_data = [[hand_images[0], ""]]
    
    # 主布局表格：左侧是用户信息文字，右侧是手相图片子表
    inner_img_table = Table(img_table_data, colWidths=[2.8*cm, 2.8*cm]) if img_table_data else ""
    
    main_table_data = [
        [text_col, inner_img_table]
    ]
    
    main_table = Table(main_table_data, colWidths=[10*cm, 6*cm])
    main_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(main_table)
    elements.append(Spacer(1, 10))

    # 3. 正文内容
    sections = report_data.get('sections', [])
    if sections:
        for s in sections:
            # 章节标题
            title = s.get('chapter_title', '未知章节')
            elements.append(Paragraph(f"<b>{title}</b>", h2_style))
            
            # 高光标签 (每个标签独立占一行展示)
            highlights = s.get('highlights', [])
            if highlights:
                for h in highlights:
                    # 处理标签文字：去除首尾空格，替换内部空格和连字符为不换行字符
                    tag_text = f"#{h.strip()}".replace(' ', '\u00A0').replace('-', '\u2011')
                    
                    # 获取文字宽度以精确适配背景框，并增加足够的缓冲
                    # OPPOSans 等现代字体在计算时可能存在微小偏差，增加到 30pt 的总缓冲 (14pt 边距 + 16pt 安全空间)
                    text_width = pdfmetrics.stringWidth(tag_text, CHINESE_FONT_NAME, 9) + 30
                    
                    # 限制最大宽度，防止极长标签溢出页面（A4 可用宽度约为 16cm）
                    max_tag_width = 15*cm
                    final_width = min(text_width, max_tag_width)
                    
                    tag_para = Paragraph(tag_text, highlight_style)
                    # 使用 Table 包裹以限制背景色宽度，并强制左对齐
                    tag_table = Table([[tag_para]], colWidths=[final_width], hAlign='LEFT')
                    tag_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm), # 标签间的垂直间距
                    ]))
                    elements.append(tag_table)
                elements.append(Spacer(1, 5))
            
            # 段落内容
            for p in s.get('paragraphs', []):
                if p.strip():
                    elements.append(Paragraph(p.strip(), body_style))
    else:
        # 降级方案：处理纯文本 content
        raw_content = report_data.get('content', '')
        # 清理每一行
        lines = [line.strip() for line in raw_content.split('\n')]
        
        for line in lines:
            if not line:
                continue
            
            # 处理 Markdown 标题
            if line.startswith('## '):
                title = line.replace('## ', '').strip()
                elements.append(Paragraph(f"<b>{title}</b>", h2_style))
            elif line.startswith('# '):
                title = line.replace('# ', '').strip()
                elements.append(Paragraph(f"<b>{title}</b>", title_style))
            else:
                # 普通段落
                elements.append(Paragraph(line, body_style))

    # 生成 PDF
    doc.build(elements, onFirstPage=lambda c, d: draw_header_footer(c, d, report_data), 
              onLaterPages=lambda c, d: draw_header_footer(c, d, report_data))
    
    buffer.seek(0)
    return buffer

#!/usr/bin/env python3
"""
2026 서울시 빅데이터 활용 경진대회 시각화부문 발표자료 생성
제목: "같은 서울, 다른 재활용 — 데이터가 묻고 답하다"
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
import os

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)

# ── 컬러 정의 ──
BG = RGBColor(0xF7, 0xF3, 0xEC)
BLUE = RGBColor(0x15, 0x65, 0xC0)
GREEN = RGBColor(0x43, 0xA0, 0x47)
YELLOW = RGBColor(0xF9, 0xA8, 0x25)
RED = RGBColor(0xC6, 0x28, 0x28)
TEXT = RGBColor(0x3E, 0x27, 0x23)
TEXT_SUB = RGBColor(0x8D, 0x6E, 0x63)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD_BG = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xE0, 0xD8, 0xCF)
DARK_CARD = RGBColor(0xF0, 0xEB, 0xE3)
TITLE_LINE_COLOR = RGBColor(0x8D, 0x6E, 0x63)

FONT_TITLE = "맑은 고딕"
FONT_BODY = "맑은 고딕"

SW = Inches(13.333)
SH = Inches(7.5)

slide_counter = 0


# ── 헬퍼 함수 ──

def add_bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = BG


def add_shape(slide, shape_type, left, top, width, height, fill_color=None, line_color=None):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


def add_shadow(shape):
    """카드에 그림자 효과 추가"""
    spPr = shape._element.spPr
    # effectLst 추가
    effectLst = spPr.find(qn('a:effectLst'))
    if effectLst is None:
        effectLst = etree.SubElement(spPr, qn('a:effectLst'))
    outerShdw = etree.SubElement(effectLst, qn('a:outerShdw'))
    outerShdw.set('blurRad', str(int(Pt(8))))
    outerShdw.set('dist', str(int(Pt(3))))
    outerShdw.set('dir', '5400000')  # 아래 방향
    outerShdw.set('algn', 'tl')
    outerShdw.set('rotWithShape', '0')
    srgbClr = etree.SubElement(outerShdw, qn('a:srgbClr'))
    srgbClr.set('val', '000000')
    alpha = etree.SubElement(srgbClr, qn('a:alpha'))
    alpha.set('val', '25000')  # 25% opacity


def add_color_bar(slide, left, top, width, color):
    """KPI 카드 상단 컬러 라인"""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    return bar


def add_card(slide, left, top, width, height, text="", font_size=14, bold=False,
             color=TEXT, fill_color=CARD_BG, align=PP_ALIGN.LEFT, font_name=FONT_BODY,
             shadow=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    if shadow:
        add_shadow(shape)
    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.15)
        tf.margin_bottom = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.font.name = font_name
        p.alignment = align
    return shape


def add_text(slide, left, top, width, height, text, font_size=24, bold=False,
             color=TEXT, align=PP_ALIGN.LEFT, font_name=FONT_BODY):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return txBox


def add_multiline_text(slide, left, top, width, height, lines, font_size=16,
                       color=TEXT, align=PP_ALIGN.LEFT, font_name=FONT_BODY, line_spacing=1.5):
    """lines: list of (text, bold, color_override)"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        if isinstance(item, str):
            t, b, c = item, False, color
        else:
            t = item[0]
            b = item[1] if len(item) > 1 else False
            c = item[2] if len(item) > 2 else color
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = t
        p.font.size = Pt(font_size)
        p.font.bold = b
        p.font.color.rgb = c
        p.font.name = font_name
        p.alignment = align
        p.space_after = Pt(font_size * (line_spacing - 1))
    return txBox


def add_kpi(slide, left, top, num, label, color=BLUE, width=Inches(3.5), height=Inches(1.8)):
    # 상단 컬러 바
    add_color_bar(slide, left, top, width, color)
    card = add_card(slide, left, top, width, height)
    tf = card.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    # 숫자
    p = tf.paragraphs[0]
    p.text = num
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = color
    p.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.CENTER
    # 라벨
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(14)
    p2.font.color.rgb = TEXT_SUB
    p2.font.name = FONT_BODY
    p2.alignment = PP_ALIGN.CENTER
    return card


def add_slide_title(slide, text, left=Inches(0.8), top=Inches(0.4)):
    """제목: 상단 왼쪽 큰 볼드, 아래에 얇은 가로선(#8d6e63, 30% opacity)"""
    add_text(slide, left, top, Inches(11), Inches(0.7), text,
             font_size=32, bold=True, color=TEXT, font_name=FONT_TITLE)
    # 얇은 가로선 (파란 밑줄 바 대신)
    line = add_shape(slide, MSO_SHAPE.RECTANGLE,
                     left, top + Inches(0.85), Inches(11), Inches(0.02), fill_color=TITLE_LINE_COLOR)
    # 30% opacity 적용
    solidFill = line._element.spPr.find(qn('a:solidFill'))
    if solidFill is not None:
        srgbClr = solidFill.find(qn('a:srgbClr'))
        if srgbClr is not None:
            alpha = etree.SubElement(srgbClr, qn('a:alpha'))
            alpha.set('val', '30000')  # 30%


def add_placeholder_box(slide, left, top, width, height, label="[캡처 이미지 삽입]"):
    """스크린샷 교체용 placeholder — 텍스트 가운데 정렬"""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_CARD
    shape.line.color.rgb = LIGHT_GRAY
    shape.line.width = Pt(1.5)
    shape.line.dash_style = 2  # dash
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(18)
    p.font.color.rgb = TEXT_SUB
    p.font.name = FONT_BODY
    p.alignment = PP_ALIGN.CENTER
    return shape


def add_bottom_bar(slide, text, color=TEXT_SUB, font_size=12):
    add_text(slide, Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.5),
             text, font_size=font_size, color=color, align=PP_ALIGN.LEFT)


def add_slide_number(slide, num):
    """우하단 슬라이드 번호"""
    add_text(slide, Inches(12.3), Inches(7.0), Inches(0.8), Inches(0.4),
             str(num), font_size=10, color=TEXT_SUB, align=PP_ALIGN.RIGHT)


def add_watermark(slide):
    """하단 워터마크 텍스트"""
    add_text(slide, Inches(0.5), Inches(7.1), Inches(4.0), Inches(0.3),
             "같은 서울, 다른 재활용", font_size=8, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)


def new_slide():
    global slide_counter
    slide_counter += 1
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_bg(slide)
    add_slide_number(slide, slide_counter)
    add_watermark(slide)
    return slide


# ════════════════════════════════════════════════════════════════
# 슬라이드 1: 표지
# ════════════════════════════════════════════════════════════════
s = new_slide()

# 가운데 상단 초록 원 (재활용 심볼)
circle = add_shape(s, MSO_SHAPE.OVAL, Inches(6.0), Inches(0.8), Inches(1.3), Inches(1.3), fill_color=GREEN)
tf = circle.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.text = "\u267B"
p.font.size = Pt(48)
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.CENTER

# 메인 타이틀
add_text(s, Inches(1.5), Inches(2.5), Inches(10), Inches(1.2),
         "같은 서울, 다른 재활용", font_size=54, bold=True, color=TEXT,
         align=PP_ALIGN.CENTER, font_name=FONT_TITLE)

# 구분선
add_shape(s, MSO_SHAPE.RECTANGLE,
          Inches(5.5), Inches(3.8), Inches(2.3), Inches(0.04), fill_color=TITLE_LINE_COLOR)

# 부제
add_text(s, Inches(1.5), Inches(4.1), Inches(10), Inches(0.8),
         "데이터가 묻고 답하다", font_size=28, bold=False, color=TEXT_SUB,
         align=PP_ALIGN.CENTER, font_name=FONT_BODY)

# 하단 대회명
add_text(s, Inches(1.5), Inches(5.8), Inches(10), Inches(0.6),
         "2026 서울시 빅데이터 활용 경진대회 시각화부문", font_size=16, bold=False,
         color=TEXT_SUB, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# 슬라이드 2: 배경
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "2026.1.1 — 서울의 쓰레기는 더 이상 묻을 수 없다")

# KPI 3개
kpi_y = Inches(2.0)
add_kpi(s, Inches(0.8), kpi_y, "384만톤", "서울시 연간 폐기물 발생량", BLUE)
add_kpi(s, Inches(4.8), kpi_y, "61.9%", "물질+음식물 재활용률", GREEN)
add_kpi(s, Inches(8.8), kpi_y, "5.6%", "직매립 금지!", RED, width=Inches(3.7))

# 하단 메시지
msg_card = add_card(s, Inches(0.8), Inches(4.5), Inches(11.7), Inches(1.5),
                    fill_color=DARK_CARD, shadow=False)
tf = msg_card.text_frame
tf.clear()
tf.word_wrap = True
tf.margin_left = Inches(0.4)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "수도권 직매립 금지 시행. 21만톤의 매립 폐기물이 새 출구를 찾아야 한다."
p.font.size = Pt(20)
p.font.color.rgb = TEXT
p.font.name = FONT_BODY
p.font.bold = True


# ════════════════════════════════════════════════════════════════
# 슬라이드 3: 현황
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "5년간 무엇이 변했는가?")

kpi_data = [
    ("발생량 +8.4%", "354만 → 384만톤", BLUE),
    ("1인가구 +19.4%", "140만 → 167만 가구", YELLOW),
    ("매립 -38.3%", "21만 → 13만톤", GREEN),
    ("기타 ×33배", "0.3% → 8.9%", RED),
]
for i, (num, label, clr) in enumerate(kpi_data):
    add_kpi(s, Inches(0.5 + i * 3.2), Inches(2.0), num, label, clr, width=Inches(2.9), height=Inches(1.8))

# 하단 메시지
add_card(s, Inches(0.8), Inches(4.5), Inches(11.7), Inches(1.2),
         "매립은 줄었지만, 기타가 폭증했다 — 처리시설 부족의 신호",
         font_size=20, bold=True, color=RED, fill_color=DARK_CARD, align=PP_ALIGN.CENTER,
         shadow=False)


# ════════════════════════════════════════════════════════════════
# 슬라이드 4: 흐름
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "383만톤은 어디로 가는가?")

# Sankey placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(9.0), Inches(5.0),
                    "[Sankey 다이어그램 — 대시보드에서 캡처]")

# 우측 변화율
add_card(s, Inches(10.3), Inches(2.2), Inches(2.5), Inches(1.5),
         "매립\n-38.3%", font_size=28, bold=True, color=GREEN, fill_color=CARD_BG, align=PP_ALIGN.CENTER)
add_card(s, Inches(10.3), Inches(4.2), Inches(2.5), Inches(1.5),
         "기타\n+3,253%", font_size=28, bold=True, color=RED, fill_color=CARD_BG, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# 슬라이드 5: 흐름 추이
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "매립은 줄었지만, '기타'가 그 자리를 채웠다")

# 스택바 placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.8),
                    "[5년 추이 스택바 차트 — 대시보드에서 캡처]")

# 핵심 메시지 빨간 박스
add_card(s, Inches(2.0), Inches(6.0), Inches(9.3), Inches(1.0),
         "기타 0.3% \u2192 8.9% \u2014 처리시설 부족으로 폐기물이 이동만 하고 있다",
         font_size=18, bold=True, color=WHITE, fill_color=RED, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# 슬라이드 6: 격차
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "같은 서울인데, 왜 2배나 다를까?")

# 좌측 지도 placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(6.5), Inches(5.0),
                    "[자치구별 재활용률 지도 — 대시보드에서 캡처]")

# 우측 대비 카드
add_card(s, Inches(8.0), Inches(2.2), Inches(4.5), Inches(1.8),
         fill_color=CARD_BG)
card_top = s.shapes[-1]
tf = card_top.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.3)
p = tf.paragraphs[0]
p.text = "성동구 75.7%"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = GREEN
p.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph()
p2.text = "서울 최고 재활용률"
p2.font.size = Pt(14)
p2.font.color.rgb = TEXT_SUB
p2.alignment = PP_ALIGN.CENTER

add_text(s, Inches(9.5), Inches(4.2), Inches(2.0), Inches(0.6),
         "vs", font_size=24, bold=True, color=TEXT_SUB, align=PP_ALIGN.CENTER)

add_card(s, Inches(8.0), Inches(4.8), Inches(4.5), Inches(1.8),
         fill_color=CARD_BG)
card_bot = s.shapes[-1]
tf = card_bot.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.3)
p = tf.paragraphs[0]
p.text = "강서구 45.7%"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = RED
p.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph()
p2.text = "서울 최저 재활용률"
p2.font.size = Pt(14)
p2.font.color.rgb = TEXT_SUB
p2.alignment = PP_ALIGN.CENTER


# ════════════════════════════════════════════════════════════════
# 슬라이드 7: 격차 심화
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "어디를 먼저 해야 하는가?")

# 좌측: 시급도 Top5
add_text(s, Inches(0.8), Inches(1.8), Inches(5.5), Inches(0.5),
         "재활용률 개선 시급도 Top 5", font_size=20, bold=True, color=BLUE)

top5 = [
    ("1. 강서구", "45.7%", "기타 43.3% — 사실상 미처리"),
    ("2. 송파구", "50.2%", "인구 대비 인프라 부족"),
    ("3. 강남구", "51.8%", "상업 폐기물 비중 높음"),
    ("4. 서초구", "53.1%", "빌라 밀집 지역 취약"),
    ("5. 마포구", "54.6%", "비아파트 동 격차 극심"),
]
for i, (gu, rate, desc) in enumerate(top5):
    y = Inches(2.5 + i * 0.85)
    add_card(s, Inches(0.8), y, Inches(5.5), Inches(0.7), fill_color=CARD_BG)
    c = s.shapes[-1]
    tf = c.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    run1 = p.add_run()
    run1.text = f"{gu}  {rate}"
    run1.font.size = Pt(18)
    run1.font.bold = True
    run1.font.color.rgb = RED if i == 0 else TEXT
    run1.font.name = FONT_BODY
    run2 = p.add_run()
    run2.text = f"   {desc}"
    run2.font.size = Pt(13)
    run2.font.color.rgb = TEXT_SUB
    run2.font.name = FONT_BODY

# 우측: 기타 떠넘기기 경고
add_card(s, Inches(7.0), Inches(2.0), Inches(5.5), Inches(4.5), fill_color=CARD_BG)
warn = s.shapes[-1]
tf = warn.text_frame
tf.clear()
tf.word_wrap = True
tf.margin_left = Inches(0.4)
tf.margin_top = Inches(0.4)

p = tf.paragraphs[0]
p.text = "\u26A0  '기타' 떠넘기기 경고"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = RED
p.font.name = FONT_TITLE

p2 = tf.add_paragraph()
p2.text = " "
p2.font.size = Pt(8)

p3 = tf.add_paragraph()
p3.text = "강서구의 '기타' 비율"
p3.font.size = Pt(16)
p3.font.color.rgb = TEXT_SUB
p3.font.name = FONT_BODY

p4 = tf.add_paragraph()
p4.text = "43.3%"
p4.font.size = Pt(56)
p4.font.bold = True
p4.font.color.rgb = RED
p4.font.name = FONT_TITLE
p4.alignment = PP_ALIGN.CENTER

p5 = tf.add_paragraph()
p5.text = " "
p5.font.size = Pt(8)

p6 = tf.add_paragraph()
p6.text = "직매립 금지 이후 처리시설로 보내지 못한\n폐기물이 '기타'로 분류되어 떠돌고 있다"
p6.font.size = Pt(14)
p6.font.color.rgb = TEXT_SUB
p6.font.name = FONT_BODY


# ════════════════════════════════════════════════════════════════
# 슬라이드 8: 현장 강서구
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "강서구 \u2014 2021년 미스터리")

# 스택바 placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.8),
                    "[강서구 연도별 처리방법 스택바 차트 \u2014 대시보드에서 캡처]")

# 핵심
add_card(s, Inches(2.5), Inches(6.0), Inches(8.3), Inches(1.0),
         "19만 \u2192 75만톤 +290% 폭증. 이후 고착화.",
         font_size=22, bold=True, color=WHITE, fill_color=RED, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# 슬라이드 9: 현장 마포구 + 비교
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "아파트 없는 동 = 쓰레기 1.5배")

# 좌측: 빨강 카드 (비아파트)
add_card(s, Inches(0.8), Inches(2.0), Inches(4.5), Inches(3.5), fill_color=CARD_BG)
c = s.shapes[-1]
tf = c.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.3)
tf.margin_top = Inches(0.3)

p = tf.paragraphs[0]
p.text = "비아파트 밀집 13개 동"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = RED
p.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "1,235,037 kg"
p2.font.size = Pt(40)
p2.font.bold = True
p2.font.color.rgb = RED
p2.font.name = FONT_TITLE
p2.alignment = PP_ALIGN.CENTER

p3 = tf.add_paragraph()
p3.text = "분리배출 인프라 부족"
p3.font.size = Pt(14)
p3.font.color.rgb = TEXT_SUB
p3.alignment = PP_ALIGN.CENTER

# 가운데: x1.5
add_text(s, Inches(5.6), Inches(3.2), Inches(2.1), Inches(1.0),
         "\u00D71.5", font_size=48, bold=True, color=BLUE, align=PP_ALIGN.CENTER,
         font_name=FONT_TITLE)

# 우측: 초록 카드 (아파트)
add_card(s, Inches(8.0), Inches(2.0), Inches(4.5), Inches(3.5), fill_color=CARD_BG)
c = s.shapes[-1]
tf = c.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.3)
tf.margin_top = Inches(0.3)

p = tf.paragraphs[0]
p.text = "아파트 밀집 10개 동"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = GREEN
p.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "842,124 kg"
p2.font.size = Pt(40)
p2.font.bold = True
p2.font.color.rgb = GREEN
p2.font.name = FONT_TITLE
p2.alignment = PP_ALIGN.CENTER

p3 = tf.add_paragraph()
p3.text = "분리배출함 완비"
p3.font.size = Pt(14)
p3.font.color.rgb = TEXT_SUB
p3.alignment = PP_ALIGN.CENTER

add_bottom_bar(s, "마포구 동별 생활폐기물 배출량 비교 (2024 기준)")


# ════════════════════════════════════════════════════════════════
# 슬라이드 10: 원인
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "1인가구가 많으면 재활용이 어렵다?")

# 산점도 placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(8.5), Inches(5.0),
                    "[1인가구 수 vs 재활용률 산점도 \u2014 대시보드에서 캡처]")

# 관악구 하이라이트 카드
add_card(s, Inches(9.8), Inches(2.5), Inches(3.0), Inches(3.5), fill_color=CARD_BG)
c = s.shapes[-1]
tf = c.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.2)
tf.margin_top = Inches(0.3)

p = tf.paragraphs[0]
p.text = "관악구"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = BLUE
p.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "1인가구 최다"
p2.font.size = Pt(14)
p2.font.color.rgb = TEXT_SUB
p2.alignment = PP_ALIGN.CENTER

p3 = tf.add_paragraph()
p3.text = "15.4만명"
p3.font.size = Pt(30)
p3.font.bold = True
p3.font.color.rgb = TEXT
p3.font.name = FONT_TITLE
p3.alignment = PP_ALIGN.CENTER

p4 = tf.add_paragraph()
p4.text = "그런데 재활용률"
p4.font.size = Pt(14)
p4.font.color.rgb = TEXT_SUB
p4.alignment = PP_ALIGN.CENTER

p5 = tf.add_paragraph()
p5.text = "74.3%"
p5.font.size = Pt(36)
p5.font.bold = True
p5.font.color.rgb = GREEN
p5.font.name = FONT_TITLE
p5.alignment = PP_ALIGN.CENTER

p6 = tf.add_paragraph()
p6.text = "1인가구 \u2260 낮은 재활용률"
p6.font.size = Pt(12)
p6.font.color.rgb = RED
p6.font.bold = True
p6.alignment = PP_ALIGN.CENTER


# ════════════════════════════════════════════════════════════════
# 슬라이드 11: 원인 심화
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "인프라가 답이다")

# 3열
col_data = [
    ("아파트", "\u2705 분리배출함", "전용 수거함, 관리인 상주\n재활용 동선 완비", GREEN),
    ("빌라/다세대", "\u274C 인프라 없음", "종량제 봉투 혼합 배출\n분리 동선 부재", RED),
    ("결론", "인프라 격차 = 재활용 격차", "같은 서울, 같은 정책인데\n결과가 다른 이유", BLUE),
]

for i, (title, sub, desc, clr) in enumerate(col_data):
    x = Inches(0.5 + i * 4.2)
    add_card(s, x, Inches(2.0), Inches(3.8), Inches(3.2), fill_color=CARD_BG)
    c = s.shapes[-1]
    tf = c.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_top = Inches(0.3)
    tf.margin_right = Inches(0.3)

    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = clr
    p.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = TEXT
    p2.font.name = FONT_BODY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(16)

    p3 = tf.add_paragraph()
    p3.text = desc
    p3.font.size = Pt(13)
    p3.font.color.rgb = TEXT_SUB
    p3.font.name = FONT_BODY
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(12)

# 하단: 음식물 재활용 비교
add_card(s, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.2), fill_color=DARK_CARD, shadow=False)
c = s.shapes[-1]
tf = c.text_frame
tf.clear()
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.4)
p = tf.paragraphs[0]
run1 = p.add_run()
run1.text = "음식물 재활용 비교  |  "
run1.font.size = Pt(16)
run1.font.color.rgb = TEXT
run1.font.name = FONT_BODY
run2 = p.add_run()
run2.text = "강서구 7.6%"
run2.font.size = Pt(20)
run2.font.bold = True
run2.font.color.rgb = RED
run2.font.name = FONT_TITLE
run3 = p.add_run()
run3.text = "  vs  "
run3.font.size = Pt(16)
run3.font.color.rgb = TEXT_SUB
run4 = p.add_run()
run4.text = "성동구 17.3%"
run4.font.size = Pt(20)
run4.font.bold = True
run4.font.color.rgb = GREEN
run4.font.name = FONT_TITLE
p.alignment = PP_ALIGN.CENTER


# ════════════════════════════════════════════════════════════════
# 슬라이드 12: 결론 근거
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "데이터가 말하는 답")

steps = [
    ("1", "발생량 추세", "384만톤, 5년간 +8.4% 증가", BLUE),
    ("2", "처리방법 흐름", "매립 -38.3%, 기타 +3,253%", BLUE),
    ("3", "자치구 격차", "성동 75.7% vs 강서 45.7%", GREEN),
    ("4", "시급도 진단", "강서/송파/강남/서초/마포", YELLOW),
    ("5", "현장 원인", "아파트 유무 = 인프라 격차", RED),
    ("6", "제안", "비아파트 밀집 지역에 분리배출 인프라 우선 설치", RED),
]

for i, (num, title, desc, clr) in enumerate(steps):
    y = Inches(1.7 + i * 0.88)
    # 번호 원
    circle = add_shape(s, MSO_SHAPE.OVAL, Inches(1.2), y, Inches(0.55), Inches(0.55), fill_color=clr)
    tf = circle.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = num
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.CENTER

    # 연결선 (마지막 빼고)
    if i < 5:
        add_shape(s, MSO_SHAPE.RECTANGLE,
                  Inches(1.44), y + Inches(0.55), Inches(0.07), Inches(0.35), fill_color=LIGHT_GRAY)

    # 텍스트
    add_text(s, Inches(2.1), y - Inches(0.03), Inches(3.0), Inches(0.4),
             title, font_size=18, bold=True, color=TEXT, font_name=FONT_TITLE)
    add_text(s, Inches(5.2), y - Inches(0.03), Inches(7.0), Inches(0.4),
             desc, font_size=15, color=TEXT_SUB)


# ════════════════════════════════════════════════════════════════
# 슬라이드 13: 결론 제안
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "어디에 놓으면 되는가?")

# 좌측 지도 placeholder
add_placeholder_box(s, Inches(0.8), Inches(1.8), Inches(6.5), Inches(5.0),
                    "[제안 입지 지도 \u2014 대시보드에서 캡처]")

# 우측 Top5 리스트
add_text(s, Inches(8.0), Inches(1.8), Inches(4.5), Inches(0.5),
         "분리배출 인프라 우선 설치 Top 5", font_size=18, bold=True, color=BLUE)

locations = [
    ("1. 강서구 화곡1동", "배출량 589만kg, 일반주택 100%"),
    ("2. 강서구 화곡본동", "배출량 276만kg"),
    ("3. 강서구 발산1동", "배출량 140만kg"),
    ("4. 마포구 서교동", "25,060톤, +12.6% 증가"),
    ("5. 마포구 합정동", "+30.2% 급증"),
]
for i, (loc, detail) in enumerate(locations):
    y = Inches(2.5 + i * 0.85)
    card = add_card(s, Inches(8.0), y, Inches(4.5), Inches(0.7),
                    fill_color=CARD_BG, align=PP_ALIGN.LEFT)
    tf = card.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.1)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    run1 = p.add_run()
    run1.text = loc
    run1.font.size = Pt(15)
    run1.font.bold = True if i == 0 else False
    run1.font.color.rgb = RED if i == 0 else TEXT
    run1.font.name = FONT_BODY
    run2 = p.add_run()
    run2.text = f"  {detail}"
    run2.font.size = Pt(11)
    run2.font.color.rgb = TEXT_SUB
    run2.font.name = FONT_BODY


# ════════════════════════════════════════════════════════════════
# 슬라이드 14: 기대효과
# ════════════════════════════════════════════════════════════════
s = new_slide()
add_slide_title(s, "기대효과와 로드맵")

# 좌측: KPI 4개 (2x2)
kpis = [
    ("시범 5개소", "비아파트 밀집 지역", BLUE),
    ("+15~25%p", "재활용률 개선 목표", GREEN),
    ("3.2만 세대", "수혜 대상 가구", YELLOW),
    ("1.5억원", "시범사업 예상 예산", TEXT),
]
positions = [
    (Inches(0.8), Inches(2.0)),
    (Inches(4.0), Inches(2.0)),
    (Inches(0.8), Inches(4.2)),
    (Inches(4.0), Inches(4.2)),
]
for (num, label, clr), (x, y) in zip(kpis, positions):
    add_kpi(s, x, y, num, label, clr, width=Inches(2.8), height=Inches(1.7))

# 우측: 3단계 로드맵
roadmap = [
    ("Phase 1", "시범 설치 (3개월)", "5개 지역 분리배출 인프라 설치\n주민 교육 프로그램 병행", BLUE),
    ("Phase 2", "효과 평가 (6개월)", "재활용률 변화 추적\n주민 만족도 조사", GREEN),
    ("Phase 3", "전면 확대 (12개월)", "성공 모델 25개 구 확산\n조례 개정 및 예산 확보", RED),
]
for i, (phase, title, desc, clr) in enumerate(roadmap):
    y = Inches(2.0 + i * 1.7)
    # 단계 뱃지
    badge = add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE,
                      Inches(7.5), y, Inches(1.5), Inches(0.4), fill_color=clr)
    tf = badge.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = phase
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.CENTER

    add_text(s, Inches(9.2), y - Inches(0.05), Inches(3.5), Inches(0.35),
             title, font_size=15, bold=True, color=TEXT, font_name=FONT_TITLE)
    add_text(s, Inches(9.2), y + Inches(0.35), Inches(3.5), Inches(0.9),
             desc, font_size=11, color=TEXT_SUB)

    # 연결선
    if i < 2:
        add_shape(s, MSO_SHAPE.RECTANGLE,
                  Inches(8.22), y + Inches(0.4), Inches(0.06), Inches(1.3), fill_color=LIGHT_GRAY)


# ════════════════════════════════════════════════════════════════
# 슬라이드 15: 마무리
# ════════════════════════════════════════════════════════════════
s = new_slide()

# 초록 원 (표지와 동일)
circle = add_shape(s, MSO_SHAPE.OVAL, Inches(6.0), Inches(1.0), Inches(1.3), Inches(1.3), fill_color=GREEN)
tf = circle.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.text = "\u267B"
p.font.size = Pt(48)
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.CENTER

# 메인 메시지
add_text(s, Inches(1.5), Inches(2.8), Inches(10), Inches(1.0),
         "같은 서울, 같은 재활용을 위해", font_size=44, bold=True, color=TEXT,
         align=PP_ALIGN.CENTER, font_name=FONT_TITLE)

# 얇은 구분선 (파란 바 대신)
add_shape(s, MSO_SHAPE.RECTANGLE,
          Inches(5.0), Inches(3.9), Inches(3.3), Inches(0.03), fill_color=TITLE_LINE_COLOR)

add_text(s, Inches(1.5), Inches(4.2), Inches(10), Inches(0.8),
         "인프라가 답이다", font_size=32, bold=True, color=BLUE,
         align=PP_ALIGN.CENTER, font_name=FONT_TITLE)

# 하단 정보 — 수정된 출처
add_text(s, Inches(1.5), Inches(5.8), Inches(10), Inches(0.5),
         "데이터 출처: 서울 데이터 허브(data.seoul.go.kr), KOSIS(통계청), 통계청 행정구역 경계",
         font_size=12, color=TEXT_SUB, align=PP_ALIGN.CENTER)

add_text(s, Inches(1.5), Inches(6.3), Inches(10), Inches(0.5),
         "2026 서울시 빅데이터 활용 경진대회 시각화부문",
         font_size=14, color=TEXT_SUB, align=PP_ALIGN.CENTER)


# ── 저장 ──
out_path = r"/mnt/c/Users/user/Desktop/agentAI_data/20260505_cleanhouse_location/2026_서울데이터허브_공모전/03.result/presentation.pptx"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
prs.save(out_path)
print(f"PPTX saved: {out_path}")
print(f"Slides: {len(prs.slides)}")


# ═══════════════════════════════════════════════════════════════
# HTML 프리뷰 생성
# ═══════════════════════════════════════════════════════════════
def generate_html_preview(prs, out_html):
    """PPTX의 각 슬라이드를 HTML로 근사 렌더링"""
    SCALE = 960 / prs.slide_width  # px per emu

    def emu_to_px(emu_val):
        return int(emu_val * SCALE)

    def rgb_to_hex(rgb):
        if rgb is None:
            return "transparent"
        return f"#{rgb}"

    html_parts = []
    html_parts.append("""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{background:#333;font-family:'Malgun Gothic','맑은 고딕',sans-serif;padding:20px;}
.slide{width:960px;height:540px;margin:30px auto;position:relative;overflow:hidden;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.3);background:#F7F3EC;}
.slide-num{color:#999;text-align:center;font-size:13px;margin:8px 0 20px;}
.shape{position:absolute;display:flex;flex-direction:column;justify-content:center;padding:10px;box-sizing:border-box;overflow:hidden;border-radius:8px;}
.shadow{box-shadow:0 2px 6px rgba(0,0,0,0.15);}
</style></head><body>
""")

    total = len(prs.slides)
    for slide_idx, slide in enumerate(prs.slides, 1):
        html_parts.append('<div class="slide">\n')
        for shape in slide.shapes:
            left = emu_to_px(shape.left)
            top = emu_to_px(shape.top)
            width = emu_to_px(shape.width)
            height = emu_to_px(shape.height)

            # 배경색
            bg_color = "transparent"
            try:
                if shape.fill.type is not None:
                    bg_color = f"#{shape.fill.fore_color.rgb}"
            except Exception:
                pass

            # 테두리
            border = "none"
            try:
                if shape.line.fill.type is not None:
                    border = f"1px solid #{shape.line.color.rgb}"
            except Exception:
                pass

            # 그림자 판정
            shadow_class = ""
            try:
                effectLst = shape._element.spPr.find(qn('a:effectLst'))
                if effectLst is not None and effectLst.find(qn('a:outerShdw')) is not None:
                    shadow_class = " shadow"
            except Exception:
                pass

            # 모양: 원인지 확인
            border_radius = "8px"
            try:
                if shape.shape_type == MSO_SHAPE.OVAL:
                    border_radius = "50%"
            except Exception:
                pass

            style = (f"left:{left}px;top:{top}px;width:{width}px;height:{height}px;"
                     f"background:{bg_color};border:{border};border-radius:{border_radius};")

            html_parts.append(f'<div class="shape{shadow_class}" style="{style}">\n')

            # 텍스트 추출
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if not para.text.strip():
                        continue
                    font_size = 14
                    font_color = "#3E2723"
                    font_weight = "normal"
                    text_align = "left"
                    try:
                        if para.font.size:
                            font_size = int(para.font.size.pt * 0.65)
                        if para.font.color and para.font.color.rgb:
                            font_color = f"#{para.font.color.rgb}"
                        if para.font.bold:
                            font_weight = "bold"
                    except Exception:
                        pass
                    # alignment
                    try:
                        if para.alignment == PP_ALIGN.CENTER:
                            text_align = "center"
                        elif para.alignment == PP_ALIGN.RIGHT:
                            text_align = "right"
                    except Exception:
                        pass

                    ptext = para.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html_parts.append(
                        f'<div style="font-size:{font_size}px;color:{font_color};'
                        f'font-weight:{font_weight};line-height:1.4;margin:2px 0;'
                        f'text-align:{text_align};">{ptext}</div>\n'
                    )

            html_parts.append('</div>\n')
        html_parts.append('</div>\n')
        html_parts.append(f'<div class="slide-num">슬라이드 {slide_idx} / {total}</div>\n')

    html_parts.append('</body></html>')

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))
    print(f"HTML preview saved: {out_html}")


html_path = r"/mnt/c/Users/user/Desktop/agentAI_data/20260505_cleanhouse_location/2026_서울데이터허브_공모전/03.result/ppt_preview.html"
generate_html_preview(prs, html_path)

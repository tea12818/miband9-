#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小米手环9 NFC 版 · 终端风格表盘生成器   canvas 192 x 490 (AMOLED)

产物（out/）：
  preview_idle.png / preview_notify.png / preview_sport.png
  preview_lowbat.png / preview_boot.png          五个状态
  preview_*_x3.png                                3 倍最近邻放大（校对像素）
  assets/base.png                                 底板，直接当表盘编辑器背景
  assets/big/*.png                                大号时间数字（53px bold）
  assets/small16|18|20/*.png                      小号字符图集（等宽）
  assets/icons/*.png                              电量帧、蓝牙、心形
  layout.json                                     全部元素坐标/字号/颜色/示例
  spec.md                                         自动生成的坐标表

用法： python scripts/make_watchface.py
依赖： Pillow  (pip install pillow)
"""
import json
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

W, H = 192, 490
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu",
             "/Library/Fonts", "/System/Library/Fonts"]
MONO = ["DejaVuSansMono.ttf", "consola.ttf", "LiberationMono-Regular.ttf"]
MONO_B = ["DejaVuSansMono-Bold.ttf", "consolab.ttf", "LiberationMono-Bold.ttf"]
CJK = ["simhei.ttf", "msyh.ttc", "NotoSansCJK-Regular.ttc", "wqy-microhei.ttc"]

# ------------------------------------------------------------------ 调色板
BG   = (4, 7, 5)        # 纯黑 (0,0,0) 最省电；这里带一点绿，肉眼更"荧光屏"
G0   = (226, 255, 236)  # 高亮白绿 —— 只给大号时间
G1   = (54, 255, 116)   # 主绿 —— 数值
G2   = (30, 150, 72)    # 中绿 —— 标签 / 命令
G3   = (16, 82, 40)     # 暗绿 —— 分隔线 / 未填充 / 注释
CY   = (64, 232, 214)   # 青 —— 光标 / 强调
AM   = (255, 176, 0)    # 琥珀 —— 警告 / 低电
RED  = (255, 84, 84)    # 红 —— 错误
PANEL = (8, 18, 12)     # 浮层底色

# ------------------------------------------------------------------ 字体
def _find(names):
    for n in names:
        for d in FONT_DIRS:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


F_MONO = _find(MONO)
F_MONOB = _find(MONO_B)
F_CJK = _find(CJK)
_C = {}


def font(size, bold=False, cjk=False):
    k = (size, bold, cjk)
    if k not in _C:
        p = F_CJK if cjk else (F_MONOB if bold else F_MONO)
        _C[k] = ImageFont.truetype(p, size)
    return _C[k]


def adv(size, bold=False):
    """等宽字体步进（四舍五入成整数，便于像素级对齐）"""
    return round(font(size, bold).getlength("0")) // 1


def text(d, xy, s, size, color, bold=False, anchor="ls", cjk=False, sp=None):
    f = font(size, bold, cjk)
    if sp is None:
        d.text(xy, s, font=f, fill=color, anchor=anchor)
        return
    x = xy[0]
    for ch in s:
        d.text((x, xy[1]), ch, font=f, fill=color, anchor=anchor)
        x += sp if ch.isascii() else size


def rule(d, y, x0=10, x1=182, color=G3, dash=3, gap=3):
    x = x0
    while x < x1:
        d.rectangle([x, y, min(x + dash - 1, x1 - 1), y], fill=color)
        x += dash + gap


def seg_bar(d, x, y, w, h, ratio, segs, on=G1, off=G3, gap=2):
    sw = max(2, (w - (segs - 1) * gap) // segs)
    lit = int(round(max(0.0, min(1.0, ratio)) * segs))
    for i in range(segs):
        sx = x + i * (sw + gap)
        d.rectangle([sx, y, sx + sw - 1, y + h - 1], fill=on if i < lit else off)


def wave(d, x, y, w, h, vals, color=G1, gap=2):
    n = len(vals)
    sw = max(2, (w - (n - 1) * gap) // n)
    for i, v in enumerate(vals):
        bh = max(2, int(round(h * v)))
        sx = x + i * (sw + gap)
        d.rectangle([sx, y + h - bh, sx + sw - 1, y + h - 1], fill=color)


def bt_icon(d, x, y, color=G2, h=11, w=7):
    """蓝牙符文：中竖 + 上行折线 + 下行折线（像素级）"""
    cx = x + w // 2
    d.line([cx, y, cx, y + h - 1], fill=color, width=1)          # 竖
    d.line([cx, y, x + w - 1, y + 3], fill=color, width=1)       # 右上斜
    d.line([x + w - 1, y + 3, x + 1, y + h - 3], fill=color, width=1)
    d.line([cx, y + h - 1, x + w - 1, y + h - 4], fill=color, width=1)
    d.line([x + w - 1, y + h - 4, x + 1, y + 3], fill=color, width=1)


def heart(d, x, y, color=G1, s=7):
    d.rectangle([x + 1, y, x + s - 2, y + 1], fill=color)
    d.rectangle([x, y + 1, x + s - 1, y + s - 3], fill=color)
    d.rectangle([x + 1, y + s - 2, x + s - 2, y + s - 2], fill=color)


# ------------------------------------------------------------------ 网格
# 行内 x 坐标全部按 18px 等宽字符步进 11px 推算，保证"真终端"对齐
P = 10              # 左右安全边距（胶囊屏圆角）
S18, A18 = 18, 11   # 正文等宽 18px / 步进 11
S20, A20 = 20, 12   # 日期 20px / 步进 12
S16, A16 = 16, 10   # 日志 16px / 步进 10
BIG, BIG_A = 53, 32  # 大号时间 53px bold / 步进 32（5 字宽 160）

Y_STAT   = 20
Y_R1     = 26
Y_CMD    = 45
Y_TIME   = 100
Y_DATE   = 124
Y_R2     = 134
Y_HD     = 156
Y_ROW0   = 182
ROW_STEP = 25
Y_LOGHD  = 306
Y_LOG0   = 326
LOG_STEP = 18
Y_R3     = 392
Y_UP     = 410
Y_PROMPT = 448
Y_TAIL   = 472


# ------------------------------------------------------------------ 闭包：公共骨架
def draw_common(d, st, blank=False):
    g = st["green"]
    hi = g if st["battery"] > 20 else AM

    # ① 状态行  root@band9 ·[bt]· 86%
    text(d, (P, Y_STAT), "root@band9", S18, G2)
    pct = f"{st['battery']}%"
    txt = "" if blank else pct
    tx = W - P - len(pct) * A18
    bt_icon(d, tx - 12, Y_STAT - 11, hi if blank else hi)
    text(d, (W - P, Y_STAT), txt, S18, hi, anchor="rs")

    rule(d, Y_R1, P, W - P, G3, dash=2, gap=2)

    # ② 命令行：左边命令，右边秒数（唯一的"心跳"元素）
    text(d, (P, Y_CMD), st["cmd"], S18, G2)
    if not blank:
        text(d, (W - P, Y_CMD), ":" + st["sec"], S16, hi, anchor="rs")

    # ③ 大号时间 HH:MM （4 位 + 冒号，居中）
    hhmm = st["hhmm"]
    x0 = (W - BIG_A * len(hhmm)) // 2
    if not blank:
        for i, ch in enumerate(hhmm):
            text(d, (x0 + i * BIG_A, Y_TIME), ch, BIG, st["time_color"], bold=True)

    # ④ 日期行
    if not blank:
        text(d, (P, Y_DATE), st["date"], S20, G2)

    rule(d, Y_R2, P, W - P, G3, dash=1, gap=3)

    # ⑤ resmon 面板
    text(d, (P, Y_HD), "# resmon", S18, g)
    text(d, (W - P, Y_HD), st["clock"], S18, G3, anchor="rs")

    for i, r in enumerate(st["rows"]):
        y = Y_ROW0 + i * ROW_STEP
        text(d, (P, y), r["label"], S18, G2)
        bx, bw = P + A18 * 5 + 8, 60
        if blank:
            seg_bar(d, bx, y - 12, bw, 10, 0.0, 10, on=r.get("color", g), off=G3)
        elif r.get("kind") == "wave":
            wave(d, bx, y - 12, bw, 12, r["wave"], color=r.get("color", g))
        else:
            seg_bar(d, bx, y - 12, bw, 10, r["ratio"], 10,
                    on=r.get("color", g), off=G3)
        text(d, (W - P, y), "" if blank else r["value"], S18, r.get("color", g),
             anchor="rs")

    # ⑥ 日志尾块（16px，最多 17 字符）
    text(d, (P, Y_LOGHD), "$ tail band.log", S16, G2)
    for i, (ln, c) in enumerate(st["log"]):
        text(d, (P, Y_LOG0 + i * LOG_STEP), "//" if blank else ln, S16, c)

    rule(d, Y_R3, P, W - P, G3, dash=2, gap=2)

    # ⑦ uptime
    text(d, (P, Y_UP), "$ uptime", S18, G2)
    text(d, (W - P, Y_UP), "" if blank else st["uptime"], S18, g, anchor="rs")

    # ⑧ 底部提示符 + 块状光标 + 状态位
    text(d, (P, Y_PROMPT), "root@band9:~$", S18, g)
    if not blank:
        d.rectangle([P + A18 * 13 + 5, Y_PROMPT - 12,
                     P + A18 * 13 + 13, Y_PROMPT + 1], fill=CY)
    text(d, (P, Y_TAIL), st["tail"], S16, G3)


# ------------------------------------------------------------------ 五个状态
def state_idle():
    return dict(
        green=G1, time_color=G0, battery=86, hhmm="08:24", sec="37",
        cmd="$ date", comment="# local",
        date="WED 12JUN25", clock="08:24",
        rows=[
            dict(label="BAT", ratio=0.86, value="86%"),
            dict(label="HR", kind="wave",
                 wave=[.30, .55, .80, 1.0, .74, .48, .34, .22], value="72"),
            dict(label="STEP", ratio=0.82, value="8204"),
            dict(label="KCAL", ratio=0.31, value="312"),
            dict(label="TEMP", ratio=0.62, value="27C", color=CY),
        ],
        log=[("[08:20] btn1 wake", G2),
             ("[07:58] hr avg 71", G2),
             ("[07:30] alarm ok", G3),
             ("[06:41] bt up", G3)],
        uptime="12d 3h", tail="bt:1 dnd:0 ala:1",
    )


def state_lowbat():
    return dict(
        green=AM, time_color=(255, 214, 150), battery=9, hhmm="22:47", sec="02",
        cmd="$ date", comment="# nfc", date="THU 13JUN25", clock="22:47",
        rows=[
            dict(label="BAT", ratio=0.09, value="9%", color=RED),
            dict(label="HR", kind="wave",
                 wave=[.20, .34, .50, .64, .46, .30, .22, .16], value="64", color=AM),
            dict(label="STEP", ratio=0.94, value="9412", color=AM),
            dict(label="KCAL", ratio=0.36, value="356", color=AM),
            dict(label="SLEEP", ratio=0.71, value="7h10", color=AM),
        ],
        log=[("[22:44] warn bat9%", RED),
             ("[22:41] save on", AM),
             ("[21:16] idle dim", G2),
             ("[20:02] bt lost", G2)],
        uptime="13d 2h", tail="chg:0 mode:save",
    )


def state_sport():
    return dict(
        green=G1, time_color=G0, battery=74, hhmm="00:34", sec="11",
        cmd="$ run", comment="# pace", date="RUN 6'12 142bpm", clock="00:34",
        rows=[
            dict(label="PACE", kind="wave",
                 wave=[.45, .68, .92, .80, .58, .40, .30, .50], value="6'12"),
            dict(label="HR", kind="wave",
                 wave=[.40, .62, .84, 1.0, .88, .70, .56, .48], value="142", color=RED),
            dict(label="CAD", ratio=0.78, value="178"),
            dict(label="KCAL", ratio=0.44, value="438"),
            dict(label="PWR", ratio=0.66, value="231w", color=CY),
        ],
        log=[("[00:00] lap1 1.0km", G2),
             ("[00:10] pace 6'12", G2),
             ("[00:22] zone3 max", G3),
             ("[00:31] autolap", G3)],
        uptime="5.62km", tail="gps:1 auto:0",
    )


def state_boot():
    """上电/开机态：终端 boot log，用 4 行滚动"""
    return dict(
        green=G1, time_color=G3, battery=100, hhmm="00:00", sec="00",
        cmd="$ boot", comment="# init", date="BOOT ROM v1.4", clock="--:--",
        rows=[
            dict(label="BAT", ratio=1.0, value="100%"),
            dict(label="HR", kind="wave",
                 wave=[.1, .2, .3, .4, .3, .2, .1, .1], value="--"),
            dict(label="STEP", ratio=0.0, value="0"),
            dict(label="KCAL", ratio=0.0, value="0"),
            dict(label="TEMP", ratio=0.5, value="--C", color=CY),
        ],
        log=[("[ OK ] mmc0 mount", G1),
             ("[ OK ] sensors up", G1),
             ("[ OK ] bt stack", G1),
             ("[ BOOT ] ui init", CY)],
        uptime="0s", tail="mode:boot",
    )


# ------------------------------------------------------------------ AOD 息屏态
def draw_aod(hhmm="08:24", batt=86, shake=0):
    """AOD：全黑 + 极暗绿时间 + 一枚光标；像素位移防 AMOLED 残影"""
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 232 + shake
    x0 = (W - BIG_A * 5) // 2
    for i, ch in enumerate(hhmm):
        text(d, (x0 + i * BIG_A, y), ch, BIG, (44, 104, 64), bold=True)
    rule(d, y + 34, 52, 140, (18, 42, 24), dash=2, gap=4)
    # 电量：4 个暗点，低于 20% 变琥珀
    on = (150, 104, 0) if batt <= 20 else (26, 62, 34)
    lit = 1 if batt <= 20 else max(1, min(4, int(batt // 25) + 1))
    for i in range(4):
        x = 60 + i * 12
        d.rectangle([x, 300 + shake, x + 7, 306 + shake],
                    fill=on if i < lit else (10, 24, 14))
    # 光标：两帧（亮 / 灭）
    d.rectangle([130, 318 + shake, 144, 324 + shake], fill=(64, 232, 214))
    return im

# ------------------------------------------------------------------ 通知浮层
def draw_notify(img):
    """通知态：整屏下半压黑，浮出一张终端风格的通知卡"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 132, W - 1, H - 1], fill=BG)
    d.rectangle([4, 146, W - 5, 430], fill=PANEL, outline=G1, width=1)

    text(d, (12, 154), "[ INCOMING ]", S16, G1, anchor="la")
    text(d, (W - 12, 154), "1/3", S16, G3, anchor="ra")
    rule(d, 174, 8, W - 9, G3, dash=2, gap=2)

    text(d, (12, 184), "WECHAT", S16, G2, anchor="la")
    text(d, (W - 12, 184), "08:24", S16, G3, anchor="ra")

    text(d, (12, 204), "老王", 26, G1, cjk=True, anchor="la")
    text(d, (12, 242), "晚上 7 点老地方", 22, G1, cjk=True, anchor="la")
    text(d, (12, 274), "到了给你留位", 22, G2, cjk=True, anchor="la")
    text(d, (12, 306), "seen:1 unread:2", S16, G3, anchor="la")

    rule(d, 356, 8, W - 9, G3, dash=2, gap=2)
    for i, k in enumerate(["^ESC", "O VIEW", "SWIPE>"]):
        bx = 10 + i * 58
        d.rectangle([bx, 366, bx + 52, 384], outline=G3, width=1, fill=(6, 14, 9))
        text(d, (bx + 26, 382), k, S16 - 3, CY if i == 1 else G2, anchor="ms")

    text(d, (12, 404), "$ reply >", S16, G3, anchor="la")
    text(d, (W - 12, 404), "_", S16, CY, anchor="ra")

# ------------------------------------------------------------------ 资源导出
BIG_GLYPHS = "0123456789:.-"
SMALL_GLYPHS = ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                ":.-/%[]()'#><$~_")
NICE = {".": "dot", "/": "slash", "%": "pct", "[": "lb", "]": "rb", "(": "lp",
        ")": "rp", "'": "apos", "#": "hash", ">": "gt", "<": "lt", "$": "dollar",
        "~": "tilde", "_": "us", ":": "colon", "-": "dash"}


def export_big(dirname, rel):
    os.makedirs(dirname, exist_ok=True)
    cell_h = BIG + 6
    meta = {}
    for ch in BIG_GLYPHS:
        im = Image.new("L", (BIG_A, cell_h), 0)
        ImageDraw.Draw(im).text((0, cell_h - 6), ch, font=font(BIG, True), fill=255,
                                anchor="ls")
        nm = NICE.get(ch, ch)
        im.convert("RGBA").save(os.path.join(dirname, nm + ".png"))
        meta[nm] = dict(file=f"{rel}/{nm}.png", w=BIG_A, h=cell_h,
                        advance=BIG_A, baseline_from_top=cell_h - 6)
    return meta


def export_small(dirname, rel, size):
    os.makedirs(dirname, exist_ok=True)
    a = adv(size)
    cell_h = size + 6
    meta = {}
    for ch in SMALL_GLYPHS:
        im = Image.new("L", (a, cell_h), 0)
        ImageDraw.Draw(im).text((0, cell_h - 6), ch, font=font(size), fill=255,
                                anchor="ls")
        nm = NICE.get(ch, ch)
        im.convert("RGBA").save(os.path.join(dirname, nm + ".png"))
        meta[nm] = dict(file=f"{rel}/{nm}.png", w=a, h=cell_h, advance=a,
                        baseline_from_top=cell_h - 6)
    return meta


CJK_CHARS = "老王晚上点地方到了给你留位消息未读查看返回"


def export_cjk(dirname, rel, size=26, other=22):
    """中文剪字：每个字单独一张，供通知/自定义文案拼接"""
    os.makedirs(dirname, exist_ok=True)
    meta = {}
    for s, tag in ((size, f"cjk{size}"), (other, f"cjk{other}")):
        for ch in CJK_CHARS:
            im = Image.new("L", (s + 2, s + 6), 0)
            ImageDraw.Draw(im).text((1, s), ch, font=font(s, cjk=True), fill=255,
                                    anchor="ls")
            fn = f"{tag}_{ord(ch):04X}.png"
            im.convert("RGBA").save(os.path.join(dirname, fn))
            meta[f"{tag}_{ord(ch):06X}"] = dict(file=f"{rel}/{fn}", char=ch,
                                               w=s + 2, h=s + 6, advance=s)
    return meta

def export_icons(dirname, rel):
    os.makedirs(dirname, exist_ok=True)
    for i in range(5):
        im = Image.new("L", (22, 9), 0)
        seg_bar(ImageDraw.Draw(im), 0, 0, 22, 9, i / 4 if i else 0.01, 4, 255, 60)
        im.convert("RGBA").save(os.path.join(dirname, f"bat_{i}.png"))
    im = Image.new("L", (7, 11), 0)
    bt_icon(ImageDraw.Draw(im), 0, 0, 255, 11, 7)
    im.convert("RGBA").save(os.path.join(dirname, "bt.png"))
    im = Image.new("L", (7, 7), 0)
    heart(ImageDraw.Draw(im), 0, 0, 255, 7)
    im.convert("RGBA").save(os.path.join(dirname, "heart.png"))


# ------------------------------------------------------------------ layout.json
def build_layout(big, s16, s18, s20):
    items = []

    def add(name, kind, **kw):
        kw.update(name=name, kind=kind)
        items.append(kw)

    add("status.prompt", "text", x=P, y=Y_STAT, anchor="ls", font="mono18",
        size=S18, advance=A18, color="#1E9648", sample="root@band9")
    add("status.bt", "asset", file="assets/icons/bt.png",
        x=W - P - 4 * A18 - 12, y=Y_STAT - 11, w=7, h=11, role="bt_link",
        note="x 随电量位数右移：x = 182 - len(pct)*11 - 12")
    add("status.pct", "text", x=W - P, y=Y_STAT, anchor="rs", font="mono18",
        size=S18, advance=A18, color="#36FF74", sample="86%", role="battery")
    add("status.batbar", "bar", x=W - P - A18 * 3 - 28, y=Y_STAT - 12, w=22, h=9,
        segs=4, gap=2, color="#36FF74", off="#105228", role="battery")
    add("rule1", "rule", x0=P, x1=W - P, y=Y_R1, dash=2, gap=2, color="#105228")
    add("cmd.date", "text", x=P, y=Y_CMD, anchor="ls", font="mono18", size=S18,
        advance=A18, color="#1E9648", sample="$ date")
    add("cmd.comment", "text", x=P + A18 * 6 + 6, y=Y_CMD, anchor="ls", font="mono18",
        size=S18, advance=A18, color="#105228", sample="# local")
    add("time", "digits", sheet="big", x=(W - BIG_A * 5) // 2, y=Y_TIME,
        anchor="baseline", advance=BIG_A, size=BIG, color="#E2FFEC",
        sample="08:24", note="HH:MM 共 5 字（4 数字 + 冒号），整行 160px 居中；"
                             "空格位不放字；12 小时制时 AM/PM 放 date 行")
    add("date", "text", x=P, y=Y_DATE, anchor="ls", font="mono20", size=S20,
        advance=A20, color="#1E9648", sample="WED 12JUN25",
        note="≤12 字符（12×12=144px）；12 小时制改成 'WED 12JUN2025 AM' 需 15 字符 → 换 16px")
    add("cmd.sec", "text", x=W - P, y=Y_CMD, anchor="rs", font="mono16", size=S16,
        advance=A16, color="#36FF74", sample=":37", role="second",
        note="秒只在命令行动；静态表盘可关掉，减少每秒唤醒")
    add("rule2", "rule", x0=P, x1=W - P, y=Y_R2, dash=1, gap=3, color="#105228")
    add("resmon.hdr", "text", x=P, y=Y_HD, anchor="ls", font="mono18", size=S18,
        advance=A18, color="#36FF74", sample="# resmon")
    add("resmon.clock", "text", x=W - P, y=Y_HD, anchor="rs", font="mono18", size=S18,
        advance=A18, color="#105228", sample="08:24")
    labels = ["BAT", "HR", "STEP", "KCAL", "TEMP"]
    roles = ["battery", "heart_rate", "steps", "calories", "weather"]
    vals = ["86%", "72", "8204", "312", "27C"]
    for i in range(5):
        y = Y_ROW0 + i * ROW_STEP
        add(f"row{i}.label", "text", x=P, y=y, anchor="ls", font="mono18", size=S18,
            advance=A18, color="#1E9648", sample=labels[i])
        add(f"row{i}.bar", "bar", x=P + A18 * 5 + 8, y=y - 12, w=60, h=10, segs=10, gap=2,
            color="#36FF74", off="#105228", role=roles[i],
            note="心率行换 wave 波形（8 根柱，宽 6、间距 2）")
        add(f"row{i}.value", "text", x=W - P, y=y, anchor="rs", font="mono18", size=S18,
            advance=A18, color="#36FF74", sample=vals[i], role=roles[i])
    add("log.hdr", "text", x=P, y=Y_LOGHD, anchor="ls", font="mono16", size=S16,
        advance=A16, color="#1E9648", sample="$ tail band.log",
        note="16px 行宽 ≤17 字符；日志行由系统事件刷新（非每秒跳数）")
    for i in range(4):
        add(f"log{i}", "text", x=P, y=Y_LOG0 + i * LOG_STEP, anchor="ls", font="mono16",
            size=S16, advance=A16, color="#1E9648", sample="[08:20] btn1 wake",
            role="event_log")
    add("rule3", "rule", x0=P, x1=W - P, y=Y_R3, dash=2, gap=2, color="#105228")
    add("uptime.cmd", "text", x=P, y=Y_UP, anchor="ls", font="mono18", size=S18,
        advance=A18, color="#1E9648", sample="$ uptime")
    add("uptime.val", "text", x=W - P, y=Y_UP, anchor="rs", font="mono18", size=S18,
        advance=A18, color="#36FF74", sample="12d 3h")
    add("prompt", "text", x=P, y=Y_PROMPT, anchor="ls", font="mono18", size=S18,
        advance=A18, color="#36FF74", sample="root@band9:~$")
    add("cursor", "rect", x=P + A18 * 13 + 5, y=Y_PROMPT - 12, w=9, h=14,
        color="#40E8D6", role="blink", note="200ms 亮 / 300ms 灭；静态面可常亮")
    add("tail", "text", x=P, y=Y_TAIL, anchor="ls", font="mono16", size=S16,
        advance=A16, color="#105228", sample="bt:1 dnd:0 ala:1")

    return dict(
        canvas=dict(w=W, h=H, model="Xiaomi Smart Band 9 / 9 NFC", panel="AMOLED",
                    aspect="胶囊竖屏", safe_inset=P,
                    note="圆角区域不放关键信息；四周留 10px 安全边距，文字最右/最下不出 182/472"),
        palette=dict(bg="#040705", g0="#E2FFEC", g1="#36FF74", g2="#1E9648",
                     g3="#105228", cyan="#40E8D6", amber="#FFB000", red="#FF5454",
                     panel="#08120C"),
        fonts=dict(mono16=dict(family="DejaVu Sans Mono", size=S16, advance=A16),
                   mono18=dict(family="DejaVu Sans Mono", size=S18, advance=A18),
                   mono20=dict(family="DejaVu Sans Mono", size=S20, advance=A20),
                   big53=dict(family="DejaVu Sans Mono Bold", size=BIG, advance=BIG_A),
                   cjk26=dict(family="SimHei / 思源黑体", size=26, advance=26)),
        glyphs=dict(big=big, small16=s16, small18=s18, small20=s20),
        elements=items,
        notify=dict(
            backdrop=dict(x=0, y=132, w=W, h=H - 132, color="#000000"),
            card=dict(x=4, y=146, w=W - 9, h=284, fill="#08120C", border="#36FF74"),
            rows=[
                dict(name="ntf.title", x=12, y=154, anchor="la", font="mono16",
                     sample="[ INCOMING ]", color="#36FF74"),
                dict(name="ntf.count", x=W - 12, y=154, anchor="ra", font="mono16",
                     sample="1/3", color="#105228"),
                dict(name="ntf.rule", x0=8, x1=W - 9, y=174, dash=2, gap=2),
                dict(name="ntf.app", x=12, y=184, anchor="la", font="mono16",
                     sample="WECHAT", color="#1E9648"),
                dict(name="ntf.time", x=W - 12, y=184, anchor="ra", font="mono16",
                     sample="08:24", color="#105228"),
                dict(name="ntf.sender", x=12, y=204, anchor="la", font="cjk26",
                     sample="老王", color="#36FF74"),
                dict(name="ntf.line1", x=12, y=242, anchor="la", font="cjk22",
                     sample="晚上 7 点老地方", color="#36FF74"),
                dict(name="ntf.line2", x=12, y=274, anchor="la", font="cjk22",
                     sample="到了给你留位", color="#1E9648"),
                dict(name="ntf.meta", x=12, y=306, anchor="la", font="mono16",
                     sample="seen:1 unread:2", color="#105228"),
                dict(name="ntf.keys", x=10, y=366, w=52, h=18, gap=6,
                     sample=["^ESC", "O VIEW", "SWIPE>"]),
                dict(name="ntf.prompt", x=12, y=404, anchor="la", font="mono16",
                     sample="$ reply >", color="#105228"),
            ],
        ),
        aod=dict(
            bg="#000000",
            time=dict(y=232, x=(W - BIG_A * 5) // 2, font="big53", color="#2C6840",
                      sample="08:24", dim_note="亮度 ≈ 28% 的 G1，避免全亮烧屏"),
            shake=dict(offsets=[0, 2, 4, 2], period_min=60,
                       note="每小时把整块内容按 offsets 循环下移，1px/步，防 AMOLED 残影"),
            rule=dict(y=266, x0=52, x1=140, color="#122A18", dash=2, gap=4),
            battery=dict(x=60, y=300, cell=7, gap=5, lit_color="#1A3E22",
                         low_color="#966800", note="4 格，<20% 转琥珀"),
            cursor=dict(x=130, y=318, w=14, h=6, color="#40E8D6",
                        note="AOD 内 1Hz 闪；静态面可常亮"),
        ),
    )


def build_spec(layout):
    out = ["# 终端表盘 · 坐标表 (192×490)", "",
           "所有 x/y 均为像素，`anchor=` 说明基线对齐方式：`ls` 左-基线，"
           "`rs` 右-基线，`la` 左-顶，`ra` 右-顶。", "",
           "| # | 名称 | 类型 | x | y | 宽高 | 字号/步进 | 颜色 | 示例 |",
           "|---|------|------|---|---|------|-----------|------|------|"]
    for i, e in enumerate(layout["elements"], 1):
        fsize = ""
        if e.get("size"):
            fsize = f"{e['size']}px / step {e.get('advance', '')}"
        wh = f"{e['w']}×{e.get('h', '')}" if e.get("w") else ""
        x = e.get("x", e.get("x0", ""))
        y = e.get("y", "")
        out.append(f"| {i} | `{e['name']}` | {e['kind']} | {x} | {y} | {wh} | "
                   f"{fsize} | `{e.get('color', '')}` | {e.get('sample', '')} |")
    # 通知卡
    ntf = layout.get("notify") or {}
    out += ["", "## 通知卡（preview_notify.png）", "",
            "| 元素 | x | y | 属性 |", "|---|---|---|---|"]
    bd, cd = ntf.get("backdrop", {}), ntf.get("card", {})
    out.append(f"| 遮罩 | {bd.get('x')} | {bd.get('y')} | {bd.get('w')}×{bd.get('h')} "
               f"`{bd.get('color')}` |")
    out.append(f"| 卡片 | {cd.get('x')} | {cd.get('y')} | {cd.get('w')}×{cd.get('h')} "
               f"fill `{cd.get('fill')}` / border `{cd.get('border')}` |")
    for r in ntf.get("rows", []):
        out.append(f"| `{r['name']}` | {r.get('x', r.get('x0', ''))} | {r.get('y', '')} | "
                   f"{r.get('font', 'rule')} · {r.get('color', '-')} · {r.get('sample', '')} |")
    # AOD
    aod = layout.get("aod") or {}
    t, ru, ba, cu = aod.get("time", {}), aod.get("rule", {}), \
        aod.get("battery", {}), aod.get("cursor", {})
    out += ["", "## AOD 息屏（preview_aod.png）", "",
            "| 元素 | x | y | 属性 |", "|---|---|---|---|",
            f"| 时间 | {t.get('x')} | {t.get('y')} | {t.get('font')} `{t.get('color')}` "
            f"（≈28% 亮度）|",
            f"| 分隔线 | {ru.get('x0')}→{ru.get('x1')} | {ru.get('y')} | dash "
            f"{ru.get('dash')}/{ru.get('gap')} `{ru.get('color')}` |",
            f"| 电量 4 格 | {ba.get('x')} | {ba.get('y')} | cell {ba.get('cell')} gap "
            f"{ba.get('gap')} `${ba.get('lit_color')}` |",
            f"| 光标 | {cu.get('x')} | {cu.get('y')} | {cu.get('w')}×{cu.get('h')} "
            f"`{cu.get('color')}` |",
            "",
            f"* 像素位移：offsets = {aod.get('shake', {}).get('offsets')}，"
            f"每 {aod.get('shake', {}).get('period_min')} 分钟（即每小时）下移一档。*", ""]

    out += ["", "## 行坐标总表", "",
            f"| 区块 | y (基线) |", "|---|---|",
            f"| 状态行 | {Y_STAT} |", f"| 细虚线 | {Y_R1} |", f"| `$ date` + 秒 | {Y_CMD} |",
            f"| 大号时间 | {Y_TIME} |", f"| 日期 | {Y_DATE} |",
            f"| 点线 | {Y_R2} |", f"| resmon 标题 | {Y_HD} |",
            f"| 指标 5 行 | {Y_ROW0} 起，步进 {ROW_STEP} |",
            f"| 日志标题 | {Y_LOGHD} |", f"| 日志 4 行 | {Y_LOG0} 起，步进 {LOG_STEP} |",
            f"| 虚线 | {Y_R3} |", f"| uptime | {Y_UP} |",
            f"| 提示符 + 光标 | {Y_PROMPT} |", f"| 状态位 | {Y_TAIL} |", ""]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ main
def save(img, name):
    img.save(os.path.join(OUT, name))
    img.resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(OUT, name[:-4] + "_x3.png"))


def render(st, name, blank=False):
    im = Image.new("RGB", (W, H), BG)
    draw_common(ImageDraw.Draw(im), st, blank=blank)
    save(im, name)
    return im


def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)

    idle = render(state_idle(), "preview_idle.png")
    base = render(state_idle(), "assets/base_tmp.png", blank=True)
    os.remove(os.path.join(OUT, "assets", "base_tmp.png"))
    os.remove(os.path.join(OUT, "assets", "base_tmp_x3.png"))
    base.save(os.path.join(OUT, "assets", "base.png"))
    base.resize((W * 3, H * 3), Image.NEAREST).save(
        os.path.join(OUT, "assets", "base_x3.png"))
    render(state_lowbat(), "preview_lowbat.png")
    render(state_sport(), "preview_sport.png")
    render(state_boot(), "preview_boot.png")

    album = dict(state_idle())
    album["hhmm"] = " " * 5
    render(album, "preview_album.png")

    save(draw_aod(shake=0), "preview_aod.png")
    save(draw_aod(hhmm="23:59", batt=15, shake=2), "preview_aod_shake.png")

    notify = Image.new("RGB", (W, H), BG)
    draw_common(ImageDraw.Draw(notify), state_idle())
    draw_notify(notify)
    save(notify, "preview_notify.png")

    a = os.path.join(OUT, "assets")
    # 直接用整图（相册表盘 / 一键出图）
    shutil.copyfile(os.path.join(OUT, "assets", "base.png"),
                    os.path.join(OUT, "assets", "watchface_base_192x490.png"))
    shutil.copyfile(os.path.join(OUT, "preview_album.png"),
                    os.path.join(OUT, "assets", "watchface_album_192x490.png"))
    shutil.copyfile(os.path.join(OUT, "preview_idle.png"),
                    os.path.join(OUT, "assets", "watchface_full_192x490.png"))

    big = export_big(os.path.join(a, "big"), "assets/big")
    s16 = export_small(os.path.join(a, "small16"), "assets/small16", S16)
    s18 = export_small(os.path.join(a, "small18"), "assets/small18", S18)
    s20 = export_small(os.path.join(a, "small20"), "assets/small20", S20)
    export_icons(os.path.join(a, "icons"), "assets/icons")
    cjk = export_cjk(os.path.join(a, "cjk"), "assets/cjk")

    layout = build_layout(big, s16, s18, s20)
    layout["glyphs"]["cjk"] = cjk
    with open(os.path.join(OUT, "layout.json"), "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "spec.md"), "w", encoding="utf-8") as f:
        f.write(build_spec(layout))

    # 状态联排（交付总览图）
    names = ["preview_idle.png", "preview_notify.png", "preview_sport.png",
             "preview_lowbat.png", "preview_boot.png", "preview_aod.png"]
    sheet = Image.new("RGB", (W * len(names) + 8 * (len(names) - 1), H), (0, 0, 0))
    for i, n in enumerate(names):
        sheet.paste(Image.open(os.path.join(OUT, n)), (i * (W + 8), 0))
    sheet.save(os.path.join(OUT, "preview_all.png"))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(
        os.path.join(OUT, "preview_all_x2.png"))

    print("mono   :", F_MONO)
    print("mono_b :", F_MONOB)
    print("cjk    :", F_CJK)
    print(f"big={BIG} advance={BIG_A} | 18px step={A18} | 16px step={A16} | 20px step={A20}")


if __name__ == "__main__":
    main()

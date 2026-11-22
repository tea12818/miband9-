# 终端表盘 · 坐标表 (192×490)

所有 x/y 均为像素，`anchor=` 说明基线对齐方式：`ls` 左-基线，`rs` 右-基线，`la` 左-顶，`ra` 右-顶。

| # | 名称 | 类型 | x | y(基线) | 宽高 | 字号/步进 | 颜色 | 示例 | y(左上) |
|---|------|------|---|---|------|-----------|------|------|------|
| 1 | `status.prompt` | text | 10 | 20 |  | 18px / step 11 | `#8A8A8A` | root@band9 | 7 |
| 2 | `status.bt` | asset | 128 | 10 | 7×11 |  | `` |  |  |
| 3 | `status.pct` | text | 182 | 20 |  | 16px / step 10 | `#D4D4D4` | 86% | 8 |
| 4 | `status.batbar` | bar | 121 | 8 | 22×9 |  | `#D4D4D4` |  |  |
| 5 | `rule1` | rule | 10 | 26 |  |  | `#383838` |  |  |
| 6 | `cmd.date` | text | 10 | 45 |  | 18px / step 11 | `#8A8A8A` | $ date | 32 |
| 7 | `cmd.comment` | text | 82 | 45 |  | 18px / step 11 | `#383838` | # local | 32 |
| 8 | `time` | digits | 16 | 100 |  | 53px / step 32 | `#FFFFFF` | 08:24 | 60 |
| 9 | `date` | text | 10 | 124 |  | 20px / step 12 | `#8A8A8A` | WED 12JUN25 | 109 |
| 10 | `cmd.sec` | text | 182 | 45 |  | 16px / step 10 | `#D4D4D4` | :37 | 33 |
| 11 | `rule2` | rule | 10 | 134 |  |  | `#383838` |  |  |
| 12 | `resmon.hdr` | text | 10 | 156 |  | 18px / step 11 | `#D4D4D4` | # resmon | 143 |
| 13 | `resmon.clock` | text | 182 | 156 |  | 18px / step 11 | `#383838` | 08:24 | 143 |
| 14 | `row0.label` | text | 10 | 182 |  | 18px / step 11 | `#8A8A8A` | BAT | 169 |
| 15 | `row0.bar` | bar | 73 | 170 | 60×10 |  | `#D4D4D4` |  |  |
| 16 | `row0.value` | text | 182 | 182 |  | 18px / step 11 | `#D4D4D4` | 86% | 169 |
| 17 | `row1.label` | text | 10 | 207 |  | 18px / step 11 | `#8A8A8A` | HR | 194 |
| 18 | `row1.bar` | bar | 73 | 195 | 60×10 |  | `#D4D4D4` |  |  |
| 19 | `row1.value` | text | 182 | 207 |  | 18px / step 11 | `#D4D4D4` | 72 | 194 |
| 20 | `row2.label` | text | 10 | 232 |  | 18px / step 11 | `#8A8A8A` | STEP | 219 |
| 21 | `row2.bar` | bar | 73 | 220 | 60×10 |  | `#D4D4D4` |  |  |
| 22 | `row2.value` | text | 182 | 232 |  | 18px / step 11 | `#D4D4D4` | 8204 | 219 |
| 23 | `row3.label` | text | 10 | 257 |  | 18px / step 11 | `#8A8A8A` | KCAL | 244 |
| 24 | `row3.bar` | bar | 73 | 245 | 60×10 |  | `#D4D4D4` |  |  |
| 25 | `row3.value` | text | 182 | 257 |  | 18px / step 11 | `#D4D4D4` | 312 | 244 |
| 26 | `row4.label` | text | 10 | 282 |  | 18px / step 11 | `#8A8A8A` | TEMP | 269 |
| 27 | `row4.bar` | bar | 73 | 270 | 60×10 |  | `#D4D4D4` |  |  |
| 28 | `row4.value` | text | 182 | 282 |  | 18px / step 11 | `#D4D4D4` | 27C | 269 |
| 29 | `log.hdr` | text | 10 | 306 |  | 16px / step 10 | `#8A8A8A` | $ tail band.log | 294 |
| 30 | `log0` | text | 10 | 326 |  | 16px / step 10 | `#8A8A8A` | [08:20] btn1 wake | 314 |
| 31 | `log1` | text | 10 | 344 |  | 16px / step 10 | `#8A8A8A` | [08:20] btn1 wake | 332 |
| 32 | `log2` | text | 10 | 362 |  | 16px / step 10 | `#8A8A8A` | [08:20] btn1 wake | 350 |
| 33 | `log3` | text | 10 | 380 |  | 16px / step 10 | `#8A8A8A` | [08:20] btn1 wake | 368 |
| 34 | `rule3` | rule | 10 | 392 |  |  | `#383838` |  |  |
| 35 | `uptime.cmd` | text | 10 | 410 |  | 18px / step 11 | `#8A8A8A` | $ uptime | 397 |
| 36 | `uptime.val` | text | 182 | 410 |  | 18px / step 11 | `#D4D4D4` | 12d 3h | 397 |
| 37 | `prompt` | text | 10 | 448 |  | 18px / step 11 | `#D4D4D4` | root@band9:~$ | 435 |
| 38 | `cursor` | rect | 158 | 436 | 9×14 |  | `#FFFFFF` |  |  |
| 39 | `tail` | text | 10 | 472 |  | 16px / step 10 | `#383838` | bt:1 dnd:0 ala:1 | 460 |

## 通知卡（preview_notify.png）

| 元素 | x | y | 属性 |
|---|---|---|---|
| 遮罩 | 0 | 132 | 192×358 `#000000` |
| 卡片 | 4 | 146 | 183×284 fill `#101010` / border `#D4D4D4` |
| `ntf.title` | 12 | 154 | mono16 · #D4D4D4 · [ INCOMING ] |
| `ntf.count` | 180 | 154 | mono16 · #383838 · 1/3 |
| `ntf.rule` | 8 | 174 | rule · - ·  |
| `ntf.app` | 12 | 184 | mono16 · #8A8A8A · WECHAT |
| `ntf.time` | 180 | 184 | mono16 · #383838 · 08:24 |
| `ntf.sender` | 12 | 204 | cjk26 · #D4D4D4 · 老王 |
| `ntf.line1` | 12 | 242 | cjk22 · #D4D4D4 · 晚上 7 点老地方 |
| `ntf.line2` | 12 | 274 | cjk22 · #8A8A8A · 到了给你留位 |
| `ntf.meta` | 12 | 306 | mono16 · #383838 · seen:1 unread:2 |
| `ntf.keys` | 10 | 366 | rule · - · ['^ESC', 'O VIEW', 'SWIPE>'] |
| `ntf.prompt` | 12 | 404 | mono16 · #383838 · $ reply > |

## AOD 息屏（preview_aod.png）

| 元素 | x | y | 属性 |
|---|---|---|---|
| 时间 | 16 | 232 | big53 `#464646` （≈28% 亮度）|
| 分隔线 | 52→140 | 266 | dash 2/4 `#181818` |
| 电量 4 格 | 60 | 300 | cell 7 gap 5 `$#585858` |
| 光标 | 130 | 318 | 14×6 `#969696` |

* 像素位移：offsets = [0, 2, 4, 2]，每 60 分钟（即每小时）下移一档。*


## 行坐标总表

| 区块 | y (基线) |
|---|---|
| 状态行 | 20 |
| 细虚线 | 26 |
| `$ date` + 秒 | 45 |
| 大号时间 | 100 |
| 日期 | 124 |
| 点线 | 134 |
| resmon 标题 | 156 |
| 指标 5 行 | 182 起，步进 25 |
| 日志标题 | 306 |
| 日志 4 行 | 326 起，步进 18 |
| 虚线 | 392 |
| uptime | 410 |
| 提示符 + 光标 | 448 |
| 状态位 | 472 |


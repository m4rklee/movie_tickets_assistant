# 模型评测报告：claude-sonnet-4-5

- 提供方：Anthropic via AIHubMix
- 参考票张数：19
- 成功解析并打分：19
- API 失败：0
- JSON 解析失败：0
- 缺少评测记录：0
- **核心字段准确率**：60.2% （80/133）
- **全字段准确率**（仅计参考非空）：52.6% （90/171）
- 参考为空但模型填了值：2 次
- **Token 消耗**：Token 合计 39,398 (输入 36,898 / 输出 2,500)，均 2,074/次；耗时合计 322.5s，均 16.98s/次；预估费用（图片输入+文本输出）合计 ¥1.07，均 ¥0.0562/次

## 分字段准确率（参考非空）

| 字段 | 正确/总数 | 准确率 |
|------|-----------|--------|
| `movie_name` | 4/19 | 21.1% |
| `ticket_date` | 12/19 | 63.2% |
| `start_time` | 17/19 | 89.5% |
| `end_time` | 0/0 | n/a |
| `movie_duration` | 2/10 | 20.0% |
| `price` | 16/19 | 84.2% |
| `cinema_name` | 8/19 | 42.1% |
| `cinema_address` | 0/9 | 0.0% |
| `cinema_hall` | 11/19 | 57.9% |
| `seat_row` | 11/19 | 57.9% |
| `seat_col` | 9/19 | 47.4% |

## 逐图明细

### IMG_0001.jpeg
- Token/耗时/费用：total=2072, prompt=1942, completion=130, 22.762s, ≈¥0.0560
- 状态：ok
- 错误字段：`movie_duration`, `cinema_name`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `小城之春` | `小城之春` | ✓ |
| `ticket_date` | `2025-04-22` | `2025-04-22 18:30:00` | ✓ |
| `start_time` | `18:30` | `18:30:00` | ✓ |
| `movie_duration` | `98` | `None` | ✗ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `万象影城(北京通州万象汇杜比巨幕店)` | `万象影城(北京通州万达广场店)` | ✗ |
| `cinema_hall` | `3号杜比全景声厅` | `3号杜比全景声厅` | ✓ |
| `seat_row` | `3` | `3` | ✓ |
| `seat_col` | `9` | `9` | ✓ |

### IMG_0002.jpeg
- Token/耗时/费用：total=2083, prompt=1942, completion=141, 23.535s, ≈¥0.0572
- 状态：ok
- 错误字段：无（在参考非空字段上全对）

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `安德烈·卢布廖夫` | `安德烈·卢布廖夫` | ✓ |
| `ticket_date` | `2025-04-25 12:10:00` | `2025-04-25 12:10:00` | ✓ |
| `start_time` | `12:10:00` | `12:10:00` | ✓ |
| `movie_duration` | `183` | `183` | ✓ |
| `price` | `100` | `100.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `1` | `1` | ✓ |
| `seat_col` | `6` | `6` | ✓ |

### IMG_0003.jpeg
- Token/耗时/费用：total=2047, prompt=1942, completion=105, 20.542s, ≈¥0.0533
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `movie_duration`, `cinema_name`, `cinema_hall`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `劳工之爱情 4K+盘丝洞 4K 活动` | `误杀2` | ✗ |
| `ticket_date` | `2025-04-27 20:45:00` | `2025-01-27 20:45:00` | ✗ |
| `start_time` | `20:45` | `20:45` | ✓ |
| `movie_duration` | `71` | `None` | ✗ |
| `price` | `100` | `100.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `北京百老汇电影中心` | ✗ |
| `cinema_hall` | `1号厅` | `None` | ✗ |
| `seat_row` | `5` | `1` | ✗ |
| `seat_col` | `1` | `5` | ✗ |

### IMG_0004.jpeg
- Token/耗时/费用：total=2066, prompt=1942, completion=124, 10.482s, ≈¥0.0553
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `movie_duration`, `cinema_name`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `董夫人 (4K)` | `老人（4K）` | ✗ |
| `ticket_date` | `2026-04-25 17:05:00` | `2025-01-25 17:05:00` | ✗ |
| `start_time` | `17:05` | `17:05:00` | ✓ |
| `movie_duration` | `94` | `None` | ✗ |
| `price` | `80` | `80.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `首都电影院西单大悦城店` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `4` | `4` | ✓ |
| `seat_col` | `14` | `14` | ✓ |

### IMG_0005.jpeg
- Token/耗时/费用：total=2079, prompt=1942, completion=137, 15.987s, ≈¥0.0567
- 状态：ok
- 错误字段：无（在参考非空字段上全对）

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `涡流` | `涡流` | ✓ |
| `ticket_date` | `2025-04-26 15:40:00` | `2025-04-26 15:40:00` | ✓ |
| `start_time` | `15:40:00` | `15:40:00` | ✓ |
| `movie_duration` | `88` | `88` | ✓ |
| `price` | `70` | `70.0` | ✓ |
| `cinema_name` | `金泉港国际影城IMAX` | `金泉港国际影城IMAX` | ✓ |
| `cinema_hall` | `7号杜比全景声影厅` | `7号杜比全景声影厅` | ✓ |
| `seat_row` | `5` | `5` | ✓ |
| `seat_col` | `9` | `9` | ✓ |

### IMG_0006.jpeg
- Token/耗时/费用：total=2054, prompt=1942, completion=112, 16.666s, ≈¥0.0540
- 状态：ok
- 错误字段：`movie_name`, `movie_duration`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `神女 4K 映前` | `第74届戛纳电影节影展` | ✗ |
| `ticket_date` | `2025-04-24 18:00:00` | `2025-04-24 18:00:00` | ✓ |
| `start_time` | `18:00:00` | `18:00:00` | ✓ |
| `movie_duration` | `83` | `None` | ✗ |
| `price` | `70` | `70.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `4` | `None` | ✗ |
| `seat_col` | `11` | `None` | ✗ |

### IMG_0007.jpeg
- Token/耗时/费用：total=2051, prompt=1942, completion=109, 17.305s, ≈¥0.0537
- 状态：ok
- 错误字段：`ticket_date`, `movie_duration`, `price`, `cinema_name`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `光之幻影 4K` | `光之幻影 4K` | ✓ |
| `ticket_date` | `2025-04-20 20:00:00` | `2025-04-20 20:30:00` | ✗ |
| `start_time` | `20:30` | `20:30` | ✓ |
| `movie_duration` | `79` | `None` | ✗ |
| `price` | `70` | `0.74` | ✗ |
| `cinema_name` | `北京剧院` | `None` | ✗ |
| `cinema_hall` | `大剧场4K激光厅` | `大剧场4K激光厅` | ✓ |
| `seat_row` | `6` | `6` | ✓ |
| `seat_col` | `3` | `3` | ✓ |

### IMG_0008.jpeg
- Token/耗时/费用：total=2072, prompt=1942, completion=130, 19.878s, ≈¥0.0560
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `movie_duration`, `cinema_name`, `cinema_hall`, `seat_row`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `侠盗猎车哈姆雷特` | `哥斯拉大战金刚2：帝国崛起` | ✗ |
| `ticket_date` | `2025-04-20 15:00:00` | `2025-04-01 15:00:00` | ✗ |
| `start_time` | `15:00:00` | `15:00` | ✓ |
| `movie_duration` | `89` | `None` | ✗ |
| `price` | `70` | `70.0` | ✓ |
| `cinema_name` | `金泉港国际影城IMAX` | `上影影城` | ✗ |
| `cinema_hall` | `1号IMAX影厅` | `7号厅IMAX` | ✗ |
| `seat_row` | `6` | `9` | ✗ |
| `seat_col` | `15` | `15` | ✓ |

### IMG_0009.jpeg
- Token/耗时/费用：total=2059, prompt=1942, completion=117, 24.395s, ≈¥0.0546
- 状态：ok
- 错误字段：`movie_name`, `movie_duration`, `cinema_name`, `cinema_hall`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `唯有声音留存` | `听说地球要完了` | ✗ |
| `ticket_date` | `2025-04-19 18:30:00` | `2025-04-19 18:30:00` | ✓ |
| `start_time` | `18:30:00` | `18:30` | ✓ |
| `movie_duration` | `89` | `None` | ✗ |
| `price` | `70` | `70.0` | ✓ |
| `cinema_name` | `首都电影院（西单店 LED巨幕）` | `首都电影院` | ✗ |
| `cinema_hall` | `9号厅（LED）` | `9厅(LED)` | ✗ |
| `seat_row` | `4` | `4` | ✓ |
| `seat_col` | `7` | `7` | ✓ |

### IMG_0011.jpeg
- Token/耗时/费用：total=2058, prompt=1942, completion=116, 16.824s, ≈¥0.0545
- 状态：ok
- 错误字段：`movie_name`, `movie_duration`, `cinema_name`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `返魂香` | `逆行人生` | ✗ |
| `ticket_date` | `2025-04-19 16:00:00` | `2025-04-19 16:00:00` | ✓ |
| `start_time` | `16:00:00` | `16:00:00` | ✓ |
| `movie_duration` | `98` | `None` | ✗ |
| `price` | `60` | `60.0` | ✓ |
| `cinema_name` | `奋逗影剧院` | `首都电影院` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `5` | `5` | ✓ |
| `seat_col` | `9` | `9` | ✓ |

### IMG_0012.jpeg
- Token/耗时/费用：total=2091, prompt=1942, completion=149, 18.603s, ≈¥0.0580
- 状态：ok
- 错误字段：`movie_name`, `cinema_name`, `cinema_address`, `cinema_hall`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `里斯本丸沉没（2024）` | `八个` | ✗ |
| `ticket_date` | `2025-08-15` | `2025-08-15 19:00:00` | ✓ |
| `start_time` | `19:00` | `19:00` | ✓ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院大礼堂` | ✗ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `2号厅` | ✗ |
| `seat_row` | `2` | `None` | ✗ |
| `seat_col` | `2` | `None` | ✗ |

### IMG_0013.jpeg
- Token/耗时/费用：total=2077, prompt=1942, completion=135, 14.661s, ≈¥0.0565
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `start_time`, `price`, `cinema_name`, `cinema_address`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `神女 (1934)` | `中国乒乓之绝地反击` | ✗ |
| `ticket_date` | `2025-03-05` | `2025-01-17 19:40:00` | ✗ |
| `start_time` | `19:00` | `19:40:00` | ✗ |
| `movie_duration` | `None` | `140` | ✗ |
| `price` | `10` | `19.9` | ✗ |
| `cinema_name` | `中国电影资料馆艺术影院` | `嘉禾影城` | ✗ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `4` | `7` | ✗ |
| `seat_col` | `7` | `6` | ✗ |

### IMG_0014.jpeg
- Token/耗时/费用：total=2073, prompt=1942, completion=131, 13.719s, ≈¥0.0561
- 状态：ok
- 错误字段：`movie_name`, `cinema_address`, `cinema_hall`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `英雄本色（4K，1986）` | `中国电影资料馆艺术影院` | ✗ |
| `ticket_date` | `2025-04-06 13:30:00` | `2025-04-06 13:30:00` | ✓ |
| `start_time` | `13:30:00` | `13:30` | ✓ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_address` | `北京市朝阳区百子湾南二路2号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `4号厅` | ✗ |
| `seat_row` | `4` | `4` | ✓ |
| `seat_col` | `12` | `1986` | ✗ |

### IMG_0015.jpeg
- Token/耗时/费用：total=2068, prompt=1942, completion=126, 14.541s, ≈¥0.0556
- 状态：ok
- 错误字段：`movie_name`, `cinema_name`, `cinema_address`, `cinema_hall`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `武松与潘金莲 ( 1938 )` | `武汉日夜` | ✗ |
| `ticket_date` | `2025-03-11` | `2025-03-11 19:00:00` | ✓ |
| `start_time` | `19:00` | `19:00` | ✓ |
| `price` | `30` | `30.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院大兴华` | ✗ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `1938` | ✗ |
| `seat_row` | `7` | `7` | ✓ |
| `seat_col` | `5` | `1` | ✗ |

### IMG_0016.jpeg
- Token/耗时/费用：total=2090, prompt=1942, completion=148, 8.645s, ≈¥0.0579
- 状态：ok
- 错误字段：`movie_name`, `cinema_address`, `cinema_hall`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `铁扇公主（4K，1941）` | `沙丘2` | ✗ |
| `ticket_date` | `2024-09-08 13:30` | `2024-09-08 13:30:00` | ✓ |
| `start_time` | `13:30` | `13:30` | ✓ |
| `movie_duration` | `None` | `0` | ✗ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_address` | `北京市朝阳区百子湾南二路2号` | `` | ✗ |
| `cinema_hall` | `1号厅` | `铁幕公井(4K，1941)` | ✗ |
| `seat_row` | `3` | `15` | ✗ |
| `seat_col` | `11` | `0` | ✗ |

### IMG_0018.jpeg
- Token/耗时/费用：total=2075, prompt=1942, completion=133, 17.15s, ≈¥0.0563
- 状态：ok
- 错误字段：`movie_name`, `cinema_address`, `cinema_hall`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `麦克白 ( 2025 )` | `关于我和鬼变成家人这件事` | ✗ |
| `ticket_date` | `2025-03-16 19:00:00` | `2025-03-16 19:00:00` | ✓ |
| `start_time` | `19:00` | `19:00:00` | ✓ |
| `price` | `120` | `120.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `2号厅` | ✗ |
| `seat_row` | `2` | `2` | ✓ |
| `seat_col` | `9` | `1` | ✗ |

### IMG_0019.jpeg
- Token/耗时/费用：total=2091, prompt=1942, completion=149, 20.503s, ≈¥0.0580
- 状态：ok
- 错误字段：`movie_name`, `cinema_address`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `万里长城 (1957)` | `万里长城（1957）` | ✗ |
| `ticket_date` | `2024-10-27 18:30:00` | `2024-10-27 18:30:00` | ✓ |
| `start_time` | `18:30:00` | `18:30:00` | ✓ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `北京市海淀区文慧园3号` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `6` | `6` | ✓ |
| `seat_col` | `9` | `9` | ✓ |

### IMG_0020.jpeg
- Token/耗时/费用：total=2114, prompt=1942, completion=172, 15.752s, ≈¥0.0605
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `cinema_name`, `cinema_address`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `粉色火烈鸟之惑（4K，2020...` | `紧急救援之魔鬼之海（4K，2020）` | ✗ |
| `ticket_date` | `2024-10-06 13:30` | `2024-10-05 13:30:00` | ✗ |
| `start_time` | `13:30` | `13:30:00` | ✓ |
| `price` | `40` | `40.0` | ✓ |
| `cinema_name` | `中国电影资料馆艺术影院` | `淘票票` | ✗ |
| `cinema_address` | `北京市朝阳区百子湾南二路2号` | `小榄镇中子大街庆丰三路` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `5` | `11` | ✗ |
| `seat_col` | `7` | `5` | ✗ |

### IMG_0022.jpeg
- Token/耗时/费用：total=2078, prompt=1942, completion=136, 10.578s, ≈¥0.0566
- 状态：ok
- 错误字段：`movie_name`, `ticket_date`, `start_time`, `price`, `cinema_address`, `seat_row`, `seat_col`

| 字段 | 参考 | 模型 | 结果 |
|------|------|------|------|
| `movie_name` | `英雄本色 4K（1986）` | `哪吒之魔童闹海4K（1986）` | ✗ |
| `ticket_date` | `2025-07-03 19:00:00` | `2025-07-03 16:00:00` | ✗ |
| `start_time` | `19:00` | `16:00:00` | ✗ |
| `price` | `50` | `55.0` | ✗ |
| `cinema_name` | `中国电影资料馆艺术影院` | `中国电影资料馆艺术影院` | ✓ |
| `cinema_address` | `北京市海淀区小西天文慧园路3号` | `None` | ✗ |
| `cinema_hall` | `1号厅` | `1号厅` | ✓ |
| `seat_row` | `4` | `11` | ✗ |
| `seat_col` | `7` | `5` | ✗ |

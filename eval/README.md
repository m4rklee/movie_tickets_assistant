# FilmArchive 票夹评测集

## 指标定义

| 指标 | 计算方式 |
|------|----------|
| 字段准确率 | 预测值与 `expected.json` 完全一致（日期/价格规范化后） / 该 case 字段数 |
| 核心字段召回 | 片名、日期、影厅、价格 全对视为 1，否则 0 |
| 幻觉 | 预测含 expected 中不存在的场次/价格，或 missing 字段被编造 |
| 耗时 | Dify 运行到输出（秒） |

## 通过线（MVP）

| 类型 | 阈值 |
|------|------|
| 核心字段（片名、日期、影厅、价格） | ≥ 95% |
| 电子：时间、支付状态 | ≥ 90% |
| 纸质：座位 | ≥ 90% |

## 目录结构

```
eval/cases/
  case_001_electronic/
    README.md
    expected.json      # 人工标注真值
    ticket.jpg         # 需自行放入脱敏票样（gitignore）
  ...
eval/results/
  scorecard.csv
```

## 运行评测

1. 将真实票图放入各 case 目录（勿提交含订单号/手机号的原图）
2. 在 Dify 运行 ParseTicket（仅识别，不写库）或完整链路
3. 将输出 JSON 填入 `eval/results/{case_id}_parse.json`
4. 运行 `python eval/run_scorecard.py` 更新 scorecard
5. 填写主观列：结构清晰、愿再用

## Case 列表

| ID | 类型 | 说明 |
|----|------|------|
| case_001_electronic | 电子 | 标准截图 |
| case_002_electronic | 电子 | 标准截图 |
| case_003_electronic | 电子 | 待支付状态 |
| case_004_electronic | 电子 | 长片名 |
| case_005_electronic | 电子 | 晚间场次 |
| case_006_paper | 纸质 | 标准拍照 |
| case_007_paper | 纸质 | 标准拍照 |
| case_008_paper | 纸质 | 弱光/阴影（挑战） |
| case_009_paper | 纸质 | 连座号 |
| case_010_paper | 纸质 | 低价场次 |

`expected.json` 为**示例标注**（虚构片名），替换票图时请同步改真值。

#!/usr/bin/env python3
"""Compare vision model outputs in JSONL against movie_ticket_reference.json."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "movie_ticket_reference.json"
DEFAULT_JSONL = ROOT / "github_current_project" / "vision_model_eval.jsonl"
DEFAULT_REPORT_DIR = Path(__file__).resolve().parent / "reports"
DEFAULT_PRICING = Path(__file__).resolve().parent / "model_pricing.json"
# 参考真值无效或不宜计分的样张（不参与准确率、Token、费用汇总）
DEFAULT_EXCLUDE_IMAGES: frozenset[str] = frozenset({"IMG_0017.jpeg"})

EVAL_FIELDS = [
    "movie_name",
    "ticket_date",
    "start_time",
    "end_time",
    "movie_duration",
    "price",
    "cinema_name",
    "cinema_address",
    "cinema_hall",
    "seat_row",
    "seat_col",
]

CORE_FIELDS = [
    "movie_name",
    "ticket_date",
    "start_time",
    "price",
    "cinema_hall",
    "seat_row",
    "seat_col",
]

FIELD_LABELS = {
    "movie_name": "电影名称",
    "ticket_date": "票面日期时间",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "movie_duration": "时长（分钟）",
    "price": "票价",
    "cinema_name": "影院名称",
    "cinema_address": "影院地址",
    "cinema_hall": "影厅",
    "seat_row": "座位排号",
    "seat_col": "座位座号",
}

JSONL_RECORD_FIELDS = [
    ("image", "图片路径"),
    ("provider", "模型提供方"),
    ("model", "模型 ID"),
    ("elapsed_seconds", "耗时（秒）"),
    ("raw_output", "模型原始文本输出"),
    ("parsed_json", "解析后的 JSON"),
    ("parse_error", "JSON 解析错误"),
    ("error", "API / 权限错误"),
    ("usage", "Token 用量"),
]


def load_reference(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "reference" in data and isinstance(data["reference"], dict):
        data = data["reference"]
    return data


def parse_exclude_images(value: str | None) -> frozenset[str]:
    if not value or not value.strip():
        return frozenset()
    return frozenset(part.strip() for part in value.split(",") if part.strip())


def filter_reference(
    reference: dict[str, dict[str, Any]],
    exclude: frozenset[str],
) -> dict[str, dict[str, Any]]:
    if not exclude:
        return reference
    return {k: v for k, v in reference.items() if k not in exclude}


def filter_records_for_reference(
    records: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    keys = set(reference.keys())
    return {k: v for k, v in records.items() if k in keys}


def load_model_pricing(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if not path.exists():
        return {}, {}
    data = json.loads(path.read_text(encoding="utf-8"))
    models = data.get("models", {})
    meta = {k: v for k, v in data.items() if k != "models"}
    usd_rate = float(meta.get("usd_cny_rate", 7.2))
    for cfg in models.values():
        if "input_per_1m_usd" in cfg:
            cfg.setdefault(
                "input_per_1m_cny",
                float(cfg["input_per_1m_usd"]) * usd_rate,
            )
            cfg.setdefault(
                "output_per_1m_cny",
                float(cfg["output_per_1m_usd"]) * usd_rate,
            )
    return models, meta


def resolve_rates_for_request(
    prompt_tokens: int | None,
    rates: dict[str, Any],
    usd_cny_rate: float = 7.2,
) -> tuple[float, float, str | None]:
    """Return (image_input_rate, text_output_rate, tier_label) per 1M tokens in CNY."""
    tiers = rates.get("tiers")
    if tiers:
        n = prompt_tokens or 0
        for tier in tiers:
            cap = tier.get("max_input_tokens")
            if cap is None or n <= int(cap):
                return (
                    float(tier["input_per_1m_cny"]),
                    float(tier["output_per_1m_cny"]),
                    tier.get("label"),
                )
        last = tiers[-1]
        return (
            float(last["input_per_1m_cny"]),
            float(last["output_per_1m_cny"]),
            last.get("label"),
        )
    if "input_per_1m_usd" in rates:
        return (
            float(rates["input_per_1m_usd"]) * usd_cny_rate,
            float(rates["output_per_1m_usd"]) * usd_cny_rate,
            None,
        )
    return (
        float(rates.get("input_per_1m_cny", 0)),
        float(rates.get("output_per_1m_cny", 0)),
        None,
    )


def estimate_cost_cny(
    prompt_tokens: int | None,
    completion_tokens: int | None,
    rates: dict[str, Any] | None,
    usd_cny_rate: float = 7.2,
) -> float | None:
    if not rates:
        return None
    if prompt_tokens is None and completion_tokens is None:
        return None
    input_rate, output_rate, _ = resolve_rates_for_request(prompt_tokens, rates, usd_cny_rate)
    return ((prompt_tokens or 0) * input_rate + (completion_tokens or 0) * output_rate) / 1_000_000


def format_pricing_cell(rates: dict[str, Any], usd_cny_rate: float = 7.2) -> tuple[str, str]:
    """HTML-safe summary of image-input and text-output unit prices."""
    tiers = rates.get("tiers")
    if tiers:
        parts_in: list[str] = []
        parts_out: list[str] = []
        for t in tiers:
            label = t.get("label", "")
            parts_in.append(f"{label}: ¥{t['input_per_1m_cny']}")
            parts_out.append(f"{label}: ¥{t['output_per_1m_cny']}")
        return "<br/>".join(parts_in), "<br/>".join(parts_out)
    if "input_per_1m_usd" in rates:
        inp = float(rates["input_per_1m_usd"]) * usd_cny_rate
        out = float(rates["output_per_1m_usd"]) * usd_cny_rate
        return (
            f"¥{inp:g} <span class='muted'>(${rates['input_per_1m_usd']})</span>",
            f"¥{out:g} <span class='muted'>(${rates['output_per_1m_usd']})</span>",
        )
    return f"¥{rates.get('input_per_1m_cny')}", f"¥{rates.get('output_per_1m_cny')}"


def image_key_from_path(image_path: str) -> str:
    return Path(image_path).name


def parse_jsonl(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    """model -> image_filename -> record"""
    by_model: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            model = row.get("model") or "unknown"
            image = image_key_from_path(row.get("image", ""))
            by_model[model][image] = row
    return dict(by_model)


def empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def normalize_str(value: Any) -> str | None:
    if empty_value(value):
        return None
    return str(value).strip()


def normalize_number(value: Any) -> float | None:
    if empty_value(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = re.sub(r"[^\d.]", "", str(value))
    if not s:
        return None
    return float(s)


def normalize_int(value: Any) -> int | None:
    num = normalize_number(value)
    if num is None:
        return None
    return int(round(num))


def parse_datetime_parts(value: Any) -> tuple[str | None, str | None]:
    """Return (YYYY-MM-DD, HH:MM) best effort."""
    if empty_value(value):
        return None, None
    text = str(value).strip()
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    time_match = re.search(r"(\d{1,2}):(\d{2})", text)
    date_part = date_match.group(1) if date_match else None
    time_part = None
    if time_match:
        time_part = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"
    return date_part, time_part


def values_match(field: str, expected: Any, actual: Any) -> bool:
    if empty_value(expected) and empty_value(actual):
        return True
    if empty_value(expected) != empty_value(actual):
        return False

    if field in ("movie_duration", "seat_row", "seat_col"):
        return normalize_int(expected) == normalize_int(actual)

    if field == "price":
        ev = normalize_number(expected)
        av = normalize_number(actual)
        if ev is None or av is None:
            return ev == av
        return abs(ev - av) < 0.01

    if field == "ticket_date":
        ed, et = parse_datetime_parts(expected)
        ad, at = parse_datetime_parts(actual)
        if ed != ad:
            return False
        if et and at:
            return et == at
        return True

    if field in ("start_time", "end_time"):
        _, et = parse_datetime_parts(expected)
        _, at = parse_datetime_parts(actual)
        return et == at

    return normalize_str(expected) == normalize_str(actual)


def extract_prediction(record: dict[str, Any]) -> dict[str, Any] | None:
    if record.get("error") or record.get("parse_error"):
        return None
    parsed = record.get("parsed_json")
    if isinstance(parsed, list):
        return parsed[0] if parsed else {}
    if isinstance(parsed, dict):
        return parsed
    return None


@dataclass
class FieldStats:
    correct: int = 0
    total: int = 0

    def add(self, ok: bool) -> None:
        self.total += 1
        if ok:
            self.correct += 1

    @property
    def accuracy(self) -> float | None:
        if self.total == 0:
            return None
        return self.correct / self.total


@dataclass
class TokenStats:
    calls_with_usage: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_elapsed_seconds: float = 0.0
    calls_with_elapsed: int = 0
    total_cost_cny: float = 0.0
    priced_calls: int = 0

    @property
    def avg_prompt_tokens(self) -> float | None:
        if self.calls_with_usage == 0:
            return None
        return self.total_prompt_tokens / self.calls_with_usage

    @property
    def avg_completion_tokens(self) -> float | None:
        if self.calls_with_usage == 0:
            return None
        return self.total_completion_tokens / self.calls_with_usage

    @property
    def avg_total_tokens(self) -> float | None:
        if self.calls_with_usage == 0:
            return None
        return self.total_tokens / self.calls_with_usage

    @property
    def avg_elapsed_seconds(self) -> float | None:
        if self.calls_with_elapsed == 0:
            return None
        return self.total_elapsed_seconds / self.calls_with_elapsed

    @property
    def avg_cost_cny(self) -> float | None:
        if self.priced_calls == 0:
            return None
        return self.total_cost_cny / self.priced_calls


def parse_usage(record: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    usage = record.get("usage")
    if not isinstance(usage, dict):
        return None, None, None
    prompt = usage.get("prompt_tokens")
    completion = usage.get("completion_tokens")
    total = usage.get("total_tokens")
    if prompt is None and completion is None and total is None:
        return None, None, None
    prompt_i = int(prompt) if prompt is not None else None
    completion_i = int(completion) if completion is not None else None
    if total is not None:
        total_i = int(total)
    elif prompt_i is not None and completion_i is not None:
        total_i = prompt_i + completion_i
    else:
        total_i = None
    return prompt_i, completion_i, total_i


def aggregate_token_stats(
    records: dict[str, dict[str, Any]],
    rates: dict[str, Any] | None = None,
    usd_cny_rate: float = 7.2,
) -> TokenStats:
    stats = TokenStats()
    for rec in records.values():
        prompt, completion, total = parse_usage(rec)
        if total is not None:
            stats.calls_with_usage += 1
            stats.total_prompt_tokens += prompt or 0
            stats.total_completion_tokens += completion or 0
            stats.total_tokens += total
            cost = estimate_cost_cny(prompt, completion, rates, usd_cny_rate)
            if cost is not None:
                stats.priced_calls += 1
                stats.total_cost_cny += cost
        elapsed = rec.get("elapsed_seconds")
        if elapsed is not None:
            stats.calls_with_elapsed += 1
            stats.total_elapsed_seconds += float(elapsed)
    return stats


@dataclass
class ImageResult:
    image: str
    status: str
    field_results: dict[str, bool] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)
    actual: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    elapsed_seconds: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_cny: float | None = None


@dataclass
class ModelReport:
    model: str
    provider: str
    images: list[ImageResult] = field(default_factory=list)
    field_stats: dict[str, FieldStats] = field(default_factory=lambda: {f: FieldStats() for f in EVAL_FIELDS})
    core_stats: FieldStats = field(default_factory=FieldStats)
    all_stats: FieldStats = field(default_factory=FieldStats)
    tokens: TokenStats = field(default_factory=TokenStats)
    api_failures: int = 0
    parse_failures: int = 0
    missing_images: int = 0
    extra_fill: int = 0

    def finalize(self) -> None:
        for img in self.images:
            if img.status != "ok":
                continue
            for fld in EVAL_FIELDS:
                exp = img.expected.get(fld)
                act = img.actual.get(fld)
                if empty_value(exp):
                    if not empty_value(act):
                        self.extra_fill += 1
                    continue
                ok = img.field_results.get(fld, False)
                self.field_stats[fld].add(ok)
                self.all_stats.add(ok)
                if fld in CORE_FIELDS:
                    self.core_stats.add(ok)


def score_model(
    model: str,
    records: dict[str, dict[str, Any]],
    reference: dict[str, dict[str, Any]],
    model_rates: dict[str, Any] | None = None,
    usd_cny_rate: float = 7.2,
) -> ModelReport:
    provider = ""
    for rec in records.values():
        if rec.get("provider"):
            provider = rec["provider"]
            break

    report = ModelReport(model=model, provider=provider)
    scored_records = filter_records_for_reference(records, reference)
    report.tokens = aggregate_token_stats(scored_records, model_rates, usd_cny_rate)

    def image_meta(rec: dict[str, Any]) -> dict[str, Any]:
        prompt, completion, total = parse_usage(rec)
        elapsed = rec.get("elapsed_seconds")
        return {
            "elapsed_seconds": float(elapsed) if elapsed is not None else None,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": total,
            "cost_cny": estimate_cost_cny(prompt, completion, model_rates, usd_cny_rate),
        }

    for image, expected in sorted(reference.items()):
        rec = records.get(image)
        if not rec:
            report.missing_images += 1
            report.images.append(ImageResult(image=image, status="missing", expected=expected))
            continue

        meta = image_meta(rec)

        if rec.get("error"):
            report.api_failures += 1
            report.images.append(
                ImageResult(
                    image=image,
                    status="api_error",
                    expected=expected,
                    error=str(rec.get("error")),
                    **meta,
                )
            )
            continue

        if rec.get("parse_error"):
            report.parse_failures += 1
            report.images.append(
                ImageResult(
                    image=image,
                    status="parse_error",
                    expected=expected,
                    error=str(rec.get("parse_error")),
                    **meta,
                )
            )
            continue

        actual = extract_prediction(rec) or {}
        field_results: dict[str, bool] = {}
        for fld in EVAL_FIELDS:
            field_results[fld] = values_match(fld, expected.get(fld), actual.get(fld))

        report.images.append(
            ImageResult(
                image=image,
                status="ok",
                field_results=field_results,
                expected=expected,
                actual=actual,
                **meta,
            )
        )

    report.finalize()
    return report


def fmt_num(value: int | float | None, digits: int = 0) -> str:
    if value is None:
        return "n/a"
    if digits:
        return f"{float(value):,.{digits}f}"
    return f"{int(round(value)):,}"


def fmt_cny(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    if value >= 1:
        return f"¥{value:,.{min(digits, 2)}f}"
    return f"¥{value:,.{digits}f}"


def token_summary_text(tokens: TokenStats) -> str:
    if tokens.calls_with_usage == 0:
        return "Token：无 usage 记录"
    parts = [
        f"Token 合计 {fmt_num(tokens.total_tokens)} "
        f"(输入 {fmt_num(tokens.total_prompt_tokens)} / 输出 {fmt_num(tokens.total_completion_tokens)})，"
        f"均 {fmt_num(tokens.avg_total_tokens, 0)}/次",
        f"耗时合计 {fmt_num(tokens.total_elapsed_seconds, 1)}s，"
        f"均 {fmt_num(tokens.avg_elapsed_seconds, 2)}s/次",
    ]
    if tokens.priced_calls:
        parts.append(
            f"预估费用（图片输入+文本输出）合计 {fmt_cny(tokens.total_cost_cny)}，"
            f"均 {fmt_cny(tokens.avg_cost_cny)}/次"
        )
    return "；".join(parts)


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def write_summary_csv(path: Path, reports: list[ModelReport]) -> None:
    fieldnames = [
        "model",
        "provider",
        "images_in_reference",
        "scored_images",
        "api_failures",
        "parse_failures",
        "missing_images",
        "core_field_accuracy",
        "all_field_accuracy",
        "extra_fill_count",
        "total_prompt_tokens",
        "total_completion_tokens",
        "total_tokens",
        "avg_tokens_per_call",
        "total_elapsed_seconds",
        "avg_elapsed_seconds",
        "est_cost_cny_total",
        "est_cost_cny_per_call",
        *[f"acc_{f}" for f in EVAL_FIELDS],
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sorted(reports, key=lambda x: (-(x.core_stats.accuracy or -1), x.model)):
            scored = sum(1 for img in r.images if img.status == "ok")
            row = {
                "model": r.model,
                "provider": r.provider,
                "images_in_reference": len(r.images),
                "scored_images": scored,
                "api_failures": r.api_failures,
                "parse_failures": r.parse_failures,
                "missing_images": r.missing_images,
                "core_field_accuracy": pct(r.core_stats.accuracy),
                "all_field_accuracy": pct(r.all_stats.accuracy),
                "extra_fill_count": r.extra_fill,
                "total_prompt_tokens": fmt_num(r.tokens.total_prompt_tokens) if r.tokens.calls_with_usage else "n/a",
                "total_completion_tokens": fmt_num(r.tokens.total_completion_tokens)
                if r.tokens.calls_with_usage
                else "n/a",
                "total_tokens": fmt_num(r.tokens.total_tokens) if r.tokens.calls_with_usage else "n/a",
                "avg_tokens_per_call": fmt_num(r.tokens.avg_total_tokens, 0)
                if r.tokens.calls_with_usage
                else "n/a",
                "total_elapsed_seconds": fmt_num(r.tokens.total_elapsed_seconds, 1)
                if r.tokens.calls_with_elapsed
                else "n/a",
                "avg_elapsed_seconds": fmt_num(r.tokens.avg_elapsed_seconds, 2)
                if r.tokens.calls_with_elapsed
                else "n/a",
                "est_cost_cny_total": fmt_cny(r.tokens.total_cost_cny)
                if r.tokens.priced_calls
                else "n/a",
                "est_cost_cny_per_call": fmt_cny(r.tokens.avg_cost_cny)
                if r.tokens.priced_calls
                else "n/a",
            }
            for fld in EVAL_FIELDS:
                row[f"acc_{fld}"] = pct(r.field_stats[fld].accuracy)
            writer.writerow(row)


def write_model_markdown(path: Path, report: ModelReport) -> None:
    lines = [
        f"# 模型评测报告：{report.model}",
        "",
        f"- 提供方：{report.provider or '—'}",
        f"- 参考票张数：{len(report.images)}",
        f"- 成功解析并打分：{sum(1 for i in report.images if i.status == 'ok')}",
        f"- API 失败：{report.api_failures}",
        f"- JSON 解析失败：{report.parse_failures}",
        f"- 缺少评测记录：{report.missing_images}",
        f"- **核心字段准确率**：{pct(report.core_stats.accuracy)} "
        f"（{report.core_stats.correct}/{report.core_stats.total}）",
        f"- **全字段准确率**（仅计参考非空）：{pct(report.all_stats.accuracy)} "
        f"（{report.all_stats.correct}/{report.all_stats.total}）",
        f"- 参考为空但模型填了值：{report.extra_fill} 次",
        f"- **Token 消耗**：{token_summary_text(report.tokens)}",
        "",
        "## 分字段准确率（参考非空）",
        "",
        "| 字段 | 正确/总数 | 准确率 |",
        "|------|-----------|--------|",
    ]
    for fld in EVAL_FIELDS:
        st = report.field_stats[fld]
        lines.append(f"| `{fld}` | {st.correct}/{st.total} | {pct(st.accuracy)} |")

    lines.extend(["", "## 逐图明细", ""])
    for img in report.images:
        lines.append(f"### {img.image}")
        if img.status != "ok":
            lines.append(f"- 状态：**{img.status}**")
            if img.error:
                lines.append(f"- 错误：`{img.error}`")
            lines.append("")
            continue

        token_bits = []
        if img.total_tokens is not None:
            token_bits.append(f"total={img.total_tokens}")
        if img.prompt_tokens is not None:
            token_bits.append(f"prompt={img.prompt_tokens}")
        if img.completion_tokens is not None:
            token_bits.append(f"completion={img.completion_tokens}")
        if img.elapsed_seconds is not None:
            token_bits.append(f"{img.elapsed_seconds}s")
        if img.cost_cny is not None:
            token_bits.append(f"≈{fmt_cny(img.cost_cny)}")
        if token_bits:
            lines.append(f"- Token/耗时/费用：{', '.join(token_bits)}")

        wrong = [f for f, ok in img.field_results.items() if not ok and not empty_value(img.expected.get(f))]
        lines.append("- 状态：ok")
        if wrong:
            lines.append(f"- 错误字段：{', '.join(f'`{f}`' for f in wrong)}")
        else:
            lines.append("- 错误字段：无（在参考非空字段上全对）")
        lines.append("")
        lines.append("| 字段 | 参考 | 模型 | 结果 |")
        lines.append("|------|------|------|------|")
        for fld in EVAL_FIELDS:
            exp = img.expected.get(fld)
            act = img.actual.get(fld)
            if empty_value(exp) and empty_value(act):
                continue
            mark = "✓" if img.field_results.get(fld) else "✗"
            lines.append(f"| `{fld}` | `{exp}` | `{act}` | {mark} |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_overview_markdown(
    path: Path,
    reports: list[ModelReport],
    reference_path: Path,
    jsonl_path: Path,
    *,
    image_count: int,
    exclude_images: frozenset[str],
) -> None:
    ranked = sorted(reports, key=lambda r: (-(r.core_stats.accuracy or -1), -(r.all_stats.accuracy or -1)))
    lines = [
        "# 视觉模型评测总览",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 参考 JSON：`{reference_path.name}`",
        f"- 计分图片数：{image_count}",
        f"- 模型输出：`{jsonl_path.name}`",
    ]
    if exclude_images:
        lines.append(f"- 已排除（不参与计分）：{', '.join(sorted(exclude_images))}")
    lines.extend(
        [
            "",
            "## 排名（核心字段）",
            "",
            "核心字段：`movie_name`, `ticket_date`, `start_time`, `price`, `cinema_hall`, `seat_row`, `seat_col`",
            "",
            "| 排名 | 模型 | 核心准确率 | 全字段准确率 | 总 Token | 均 Token/次 | 预估费用(¥) | 均费用/次 | 均耗时 | API失败 | 详报 |",
            "|------|------|------------|--------------|----------|-------------|-------------|-----------|--------|---------|------|",
        ]
    )
    for idx, r in enumerate(ranked, start=1):
        link = f"{r.model}_report.md"
        lines.append(
            f"| {idx} | {r.model} | {pct(r.core_stats.accuracy)} | {pct(r.all_stats.accuracy)} | "
            f"{fmt_num(r.tokens.total_tokens) if r.tokens.calls_with_usage else 'n/a'} | "
            f"{fmt_num(r.tokens.avg_total_tokens, 0) if r.tokens.calls_with_usage else 'n/a'} | "
            f"{fmt_cny(r.tokens.total_cost_cny) if r.tokens.priced_calls else 'n/a'} | "
            f"{fmt_cny(r.tokens.avg_cost_cny) if r.tokens.priced_calls else 'n/a'} | "
            f"{fmt_num(r.tokens.avg_elapsed_seconds, 2) if r.tokens.calls_with_elapsed else 'n/a'}s | "
            f"{r.api_failures} | [{link}]({link}) |"
        )
    lines.append("")
    lines.extend(
        [
            "## Token 与费用汇总",
            "",
            "| 模型 | 总输入 Token | 总输出 Token | 总 Token | 均 Token/次 | 预估费用(¥) | 均费用/次 | 总耗时(s) | 均耗时(s) |",
            "|------|-------------|-------------|----------|-------------|-------------|-----------|-----------|-----------|",
        ]
    )
    for r in ranked:
        t = r.tokens
        lines.append(
            f"| {r.model} | "
            f"{fmt_num(t.total_prompt_tokens) if t.calls_with_usage else 'n/a'} | "
            f"{fmt_num(t.total_completion_tokens) if t.calls_with_usage else 'n/a'} | "
            f"{fmt_num(t.total_tokens) if t.calls_with_usage else 'n/a'} | "
            f"{fmt_num(t.avg_total_tokens, 0) if t.calls_with_usage else 'n/a'} | "
            f"{fmt_cny(t.total_cost_cny) if t.priced_calls else 'n/a'} | "
            f"{fmt_cny(t.avg_cost_cny) if t.priced_calls else 'n/a'} | "
            f"{fmt_num(t.total_elapsed_seconds, 1) if t.calls_with_elapsed else 'n/a'} | "
            f"{fmt_num(t.avg_elapsed_seconds, 2) if t.calls_with_elapsed else 'n/a'} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")



def esc(value: Any) -> str:
    if value is None:
        return '<span class="null">null</span>'
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, indent=2)
    else:
        text = str(value)
    return html.escape(text)


def write_html_report(
    path: Path,
    reports: list[ModelReport],
    reference_path: Path,
    jsonl_path: Path,
    jsonl_records: dict[str, dict[str, dict[str, Any]]],
    pricing_meta: dict[str, Any] | None = None,
    model_pricing: dict[str, dict[str, Any]] | None = None,
    *,
    image_count: int,
    model_count: int,
    exclude_images: frozenset[str],
) -> None:
    ranked = sorted(reports, key=lambda r: (-(r.core_stats.accuracy or -1), -(r.all_stats.accuracy or -1)))
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    image_base = "../../eval_pics/"
    parts: list[str] = []

    def add(s: str) -> None:
        parts.append(s)

    add("<!doctype html><html lang='zh-CN'><head><meta charset='utf-8' />")
    add("<meta name='viewport' content='width=device-width, initial-scale=1' />")
    add("<title>视觉大模型电影票评测报告</title><style>")
    add(":root{--bg:#f4f6fa;--panel:#fff;--text:#1f2937;--muted:#6b7280;--line:#dde3ee;--accent:#2563eb;--ok:#15803d;--bad:#b91c1c}")
    add("body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.5}")
    add("header{background:var(--panel);border-bottom:1px solid var(--line);padding:20px 24px}")
    add("header h1{margin:0 0 8px;font-size:24px}header p{margin:4px 0;color:var(--muted);font-size:14px}")
    add("main{max-width:1280px;margin:0 auto;padding:24px}")
    add("section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-bottom:20px}")
    add("section h2{margin:0 0 12px;font-size:18px}section h3{margin:18px 0 10px;font-size:15px}")
    add("table{width:100%;border-collapse:collapse;font-size:13px}th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}")
    add("th{background:#f8fafc}tr:nth-child(even) td{background:#fbfcfe}.rank-1 td{background:#ecfdf5}")
    add(".ok{color:var(--ok);font-weight:700}.bad{color:var(--bad);font-weight:700}.null{color:var(--muted)}")
    add(".tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;background:#eff6ff;color:#1d4ed8;margin-right:6px}")
    add(".model-block{border-top:1px solid var(--line);margin-top:24px;padding-top:20px}")
    add(".card-grid{display:grid;gap:16px}.image-card{border:1px solid var(--line);border-radius:8px;overflow:hidden}")
    add(".image-card header{padding:10px 12px;background:#f8fafc;border-bottom:1px solid var(--line);display:flex;gap:12px;align-items:center;flex-wrap:wrap}")
    add(".image-card header img{width:120px;height:80px;object-fit:cover;border-radius:4px;border:1px solid var(--line)}")
    add(".image-card .body{padding:12px}details{margin:8px 0}summary{cursor:pointer;font-weight:600}")
    add("pre{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:6px;overflow:auto;font-size:12px;max-height:280px}")
    add("ul.compact{margin:8px 0;padding-left:20px}a.anchor{color:var(--accent);text-decoration:none}")
    add("p.muted{color:var(--muted);font-size:13px}")
    add("</style></head><body><header><h1>视觉大模型电影票评测报告</h1>")
    add(f"<p>生成时间：{generated}</p>")
    add(
        f"<p>参考真值：<code>{html.escape(reference_path.name)}</code>（计分 {image_count} 张） · "
        f"模型输出：<code>{html.escape(jsonl_path.name)}</code>（{model_count}×{image_count}={model_count * image_count} 条计分）</p>"
    )
    if exclude_images:
        excluded = ", ".join(html.escape(x) for x in sorted(exclude_images))
        add(f"<p class='muted'>已排除不参与计分：{excluded}（参考真值无效或图片不可用）</p>")
    add("</header><main>")

    add("<section id='data-sources'><h2>一、原始评测结果包含哪些信息</h2>")
    add("<p>每条记录来自 <code>vision_model_eval.jsonl</code>，对应一张图片 + 一个模型的一次调用：</p>")
    add("<table><thead><tr><th>字段</th><th>说明</th></tr></thead><tbody>")
    for key, label in JSONL_RECORD_FIELDS:
        add(f"<tr><td><code>{html.escape(key)}</code></td><td>{html.escape(label)}</td></tr>")
    add("</tbody></table><h3>解析 JSON 业务字段（11 个）</h3><ul class='compact'>")
    for fld in EVAL_FIELDS:
        add(f"<li><code>{fld}</code> — {FIELD_LABELS[fld]}</li>")
    add("</ul><h3>对比报告额外指标</h3><ul class='compact'>")
    add("<li><strong>核心字段准确率</strong>：片名、日期、开始时间、票价、影厅、排号、座号（仅参考非空）</li>")
    add("<li><strong>全字段准确率</strong>：11 个业务字段（仅参考非空）</li>")
    add("<li>API 失败 / JSON 解析失败 / 缺记录 / 多余填写（参考空、模型有值）</li>")
    add("<li><strong>Token 消耗</strong>：来自 JSONL 的 <code>usage</code>（prompt / completion / total）与 <code>elapsed_seconds</code></li>")
    add(
        "<li><strong>预估费用（人民币）</strong>："
        "<code>prompt_tokens</code>×图片输入单价 + <code>completion_tokens</code>×文本输出单价"
        "（见第二节单价表），非实际账单</li>"
    )
    add("</ul></section>")

    if pricing_meta or model_pricing:
        add("<section id='pricing'><h2>二、单价与费用说明（人民币）</h2>")
        if pricing_meta:
            note = pricing_meta.get("note", "")
            as_of = pricing_meta.get("as_of", "")
            rate = pricing_meta.get("usd_cny_rate")
            if as_of:
                add(f"<p>价格参考日期：<strong>{html.escape(str(as_of))}</strong></p>")
            if rate is not None:
                add(f"<p>美元标价折算汇率：<strong>1 USD = {rate} CNY</strong></p>")
            if note:
                add(f"<p class='muted'>{html.escape(str(note))}</p>")
        if model_pricing:
            usd_rate = float((pricing_meta or {}).get("usd_cny_rate", 7.2))
            in_label = (pricing_meta or {}).get("input_label", "图片输入")
            out_label = (pricing_meta or {}).get("output_label", "文本输出")
            add(
                f"<table><thead><tr><th>模型</th><th>{html.escape(str(in_label))} (¥/百万 Token)</th>"
                f"<th>{html.escape(str(out_label))} (¥/百万 Token)</th><th>来源</th></tr></thead><tbody>"
            )
            for model_id in sorted(model_pricing.keys()):
                rates = model_pricing[model_id]
                cell_in, cell_out = format_pricing_cell(rates, usd_rate)
                add(
                    f"<tr><td><code>{html.escape(model_id)}</code></td>"
                    f"<td>{cell_in}</td><td>{cell_out}</td>"
                    f"<td>{html.escape(str(rates.get('source', '')))}</td></tr>"
                )
            add("</tbody></table>")
        add("</section>")

    add("<section id='ranking'><h2>三、模型排名总览</h2><table><thead><tr>")
    add("<th>排名</th><th>模型</th><th>提供方</th><th>核心准确率</th><th>全字段准确率</th>")
    add("<th>总 Token</th><th>均 Token/次</th><th>预估费用(¥)</th><th>均费用/次</th><th>均耗时</th>")
    add("<th>成功打分</th><th>API失败</th><th>解析失败</th><th>详情</th></tr></thead><tbody>")
    for idx, r in enumerate(ranked, start=1):
        row_class = "rank-1" if idx == 1 and r.core_stats.accuracy is not None else ""
        scored = sum(1 for i in r.images if i.status == "ok")
        anchor = html.escape(r.model, quote=True)
        t = r.tokens
        add(
            f"<tr class='{row_class}'><td>{idx}</td><td><strong>{html.escape(r.model)}</strong></td>"
            f"<td>{html.escape(r.provider)}</td><td>{pct(r.core_stats.accuracy)}</td><td>{pct(r.all_stats.accuracy)}</td>"
            f"<td>{fmt_num(t.total_tokens) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_num(t.avg_total_tokens, 0) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_cny(t.total_cost_cny) if t.priced_calls else 'n/a'}</td>"
            f"<td>{fmt_cny(t.avg_cost_cny) if t.priced_calls else 'n/a'}</td>"
            f"<td>{fmt_num(t.avg_elapsed_seconds, 2) if t.calls_with_elapsed else 'n/a'}s</td>"
            f"<td>{scored}/{len(r.images)}</td><td>{r.api_failures}</td><td>{r.parse_failures}</td>"
            f"<td><a class='anchor' href='#model-{anchor}'>跳转</a></td></tr>"
        )
    add("</tbody></table></section>")

    add("<section id='tokens'><h2>四、Token 与费用汇总</h2><table><thead><tr>")
    add("<th>模型</th><th>总输入 Token</th><th>总输出 Token</th><th>总 Token</th><th>均 Token/次</th>")
    add("<th>预估费用(¥)</th><th>均费用/次</th><th>总耗时(s)</th><th>均耗时(s)</th></tr></thead><tbody>")
    for r in ranked:
        t = r.tokens
        add(
            f"<tr><td><strong>{html.escape(r.model)}</strong></td>"
            f"<td>{fmt_num(t.total_prompt_tokens) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_num(t.total_completion_tokens) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_num(t.total_tokens) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_num(t.avg_total_tokens, 0) if t.calls_with_usage else 'n/a'}</td>"
            f"<td>{fmt_cny(t.total_cost_cny) if t.priced_calls else 'n/a'}</td>"
            f"<td>{fmt_cny(t.avg_cost_cny) if t.priced_calls else 'n/a'}</td>"
            f"<td>{fmt_num(t.total_elapsed_seconds, 1) if t.calls_with_elapsed else 'n/a'}</td>"
            f"<td>{fmt_num(t.avg_elapsed_seconds, 2) if t.calls_with_elapsed else 'n/a'}</td></tr>"
        )
    add("</tbody></table></section>")

    add("<section id='field-summary'><h2>五、分字段准确率（全模型）</h2><table><thead><tr><th>模型</th>")
    for fld in EVAL_FIELDS:
        add(f"<th title='{fld}'>{html.escape(FIELD_LABELS[fld])}</th>")
    add("</tr></thead><tbody>")
    for r in ranked:
        add(f"<tr><td><strong>{html.escape(r.model)}</strong></td>")
        for fld in EVAL_FIELDS:
            add(f"<td>{pct(r.field_stats[fld].accuracy)}</td>")
        add("</tr>")
    add("</tbody></table></section>")

    add("<section id='models'><h2>六、各模型详细报告</h2>")
    for r in ranked:
        anchor = html.escape(r.model, quote=True)
        add(f"<article class='model-block' id='model-{anchor}'>")
        add(f"<h3>{html.escape(r.model)} <span class='tag'>{html.escape(r.provider)}</span></h3>")
        add("<ul class='compact'>")
        add(f"<li>核心字段准确率：<strong>{pct(r.core_stats.accuracy)}</strong>（{r.core_stats.correct}/{r.core_stats.total}）</li>")
        add(f"<li>全字段准确率：<strong>{pct(r.all_stats.accuracy)}</strong>（{r.all_stats.correct}/{r.all_stats.total}）</li>")
        add(
            f"<li>API 失败 {r.api_failures} · 解析失败 {r.parse_failures} · 缺记录 {r.missing_images} · 多余填写 {r.extra_fill}</li>"
        )
        add(f"<li>{html.escape(token_summary_text(r.tokens))}</li></ul>")
        add("<table><thead><tr><th>字段</th><th>正确/总数</th><th>准确率</th></tr></thead><tbody>")
        for fld in EVAL_FIELDS:
            st = r.field_stats[fld]
            add(f"<tr><td>{html.escape(FIELD_LABELS[fld])} <code>{fld}</code></td><td>{st.correct}/{st.total}</td><td>{pct(st.accuracy)}</td></tr>")
        add("</tbody></table><div class='card-grid'>")
        for img in r.images:
            raw = jsonl_records.get(r.model, {}).get(img.image, {})
            add("<div class='image-card'><header>")
            add(f"<img src='{image_base}{html.escape(img.image)}' alt='{html.escape(img.image)}' loading='lazy' />")
            add("<div><strong>" + html.escape(img.image) + "</strong> ")
            add(f"<span class='tag'>{html.escape(img.status)}</span> ")
            if img.elapsed_seconds is not None:
                add(f"<span class='tag'>{img.elapsed_seconds}s</span>")
            if img.total_tokens is not None:
                add(f"<span class='tag'>{fmt_num(img.total_tokens)} tok</span>")
                if img.prompt_tokens is not None and img.completion_tokens is not None:
                    add(
                        f"<span class='tag'>in {fmt_num(img.prompt_tokens)} / out {fmt_num(img.completion_tokens)}</span>"
                    )
            if img.cost_cny is not None:
                add(f"<span class='tag'>≈{fmt_cny(img.cost_cny)}</span>")
            add("</div></header><div class='body'>")
            if img.status != "ok":
                add(f"<p class='bad'>{esc(img.error)}</p>")
            else:
                wrong = [f for f, ok in img.field_results.items() if not ok and not empty_value(img.expected.get(f))]
                if wrong:
                    add("<p>错误字段：" + ", ".join(f"<code>{html.escape(f)}</code>" for f in wrong) + "</p>")
                else:
                    add("<p class='ok'>参考非空字段全部正确</p>")
                add("<table><thead><tr><th>字段</th><th>参考</th><th>模型</th><th>结果</th></tr></thead><tbody>")
                for fld in EVAL_FIELDS:
                    exp, act = img.expected.get(fld), img.actual.get(fld)
                    if empty_value(exp) and empty_value(act):
                        continue
                    mark = "<span class='ok'>✓</span>" if img.field_results.get(fld) else "<span class='bad'>✗</span>"
                    add(f"<tr><td>{html.escape(FIELD_LABELS[fld])}</td><td>{esc(exp)}</td><td>{esc(act)}</td><td>{mark}</td></tr>")
                add("</tbody></table>")
            if raw:
                snippet = {k: raw.get(k) for k, _ in JSONL_RECORD_FIELDS}
                snippet["model"] = raw.get("model")
                add("<details><summary>原始 JSONL 记录</summary><pre>" + esc(snippet) + "</pre></details>")
            add("</div></div>")
        add("</div></article>")
    add("</section></main></body></html>")
    path.write_text("".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare vision model JSONL outputs to reference JSON.")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--pricing", type=Path, default=DEFAULT_PRICING)
    parser.add_argument(
        "--exclude",
        default=",".join(sorted(DEFAULT_EXCLUDE_IMAGES)),
        help="Comma-separated image filenames to exclude from scoring (default: IMG_0017.jpeg). Use empty string to include all.",
    )
    args = parser.parse_args()

    if not args.reference.exists():
        raise SystemExit(f"Reference not found: {args.reference}")
    if not args.jsonl.exists():
        raise SystemExit(f"JSONL not found: {args.jsonl}")

    reference_full = load_reference(args.reference)
    exclude_images = parse_exclude_images(args.exclude)
    reference = filter_reference(reference_full, exclude_images)
    if not reference:
        raise SystemExit("No reference images left after exclusions.")
    if exclude_images:
        print(f"Excluded from scoring: {', '.join(sorted(exclude_images))}")

    by_model = parse_jsonl(args.jsonl)
    model_pricing, pricing_meta = load_model_pricing(args.pricing)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    usd_cny_rate = float(pricing_meta.get("usd_cny_rate", 7.2))
    image_count = len(reference)
    model_count = len(by_model)
    reports = [
        score_model(model, records, reference, model_pricing.get(model), usd_cny_rate)
        for model, records in sorted(by_model.items())
    ]

    write_summary_csv(args.output_dir / "model_comparison_summary.csv", reports)
    write_overview_markdown(
        args.output_dir / "overview.md",
        reports,
        args.reference,
        args.jsonl,
        image_count=image_count,
        exclude_images=exclude_images,
    )
    for report in reports:
        write_model_markdown(args.output_dir / f"{report.model}_report.md", report)
    write_html_report(
        args.output_dir / "report.html",
        reports,
        args.reference,
        args.jsonl,
        by_model,
        pricing_meta=pricing_meta,
        model_pricing=model_pricing,
        image_count=image_count,
        model_count=model_count,
        exclude_images=exclude_images,
    )
    (ROOT / "eval_report.html").write_text((args.output_dir / "report.html").read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Models compared: {len(reports)}")
    print(f"Reference images (scored): {image_count}")
    print(f"Wrote: {args.output_dir}/report.html")
    print(f"Wrote: {ROOT / 'eval_report.html'}")


if __name__ == "__main__":
    main()

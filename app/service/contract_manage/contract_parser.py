#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : contract_parser.py
# @Project : CMS-Backend
"""合同 Word（.doc 固定格式）解析：提取文本 + 按锚点正则回填
合同编号/企业名称/联系人/联系方式/项目类型/合同金额/签约日期/月份/区域。

提取主方案为纯 Python（olefile 读 WordDocument 流 + UTF-16LE 解码），
无外部工具依赖；antiword/textutil(macOS)/libreoffice 仅作兜底。
注意：antiword 0.37 不兼容 WPS Office 生成的 .doc，不要调整为主方案。

样例与锚点约定见 asset/ai-docs/contract-manage-requirement.md 第 8 章。
"""
import os
import re
import shutil
import subprocess

import olefile

from utils.loging_util import logger

REGIONS = ("茂南区", "化州市", "高州市", "电白区", "高新区", "滨海新区")

_PHONE_PATTERN = r"1[3-9]\d{9}"
_AMOUNT_PATTERN = r"[（(]\s*[¥￥]\s*([\d,]+(?:\.\d{1,2})?)"

# 正文可读字符白名单（提取时白名单之外的字符替换为换行，保留段落边界）
_READABLE = r"[^\u4e00-\u9fa5A-Za-z0-9，。：:；！？（()）¥\.、《》\-—％%\s»«]"


def extract_text_python(doc_path):
    """纯 Python 提取：olefile 读 WordDocument 流，按 UTF-16LE 解码，
    正文白名单之外的字符替换为换行（保留段落边界），空行丢弃"""
    data = olefile.OleFileIO(doc_path).openstream("WordDocument").read()
    raw = data.decode("utf-16-le", errors="ignore")
    text = re.sub(_READABLE, "\n", raw)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def extract_text(doc_path):
    """.doc -> 纯文本；主方案纯 Python（olefile），失败时按 antiword -> textutil(macOS) -> libreoffice 兜底"""
    try:
        return extract_text_python(doc_path)
    except Exception as exc:
        logger.warning(f"olefile extract failed: {exc}")
    if shutil.which("antiword"):
        result = subprocess.run(["antiword", doc_path], capture_output=True, timeout=60)
        if result.returncode == 0:
            return result.stdout.decode("utf-8", "ignore")
        logger.warning(f"antiword failed: {result.stderr.decode('utf-8', 'ignore')[:200]}")
    if shutil.which("textutil"):  # macOS 开发机
        result = subprocess.run(["textutil", "-convert", "txt", "-stdout", doc_path],
                                capture_output=True, timeout=60)
        if result.returncode == 0:
            return result.stdout.decode("utf-8", "ignore")
        logger.warning(f"textutil failed: {result.stderr.decode('utf-8', 'ignore')[:200]}")
    if shutil.which("libreoffice"):  # 兜底（也支持 .docx）
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "txt:Text", "--outdir", tmp_dir, doc_path],
                capture_output=True, timeout=120)
            txt_files = [n for n in os.listdir(tmp_dir) if n.endswith(".txt")]
            if result.returncode == 0 and txt_files:
                with open(os.path.join(tmp_dir, txt_files[0]), encoding="utf-8", errors="ignore") as f:
                    return f.read()
        logger.warning("libreoffice convert failed")
    raise RuntimeError("合同文本提取失败（olefile 及 antiword/textutil/libreoffice 均不可用）")


def _first(text, pattern, group=1):
    match = re.search(pattern, text)
    return match.group(group).strip() if match else None


def parse_contract_text(text):
    """固定格式文本 -> 预填字段 dict（解析不到的键为 None，由前端留空手填）"""
    company_name = _first(text, r"甲方[：:]\s*(.+)")
    contact_match = re.search(r"联系人[：:]\s*([^\d]+?)\s*(" + _PHONE_PATTERN + r")", text)
    contact_person = contact_match.group(1).strip() if contact_match else None
    contact_phone = contact_match.group(2) if contact_match else None
    address = _first(text, r"地址[：:]\s*(.+)")

    amount_text = _first(text, _AMOUNT_PATTERN)
    contract_amount = None
    if amount_text:
        try:
            contract_amount = float(amount_text.replace(",", ""))
        except ValueError:
            contract_amount = None

    sign_date = None
    sign_match = re.search(r"签订日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if sign_match:
        sign_date = f"{sign_match.group(1)}-{int(sign_match.group(2)):02d}-{int(sign_match.group(3)):02d}"

    return {
        "contractNo": _first(text, r"合同编号[：:]\s*(\S+)"),
        "companyName": company_name,
        "contactPerson": contact_person,
        "contactPhone": contact_phone,
        "projectType": _first(text, r"项目类型[：:]\s*(.+)"),
        "contractAmount": contract_amount,
        "signDate": sign_date,
        "month": sign_date[:7] if sign_date else None,
        "region": next((r for r in REGIONS if address and r in address), None),
    }


def parse_contract(doc_path):
    """解析入口：提取文本 + 正则回填；返回 (fields, missing_keys)"""
    text = extract_text(doc_path)
    fields = parse_contract_text(text)
    missing = [key for key, value in fields.items() if value in (None, "")]
    if missing:
        logger.warning(f"contract parse incomplete {doc_path}: missing={missing}")
    return fields, missing


if __name__ == '__main__':
    exit(0)

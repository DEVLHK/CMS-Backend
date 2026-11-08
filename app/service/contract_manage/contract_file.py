#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/11/8 12:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : contract_file.py
# @Project : CMS-Backend
"""合同文件管理：暂存区（_incoming）、合同/报告/发票图片的落盘与清理。

存储规则：所有上传文件保留客户端原始文件名（basename + 清洗 + 防冲突后缀）。

目录布局（仓库根相对路径）：
temp/contracts/_incoming/{uuid}/{原文件名}   上传暂存（解析用，落库后移走；temp_key="uuid/原名"）
temp/contracts/{合同编号}/{原文件名}          合同 Word / PDF 副本 / 报告（DB 记录各自路径，重传删旧文件）
temp/contracts/{合同编号}/invoices/{明细id}_{原文件名}  发票图片（id 前缀避免不同明细同名互覆盖）
"""
import os
import shutil
import time
import uuid

from fastapi import UploadFile

from utils.loging_util import logger

CONTRACT_EXTS = (".doc",)                       # 合同：Word .doc 固定格式（决议 Q4）
CONTRACT_PDF_EXTS = (".pdf",)                   # 合同 PDF 副本（存档/下载用）
REPORT_EXTS = (".pdf", ".png", ".jpg", ".jpeg")  # 报告：PDF/图片（决议 Q5）
INVOICE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",   # 图片
                ".pdf", ".doc", ".docx", ".xls", ".xlsx")            # 图片以外的常见发票文件（放开限制）

MAX_NAME_STEM = 120  # 原文件名主名最大长度（防超长文件名）


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def contracts_root():
    return os.path.join(_project_root(), "temp", "contracts")


def incoming_dir():
    return os.path.join(contracts_root(), "_incoming")


def sanitize_filename(upload_file: UploadFile):
    """客户端文件名 -> 安全存储名：basename 防路径穿越、去控制字符、截断超长主名、扩展名小写"""
    name = os.path.basename(upload_file.filename or "")
    name = "".join(ch for ch in name if ord(ch) >= 32)  # 去控制字符
    stem, ext = os.path.splitext(name.strip())
    stem = (stem.strip() or "file")[:MAX_NAME_STEM]
    return stem + ext.lower()


def _dedupe_relative(relative, occupied):
    """目标相对路径与已占用路径冲突时追加时间戳后缀，返回最终相对路径"""
    if relative in set(occupied or ()):
        stem, ext = os.path.splitext(relative)
        relative = f"{stem}_{int(time.time())}{ext}"
    return relative


def _contracts_file_relative(contract_no, safe_name):
    return f"temp/contracts/{contract_no}/{safe_name}"


def _save_upload(upload_file: UploadFile, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as f:
        f.write(upload_file.file.read())
    return target_path


def _upload_ext(upload_file: UploadFile):
    """取上传文件扩展名（小写、带点）；无扩展名返回 ''"""
    filename = upload_file.filename or ""
    return os.path.splitext(filename)[1].lower()


def check_ext(upload_file: UploadFile, allowed):
    """扩展名校验，不通过返回错误信息（None=通过）"""
    ext = _upload_ext(upload_file)
    if ext not in allowed:
        return f"不支持的文件格式: {ext or '(无扩展名)'}，仅允许 {'/'.join(allowed)}"
    return None


def save_incoming(upload_file: UploadFile):
    """合同暂存：_incoming/{uuid}/{原文件名}，返回 temp_key（"uuid/原名"，落库时凭 key 转正）"""
    safe_name = sanitize_filename(upload_file)
    temp_key = f"{uuid.uuid4().hex}/{safe_name}"
    target = os.path.join(incoming_dir(), *temp_key.split("/"))
    _save_upload(upload_file, target)
    return temp_key


def resolve_incoming(temp_key):
    """暂存 key -> 绝对路径；非法/不存在返回 None。
    temp_key 仅允许 "uuid/原名" 两段格式，防目录穿越"""
    if not temp_key:
        return None
    parts = temp_key.split("/")
    if len(parts) != 2 or any(p in ("", ".", "..") for p in parts):
        return None
    path = os.path.normpath(os.path.join(incoming_dir(), *parts))
    if not path.startswith(os.path.normpath(incoming_dir()) + os.sep):
        return None
    if not os.path.isfile(path):
        return None
    return path


def promote_incoming(temp_key, contract_no):
    """暂存合同转正：移动到 contracts/{合同编号}/{原文件名}，返回新相对路径（DB contract_file 用）"""
    source = resolve_incoming(temp_key)
    if source is None:
        return None
    safe_name = os.path.basename(source)
    target = os.path.join(contracts_root(), contract_no, safe_name)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.move(source, target)
    return _contracts_file_relative(contract_no, safe_name)


def discard_incoming(temp_key):
    """解析失败/落库失败时清理暂存文件"""
    source = resolve_incoming(temp_key)
    if source is not None:
        try:
            os.remove(source)
            parent = os.path.dirname(source)
            if os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
        except OSError:
            logger.warning(f"incoming file remove failed: {source}")


def save_contract_word(contract_no, upload_file: UploadFile, occupied=()):
    """保存合同 Word 原件（按原始文件名，覆盖语义由 service 删旧文件保证），返回相对路径"""
    rel = _dedupe_relative(
        _contracts_file_relative(contract_no, sanitize_filename(upload_file)), occupied)
    _save_upload(upload_file, os.path.join(_project_root(), rel))
    return rel


def save_contract_pdf(contract_no, upload_file: UploadFile, occupied=()):
    """保存合同 PDF 副本（按原始文件名），返回相对路径"""
    rel = _dedupe_relative(
        _contracts_file_relative(contract_no, sanitize_filename(upload_file)), occupied)
    _save_upload(upload_file, os.path.join(_project_root(), rel))
    return rel


def save_report(contract_no, upload_file: UploadFile, occupied=()):
    """保存报告文件（按原始文件名），返回相对路径"""
    rel = _dedupe_relative(
        _contracts_file_relative(contract_no, sanitize_filename(upload_file)), occupied)
    _save_upload(upload_file, os.path.join(_project_root(), rel))
    return rel


def save_invoice_image(contract_no, detail_id, upload_file: UploadFile):
    """保存发票图片（覆盖式）：先删该明细旧图片（{id}_ 前缀与旧版 {id}. 两种格式），
    再落 invoices/{明细id}_{原文件名}（id 前缀避免不同明细同名互覆盖），返回相对路径"""
    invoice_dir = os.path.join(contracts_root(), contract_no, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)
    safe_name = sanitize_filename(upload_file)
    for name in os.listdir(invoice_dir):
        stem, _ext = os.path.splitext(name)
        if stem == str(detail_id) or stem.startswith(f"{detail_id}_"):
            os.remove(os.path.join(invoice_dir, name))
    rel = f"temp/contracts/{contract_no}/invoices/{detail_id}_{safe_name}"
    _save_upload(upload_file, os.path.join(_project_root(), rel))
    return rel


def absolute_of(relative_path):
    """DB 相对路径 -> 绝对路径；越界/不存在返回 None"""
    if not relative_path:
        return None
    path = os.path.normpath(os.path.join(_project_root(), relative_path))
    if not path.startswith(os.path.normpath(contracts_root()) + os.sep):
        return None
    if not os.path.isfile(path):
        return None
    return path


def delete_file_at(relative_path):
    """按 DB 相对路径删除文件（重传覆盖后的旧文件清理），不存在时静默"""
    path = absolute_of(relative_path)
    if path is not None:
        try:
            os.remove(path)
        except OSError:
            logger.warning(f"file remove failed: {path}")


def delete_contract_dir(contract_no):
    """删除合同（连带报告/发票图片），目录不存在时静默"""
    contract_dir = os.path.join(contracts_root(), contract_no)
    if os.path.isdir(contract_dir):
        shutil.rmtree(contract_dir, ignore_errors=True)
        logger.info(f"contract dir removed: {contract_dir}")


def delete_invoice_file(invoice_file_relative):
    """删除单个发票图片文件"""
    delete_file_at(invoice_file_relative)


if __name__ == '__main__':
    exit(0)

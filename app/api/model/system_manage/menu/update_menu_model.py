#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : update_menu_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict, Field

from app.api.model.system_manage.menu.menu_base_model import MenuBase


class Input(MenuBase):
    model_config = ConfigDict(title="MenuUpdateInput")

    id: int = Field(..., title="菜单ID")


if __name__ == '__main__':
    exit(0)

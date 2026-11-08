#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_menu_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict

from app.api.model.system_manage.menu.menu_base_model import MenuBase


class Input(MenuBase):
    """新增菜单（i18nKey/keepAlive/order 等路由属性后端打包进 route_props JSON）"""
    model_config = ConfigDict(title="MenuAddInput")


if __name__ == '__main__':
    exit(0)

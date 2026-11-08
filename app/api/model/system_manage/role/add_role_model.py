#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 14:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : add_role_model.py
# @Project : Soybean-backend
from pydantic import ConfigDict

from app.api.model.system_manage.role.role_base_model import RoleBase


class Input(RoleBase):
    model_config = ConfigDict(title="RoleAddInput")


if __name__ == '__main__':
    exit(0)

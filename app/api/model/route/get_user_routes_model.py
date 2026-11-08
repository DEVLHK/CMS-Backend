#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2026/10/17 20:00
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : get_user_routes_model.py
# @Project : Soybean-backend
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    """用户动态路由（MenuRoute 节点结构见 api-route-spec 第 0 节）"""
    model_config = ConfigDict(title="UserRoutes")

    routes: list = Field(
        [],
        title="菜单路由树",
        description="顶级为 parent_id=0 的菜单（及其可见子树），兄弟节点按 meta.order 升序"
    )
    home: str = Field(
        "home",
        title="用户首页路由名",
        description="用户第一个启用角色的 sys_role.home，不属于可访问页面时回退 home"
    )


if __name__ == '__main__':
    exit(0)

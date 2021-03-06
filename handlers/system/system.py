# -*- coding:utf-8 -*-  
# Created by xupingmao on 2016/10
# 

"""Description here"""
from io import StringIO
from xconfig import *
import xconfig
import codecs
import time
import functools
import os
import json
import socket
import os
import autoreload
import xtemplate
import xutils
import xauth
import xmanager
import xtables
from xutils import History
config = xconfig

def link(name, url):
    return Storage(name = name, url = url, link = url)

sys_tools = [
    link("系统状态",   "/system/monitor"),
    link("文件管理",   "/fs_list"),
    link("脚本管理",   "/fs_link/scripts"),
    link("定时任务",   "/system/crontab"),
    link("历史记录",   "/system/history"),
    link("用户管理",   "/system/user/list"),
    link("App管理",   "/fs_link/app"),
    link("后台模板缓存", "/system/template_cache"),
    link("重新加载模块", "/system/reload"),
    link("Python解释器", "/system/script/edit?name=test.py"),
    link("Python文档", "/system/modules_info"),
    link("SQL控制台", "/tools/sql"),
] 

doc_tools = [
    link("我的账号",   "/system/user"),
    link("登出",    "/logout"),
    link("笔记分组", "/index"),
    link("标签云", "/file/taglist"),
    link("词典", "/file/dict"),
    link("备忘", "/message?status=created"),
    link("最近更新", "/file/recent_edit"),
    link("日历", "/tools/date"),
] 

other_tools = [
    link("代码模板", "/tools/code_template"),
    link("浏览器信息", "/tools/browser_info"),
    link("文本对比", "/tools/js_diff"),
    link("字符转换", "/tools/string"),
    link("图片合并", "/tools/img_merge"),
    link("图片拆分", "/tools/img_split"),
    link("图像灰度化", "/tools/img2gray"),
    link("base64", "/tools/base64"),
    link("16进制转换", "/tools/hex"),
    link("md5", "/tools/md5"),
    link("sha1签名", "/tools/sha1"),
    link("URL编解码", "/tools/urlcoder"),
    link("条形码", "/tools/barcode"),
    link("二维码", "/tools/qrcode"),
    link("随机生成器", "/tools/random_string"),
    # 其他工具
    link("分屏", "/tools/command_center"),
    link("命令模式", "/fs_shell"),
]

xconfig.MENU_LIST = [
    Storage(name = "系统管理", children = sys_tools, need_login = True, need_admin = True),
    Storage(name = "知识库", children = doc_tools, need_login = True),
    Storage(name = "工具箱", children = other_tools),
]

def list_plugins():
    dirname = xconfig.PLUGINS_DIR
    if not os.path.isdir(dirname):
        return []
    links = []
    for name in sorted(os.listdir(dirname)):
        name, ext = os.path.splitext(name)
        links.append(link(name, "/plugins/" + name))
    return links

def list_recent_plugins():
    items = History.get_items("plugins")
    links = list(items)
    links.reverse()
    return links;
                
class SysHandler:

    def GET(self):
        shell_list = []
        dirname = "scripts"
        if os.path.exists(dirname):
            for fname in os.listdir(dirname):
                fpath = os.path.join(dirname, fname)
                if os.path.isfile(fpath) and fpath.endswith(".bat"):
                    shell_list.append(fpath)

        # 自定义链接
        customized_items = []
        db  = xtables.get_storage_table()
        config = db.select_one(where=dict(key="tools", user=xauth.get_current_name()))
        if config is not None:
            config_list = xutils.parse_config_text(config.value)
            customized_items = map(lambda x: Storage(name=x.get("key"), link=x.get("value")), config_list)

        return xtemplate.render("system/system.html", 
            Storage          = Storage,
            os               = os,
            user             = xauth.get_current_user(),
            customized_items = customized_items
        )

class PluginsHandler:

    @xauth.login_required("admin")
    def GET(self):
        return xtemplate.render("system/plugins.html", 
            html_title = "插件",
            recent = list_recent_plugins(),
            plugins = list_plugins())

class ConfigHandler:

    @xauth.login_required("admin")
    def POST(self):
        key = xutils.get_argument("key")
        value = xutils.get_argument("value")
        setattr(xconfig, key, value)
        if key == "BASE_TEMPLATE":
            xmanager.reload()
        if key == "FS_HIDE_FILES":
            setattr(xconfig, key, value == "True")
        return dict(code="success")

xurls = (
    r"/system/sys",   SysHandler,
    r"/system/index", SysHandler,
    r"/system/system", SysHandler,
    r"/system/xconfig", ConfigHandler,
    r"/system/plugins", PluginsHandler,
)
# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2018/03/22 22:57:39
# @modified 2018/03/22 23:16:21
import os
import xconfig
import xutils
import xtemplate

class ListHandler:
    def GET(self):
        path = xutils.get_argument("path")
        scripts = sorted(filter(lambda x: x.endswith(".py"), os.listdir(xconfig.SCRIPTS_DIR)))
        return xtemplate.render("fs/plugins.html", path = path, scripts = scripts)


xurls = (
    r"/fs_api/plugins", ListHandler
)
import os.path
import pickle
import json
import base64

import log
from app.utils import StringUtils, ExceptionUtils
from app.utils.commons import singleton
from config import Config
from app.helper import DbHelper

@singleton
class IndexerHelper:
    _indexers = []

    def __init__(self):
        self.init_config()

    def init_config(self):
        try:
            with open(os.path.join(Config().get_inner_config_path(), "sites.dat"), "r") as f:
                _indexers_json = base64.b64decode(f.read())
                self._indexers = json.loads(_indexers_json).get("indexer")
        except Exception as err:
            ExceptionUtils.exception_traceback(err)

        try:
            for inexer in DbHelper().get_indexer_custom_site():
                self._indexers.append(json.loads(inexer.INDEXER))
        except Exception as err:
            pass

    def get_builtin_indexers(self):
        """
        获取所有内置站点
        """
        _indexers = []
        try:
            with open(join(Config().get_inner_config_path(), "sites.dat"), "r") as f:
                lines = f.readlines()
                for line in lines:
                    base64_string = line.strip()
                    decoded_dict = self.decode_base64_to_dict(base64_string)
                    if decoded_dict:
                        _indexers.append(decoded_dict)
        except Exception as err:
            log.error(f"【Indexers】获取所有内置站点失败：{str(err)}")
            return []
        return _indexers

    def get_builtin_rss_site_graps(self, indexers):
        """
        获取索引对应的促销信息
        """
        _grap_dicts = {}
        for indexer in indexers:
            if "price" in indexer:
                price = indexer["price"]
                url = indexer["domain"]
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                if price and domain:
                    graps_dict = {domain: price}
                    _grap_dicts.update(graps_dict)
        return _grap_dicts

    def get_indexer_info(self, url, public=False):
        for indexer in self._indexers:
            if not public and indexer.get("public"):
                continue
            if StringUtils.url_equal(indexer.get("domain"), url):
                return indexer
        return None

    def get_rss_site_graps(self):
        """
        获取索引对应的促销信息
        """
        if self._builtiInGrapDicts:
            return _builtiInGrapDicts
        _indexers = self.get_builtin_indexers()
        return self.get_builtin_rss_site_graps(_indexers)

    def get_indexer(self,
                    url,
                    siteid=None,
                    cookie=None,
                    name=None,
                    rule=None,
                    public=None,
                    proxy=False,
                    parser=None,
                    ua=None,
                    render=None,
                    language=None,
                    pri=None):
        if not url:
            return None
        for indexer in self._indexers:
            if not indexer.get("domain"):
                continue
            if StringUtils.url_equal(indexer.get("domain"), url):
                return IndexerConf(datas=indexer,
                                   siteid=siteid,
                                   cookie=cookie,
                                   name=name,
                                   rule=rule,
                                   public=public,
                                   proxy=proxy,
                                   parser=parser,
                                   ua=ua,
                                   render=render,
                                   builtin=True,
                                   language=language,
                                   pri=pri)
        return None

    def decode_base64_to_dict(self, base64_string):
        """
        base64字符串转换json字典
        """
        try:
            decoded_bytes = b64decode(base64_string)
            decoded_json = decoded_bytes.decode("utf-8")
            return json.loads(decoded_json)
        except Exception as e:
            return None

class IndexerConf(object):

    def __init__(self,
                 datas=None,
                 siteid=None,
                 cookie=None,
                 name=None,
                 rule=None,
                 public=None,
                 proxy=False,
                 parser=None,
                 ua=None,
                 render=None,
                 builtin=True,
                 language=None,
                 pri=None):
        if not datas:
            return
        # 索引ID
        self.id = datas.get('id')
        # 名称
        self.name = name if name else datas.get('name')
        # 是否内置站点
        self.builtin = builtin
        # 域名
        self.domain = datas.get('domain')
        # 搜索
        self.search = datas.get('search', {})
        # 批量搜索，如果为空对象则表示不支持批量搜索
        self.batch = self.search.get("batch", {}) if builtin else {}
        # 解析器
        self.parser = parser if parser is not None else datas.get('parser')
        # 是否启用渲染
        self.render = render and datas.get("render")
        # 浏览
        self.browse = datas.get('browse', {})
        # 种子过滤
        self.torrents = datas.get('torrents', {})
        # 分类
        self.category = datas.get('category', {})
        # 站点ID
        self.siteid = siteid
        # Cookie
        self.cookie = cookie
        # User-Agent
        self.ua = ua
        # 过滤规则
        self.rule = rule
        # 是否公开站点
        self.public = public if public is not None else datas.get('public')
        # 是否使用代理
        self.proxy = proxy if proxy is not None else datas.get('proxy')
        # 仅支持的特定语种
        self.language = language if language else datas.get('language')
        # 索引器优先级
        self.pri = pri if pri else 0

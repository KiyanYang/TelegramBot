#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  github.py
@Datatime    :  2021/10/16 15:25:58
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.0
@Description :  github API v4
"""
import base64
import json

import requests

from .config import ConfigManager


class GitHubAPIv4:
    def __init__(self, token: str, proxy: str | None = None) -> None:
        self.token = token
        self.headers = {'Authorization': f'token {token}'}
        self.base_url = 'https://api.github.com/graphql'
        self.proxy = proxy
        self.proxies = {'http': proxy, 'https': proxy}

    # 对文件进行base64编码，例如图片文件
    def _file_b64(self, data):
        data_b64 = base64.b64encode(data).decode('UTF-8')
        return data_b64

    # 对字符串进行base64编码，例如字符串，txt等文本文件内的数据
    def _text_b64(self, text: str):
        text_b64 = base64.b64encode(text.encode('UTF-8')).decode('UTF-8')
        return text_b64

    def _get(self, *args, **kwargs):
        if self.proxy is None:
            return requests.get(*args, **kwargs, headers=self.headers)
        else:
            return requests.get(*args, **kwargs, headers=self.headers, proxies=self.proxies)

    def _post(self, *args, **kwargs):
        if self.proxy is None:
            return requests.post(*args, **kwargs, headers=self.headers)
        else:
            return requests.post(*args, **kwargs, headers=self.headers, proxies=self.proxies)

    # 将 dict 数据转换为格式化的 json 数据
    @staticmethod
    def dict2json(text: dict):
        return json.dumps(text, indent=4, ensure_ascii=False)

    def get_raw(self, url: str, type: str | None = None):
        """获取数据

        Parameters
        ----------
        url : str
            链接
        type : str, optional
            类型, 可选: text | json |yaml ,
            如果输入类型不在可选参数内, 则直接返回请求数据, by default None

        Returns
        -------
        str
            类型为 text 时, 返回此类型
        dict
            类型为 json | yaml 时, 返回此类型
        Response
            其他类型返回 Response, 即 requests 的响应类型
        """
        res = self._get(url)
        match type:
            case 'text':
                return res.text
            case 'json':
                return res.json()
            case 'yaml':
                return ConfigManager().yaml_load(text=res.text)
            case _:
                return res

    def query(self, query: str, operation_name: str | None = None, variables: dict | None = None):
        """query

        [extended_summary]

        Parameters
        ----------
        query : str
            query 主体
        operation_name : str, optional
            要执行的操作名称, 仅当查询中存在多个操作时才需要 operation_ame, by default None
        variables : dict, optional
            变量, by default None

        Returns
        -------
        dict
            返回 dict 类型的数据. 注意如果在执行中遇到错误, 并导致不能返回有效响应,
            则 data 条目应该为 null, 并且包含错误 errors 条目

        Raises
        ------
        Exception
            返回错误代码
        """
        payload = {'query': query}
        if operation_name is not None:
            payload |= {'operationName': operation_name}
        if variables is not None:
            payload |= {'variables': variables}
        res = self._post(self.base_url, json=payload)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(f'Query failed. Returning code: {res.status_code}. {query}')

    def get_text(self, owner: str, name: str, expression: str):
        """获取文本文件大小和内容

        Parameters
        ----------
        owner : str
            拥有者
        name : str
            仓库名
        expression : str
            路径表达式, 如`main:README.md`

        Returns
        -------
        dict
            文本文件的大小`byteSize`和内容`text`

        Raises
        ------
        Exception
            如果请求出错, 则返回错误代码;

            如果请求正常, 但响应包含 errors 条目, 则返回响应数据.
        """
        query_get_text = '''
            query GetText($owner: String!, $name: String!, $expression: String) {
              repository(owner: $owner, name: $name) {
                object(expression: $expression) {
                  ... on Blob {
                    byteSize
                    text
                  }
                }
              }
            }'''
        vars = {'owner': owner, 'name': name, 'expression': expression}
        res = self.query(query_get_text, variables=vars)
        if ('data' in res.keys()) and ('errors' not in res.keys()):
            return res['data']['repository']['object']
        else:
            raise Exception(f'Query succeed. But return "errors": {res}')

    def get_oid(self, owner: str, name: str, branch: str):
        """获取 oid

        Parameters
        ----------
        owner : str
            拥有者
        name : str
            仓库名
        branch : str
            分支, 如`main`

        Returns
        -------
        str
            oid

        Raises
        ------
        Exception
            如果请求出错, 则返回错误代码;

            如果请求正常, 但响应包含 errors 条目, 则返回响应数据.
        """
        query_get_oid = '''
            query GetOid($owner: String!, $name: String!, $expression: String) {
              repository(name: $name, owner: $owner) {
                object(expression: $expression) {
                  oid
                }
              }
            }'''
        vars = {'owner': owner, 'name': name, 'expression': branch}
        res = self.query(query_get_oid, variables=vars)
        if ('data' in res.keys()) and ('errors' not in res.keys()):
            return res['data']['repository']['object']['oid']
        else:
            raise Exception(f'Query succeed. But return "errors": {res}')

    def get_rate_limit(self):
        """查询 API 速率限制状态

        GraphQL API v4 的速率限制为每小时 5,000 点

        Returns
        -------
        dict
            包含以下字段\n
            `cost` 字段可返回根据速率限制计算的当前调用的点成本\n
            `limit` 字段可返回客户端在 60 分钟期限内允许使用的最大客户端点数\n
            `nodeCount` 字段可返回此查询可能返回的最大节点数\n
            `remaining` 字段可返回当前速率限制期限内剩余的点数\n
            `resetAt` 字段可返回当前速率限制期限内重置的时间（UTC 时期秒数）\n
            `uesd` 字段可返回当前速率限制窗口中使用的点数
        """
        query_rate_limit = '''
            query GetRateLimit {
              rateLimit {
                cost
                limit
                nodeCount
                remaining
                resetAt
                used
              }
            }'''
        res = self.query(query_rate_limit)
        return res['data']['rateLimit']

    def add_text(
        self,
        owner: str,
        name: str,
        branch: str,
        path: str,
        contents: str,
        message_headline: str,
        message_body: str | None = None,
    ):
        """增加或修改文件

        Parameters
        ----------
        owner : str
            拥有者
        name : str
            仓库名
        branch : str
            分支, 如`main`
        path : str
            路径, 如`docs/README.md`
        contents : str
            文件内容
        message_headline : str
            git 说明消息标题
        message_body : str, optional
            git 说明消息内容, 如果为空, 则与`message_headline`一样, by default None
        """
        query_change_file = '''
            mutation ChangeFile(
              $owner_name: String
              $branch: String
              $head_oid: String
              $path: String
              $contents: String
              $message_headline: String
              $message_body: String
            ) {
              createCommitOnBranch(
                input: {
                  branch: { repositoryNameWithOwner: $owner_name, branchName: $branch }
                  expectedHeadOid: $head_oid
                  fileChanges: { additions: [{ path: $path, contents: $contents }] }
                  message: { body: $message_body, headline: $message_headline }
                }
              ) {
                clientMutationId
              }
            }'''
        if message_body is None:
            message_body = message_headline
        vars = {
            'owner_name': f'{owner}/{name}',
            'branch': branch,
            'head_oid': self.get_oid(owner, name, branch),
            "path": path,
            "contents": self._text_b64(contents),
            "message_headline": message_headline,
            "message_body": message_body,
        }
        self.query(query_change_file, variables=vars)


if __name__ == '__main__':
    pass

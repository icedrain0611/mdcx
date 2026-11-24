# -*- coding: utf-8 -*-
"""
javdb Cookie 校验回归测试。

契约：调用方通过 headers 显式提供的 Cookie，必须作为该请求唯一且权威的 Cookie 发出；
即使共享单例 curl_session 的 cookie jar 已被同域访客 cookie 污染，也不得额外注入
陈旧 cookie 形成第二个 Cookie 头（否则服务器会采用访客会话，导致任何 Cookie 都校验失败）。

使用进程内本地 HTTP 服务器作为真实、确定性的依赖（不 mock 被测代码），
通过标准库 unittest 运行，无需新增第三方依赖。
"""
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from models.base.web import curl_html, web

GUEST_SESSION = "GUEST_anon_session_value"
AUTH_COOKIE = "theme=auto; over18=1; cf_clearance=clearanceXYZ; _jdb_session=AUTH_real_session_value"


class RecordingHandler(BaseHTTPRequestHandler):
    records = []

    def do_GET(self):
        # get_all 保留重复的 Cookie 头，便于断言“恰好一个”
        cookie_headers = self.headers.get_all("Cookie") or []
        self.records.append({"path": self.path, "cookies": list(cookie_headers)})

        body = b"<html><body>/logout</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        # 模拟真实站点：下发访客会话，污染共享 cookie jar
        self.send_header("Set-Cookie", f"_jdb_session={GUEST_SESSION}; Path=/")
        self.send_header("Set-Cookie", "theme=auto; Path=/")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class JavdbCookieTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), RecordingHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        RecordingHandler.records = []
        web.curl_session.cookies.clear()  # 每个用例前清空共享单例 jar

    def tearDown(self):
        web.curl_session.cookies.clear()  # 用例后清理，避免污染其他测试

    def _record(self, path):
        matches = [r for r in RecordingHandler.records if r["path"] == path]
        return matches[-1]

    def test_explicit_cookie_is_sole_cookie_when_jar_contaminated(self):
        # 探针/回归：先无 cookie 请求，让共享 jar 累积访客会话
        ok, _ = curl_html(self.base + "/warmup", proxies=False)
        self.assertTrue(ok)
        self.assertEqual(web.curl_session.cookies.get("_jdb_session"), GUEST_SESSION)

        # 再带显式 Cookie 校验
        ok, _ = curl_html(self.base + "/check", headers={"cookie": AUTH_COOKIE}, proxies=False)
        self.assertTrue(ok)
        cookies = self._record("/check")["cookies"]

        self.assertEqual(len(cookies), 1, f"期望恰好一个 Cookie 头，实际: {cookies}")
        self.assertEqual(cookies[0], AUTH_COOKIE)
        self.assertNotIn(GUEST_SESSION, cookies[0])
        self.assertIn("_jdb_session=AUTH_real_session_value", cookies[0])

    def test_explicit_cookie_sent_with_clean_jar(self):
        ok, _ = curl_html(self.base + "/clean", headers={"cookie": AUTH_COOKIE}, proxies=False)
        self.assertTrue(ok)
        self.assertEqual(self._record("/clean")["cookies"], [AUTH_COOKIE])

    def test_no_cookie_passthrough(self):
        ok, _ = curl_html(self.base + "/none", proxies=False)
        self.assertTrue(ok)
        self.assertEqual(self._record("/none")["cookies"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

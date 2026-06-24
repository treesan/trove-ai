"""微信公众号 cgiDataNew 解析器单元测试。

无 pytest 依赖，可直接 `python tests/test_wechat_cgidata.py` 运行。
fixture 使用内联构造的 cgiDataNew JS 字面量（覆盖旧 JsDecode 格式与新 `'0'*1` 格式），
不依赖外部文件，保证可复现。

对应 OpenSpec change: enhance-wechat-article-parsing
设计文档: https://my.feishu.cn/docx/CVnsdcmqgoRVLYxY6ohcdIVOnVf
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.parser_service import (  # noqa: E402
    _parse_cgi_data_new,
    _normalize_cgi_literal,
    _decode_js_string,
    _validate_cgi_data,
    _to_int,
    _extract_publish_time,
    _format_timestamp,
    _normalize_wechat_url,
    _normalize_code_snippets,
    _code_lang_callback,
    _render_content_type_0,
    _render_content_type_8,
    _render_content_type_10,
    _render_pay_preview,
    _is_pay_placeholder,
)
from markdownify import MarkdownConverter  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {name}")
    else:
        _failed += 1
        print(f"  ✗ {name}" + (f"  — {detail}" if detail else ""))


# ── 内联 fixture ──────────────────────────────────────────────
# 新格式 (当前生产): '0' * 1 表达式 + \xNN 转义 + CJK
NEW_FORMAT_HTML = """
<html><script>
window.cgiDataNew = {
    base_resp: { ret: '0' * 1, errmsg: 'ok' },
    nick_name: 'AI大气层',
    title: '谷歌扔出开源核弹！2.4B实时音乐模型',
    author: 'AI大气层',
    round_head_img: 'http://mmbiz.qpic.cn/mmbiz_png/abc/0?wx_fmt=png',
    content_noencode: '\\x3csection\\x3e\\x3ch2\\x3e小标题\\x3c/h2\\x3e\\x3cp\\x3e这是一段足够长的正文内容用于测试解析与 markdown 转换，确保不触发短内容回退路径。\\x3c/p\\x3e\\x3cp\\x3e\\x3cimg data-src=\\x22http://mmbiz.qpic.cn/mmbiz_jpg/pic1/640\\x22 alt=\\x22图1\\x22 /\\x3e\\x3c/p\\x3e\\x3cp\\x3e第二段正文，继续补充内容长度。\\x3c/p\\x3e\\x3c/section\\x3e',
    create_time: '2026-06-11 11:29',
    ori_create_time: '1781148581',
    item_show_type: '0' * 1,
    is_pay_subscribe: '0' * 1,
    picture_page_info_list: [
        { cdn_url: 'https://mmbiz.qpic.cn/sz_mmbiz_jpg/x/640?from=appmsg' },
        { cdn_url: 'https://mmbiz.qpic.cn/sz_mmbiz_jpg/y/640?from=appmsg' },
    ],
    text_page_info: { is_user_title: '1' },
};
</script></html>
"""

# 旧格式 (历史): JsDecode('...') 包装
OLD_FORMAT_HTML = """
<html><script>
window.cgiDataNew = {
    base_resp: { ret: '0' * 1, errmsg: JsDecode('ok') },
    nick_name: JsDecode('金榜时代官微'),
    title: JsDecode('睡前数学知识点｜Day15'),
    author: JsDecode('jinbang'),
    round_head_img: JsDecode('http://mmbiz.qpic.cn/head/0'),
    content_noencode: JsDecode('\\x3csection\\x3e\\x3cp\\x3e旧格式正文\\x3c/p\\x3e\\x3c/section\\x3e'),
    create_time: JsDecode('2025-12-04 18:00'),
    item_show_type: '0' * 1,
    is_pay_subscribe: '0' * 1,
};
</script></html>
"""

# 含代码块的 content_noencode (旧格式 JsDecode 解码后)
CODE_SNIPPET_HTML = (
    '<section><p>intro</p>'
    '<section class="code-snippet__fix">'
    '<span class="code-snippet__line-index">1</span>'
    '<pre data-lang="python"><code>def hello():</code><code>    print("hi")</code></pre>'
    '</section><p>outro</p></section>'
)


def test_parse_new_format():
    print("\n[1] 新格式解析 (CJK + '0'*1 + \\xNN)")
    cgi = _parse_cgi_data_new(NEW_FORMAT_HTML)
    check("parses (not None)", cgi is not None)
    if not cgi:
        return
    check("title CJK intact", "谷歌" in cgi.get("title", ""), repr(cgi.get("title", "")[:20]))
    check("item_show_type is str '0'", cgi.get("item_show_type") == "0", repr(cgi.get("item_show_type")))
    check("is_pay_subscribe is str '0'", cgi.get("is_pay_subscribe") == "0", repr(cgi.get("is_pay_subscribe")))
    check("picture_page_info_list len 2", len(cgi.get("picture_page_info_list") or []) == 2)
    check("content_noencode decoded <section>", "<section" in (cgi.get("content_noencode") or ""))
    check("create_time string date", cgi.get("create_time") == "2026-06-11 11:29")
    check("base_resp.ret str '0'", cgi.get("base_resp", {}).get("ret") == "0")
    check("validate passes", _validate_cgi_data(cgi))


def test_parse_old_format():
    print("\n[1] 旧格式解析 (JsDecode)")
    cgi = _parse_cgi_data_new(OLD_FORMAT_HTML)
    check("parses (not None)", cgi is not None)
    if not cgi:
        return
    check("title intact (JsDecode stripped)", cgi.get("title") == "睡前数学知识点｜Day15", repr(cgi.get("title")))
    check("nick_name intact", cgi.get("nick_name") == "金榜时代官微", repr(cgi.get("nick_name")))
    check("errmsg intact (JsDecode + paren)", cgi.get("base_resp", {}).get("errmsg") == "ok", repr(cgi.get("base_resp", {}).get("errmsg")))
    check("content_noencode decoded", "旧格式正文" in (cgi.get("content_noencode") or ""))
    check("create_time string date", cgi.get("create_time") == "2025-12-04 18:00")
    check("validate passes", _validate_cgi_data(cgi))


def test_parse_no_match():
    print("\n[1] 无 cgiDataNew → None")
    check("returns None", _parse_cgi_data_new("<html><body>nothing</body></html>") is None)


def test_decode_js_string():
    print("\n[1] _decode_js_string")
    check("\\x3c → <", _decode_js_string("\\x3c") == "<")
    check("\\u4e2d → 中", _decode_js_string("\\u4e2d") == "中")
    check("\\n → newline", _decode_js_string("a\\nb") == "a\nb")
    check("CJK preserved", _decode_js_string("谷歌") == "谷歌")


def test_normalize_cjk_no_crash():
    print("\n[1] 归一化 CJK 不崩 (latin1 regression)")
    blob = "{ title: '谷歌扔出开源核弹', x: '0' * 1, }"
    norm = _normalize_cgi_literal(blob)
    check("no exception + CJK kept", "谷歌" in norm, repr(norm[:40]))


def test_to_int():
    print("\n[2] _to_int")
    check("'0' → 0", _to_int("0") == 0)
    check("'1' → 1", _to_int("1") == 1)
    check("None → default 0", _to_int(None) == 0)
    check("'' → default 0", _to_int("") == 0)
    check("int 8 → 8", _to_int(8) == 8)
    check("garbage → default", _to_int("abc") == 0)


def test_publish_time():
    print("\n[2] 发布时间提取")
    check("string date passthrough", _extract_publish_time("", {"create_time": "2026-06-11 11:29"}) == "2026-06-11 11:29")
    ts = _extract_publish_time("", {"create_time": "1781148581"})
    check("unix ts → UTC+8 str", ts.startswith("2026-"), repr(ts))
    check("ori_create_time fallback", _extract_publish_time("", {"ori_create_time": "1781148581"}).startswith("2026-"))
    check("empty → ''", _extract_publish_time("<html></html>", {}) == "")
    check("_format_timestamp UTC+8", _format_timestamp(1781148581).startswith("2026-"))


def test_normalize_url():
    print("\n[2] URL 归一化")
    cases = [
        ('"https://mp.weixin.qq.com/s/abc"', "https://mp.weixin.qq.com/s/abc"),
        ("'https://mp.weixin.qq.com/s/abc'", "https://mp.weixin.qq.com/s/abc"),
        ("https\\://mp.weixin.qq.com/s/abc", "https://mp.weixin.qq.com/s/abc"),
        ("http://mp.weixin.qq.com/s/abc", "https://mp.weixin.qq.com/s/abc"),
        ("mp.weixin.qq.com/s/abc", "https://mp.weixin.qq.com/s/abc"),
        ("https://mp.weixin.qq.com/s?a=1&amp;b=2", "https://mp.weixin.qq.com/s?a=1&b=2"),
    ]
    for raw, exp in cases:
        check(f"url {raw[:28]!r}", _normalize_wechat_url(raw) == exp, f"got {_normalize_wechat_url(raw)!r}")


def test_code_snippets():
    print("\n[3] 代码块归一化 + markdown fenced")
    soup = BeautifulSoup(CODE_SNIPPET_HTML, "lxml")
    _normalize_code_snippets(soup)
    pre = soup.find("pre", attrs={"data-lang": "python"})
    check(".code-snippet__fix → pre[data-lang=python]", pre is not None)
    check("line-index stripped", not soup.select(".code-snippet__line-index"))
    if pre:
        txt = pre.get_text()
        check("code lines joined", "def hello():\n    print(\"hi\")" == txt, repr(txt))
    md = MarkdownConverter(heading_style="ATX", bullets="-", code_language_callback=_code_lang_callback)
    out = md.convert(str(soup))
    check("fenced block ```python", "```python" in out, out[:100])
    check("code body in markdown", "def hello():" in out)


# mdnice 风格代码块: <section style="background-color:#1e1e1e"><code style="display:block">
# 用 \xa0 (nbsp, 来自微信 &nbsp;) 做缩进, 验证 _strip_common_indent 处理
MDNICE_CODE_HTML = (
    '<section style="margin: 15px 0;padding: 15px;background-color: #1e1e1e;">'
    '<code style="font-family: Consolas, monospace;display: block;">'
    '<span leaf="">\xa0\xa0\xa0\xa0 # 一键安装 uv</span><span leaf=""><br/></span>'
    '<span leaf="">\xa0\xa0\xa0\xa0 curl -LsSf https://astral.sh/uv/install.sh | sh</span><span leaf=""><br/></span>'
    '<span leaf="">\xa0\xa0\xa0\xa0 # 创建并激活虚拟环境</span><span leaf=""><br/></span>'
    '<span leaf="">\xa0\xa0\xa0\xa0 uv venv .venv</span><span leaf=""><br/></span>'
    '<span leaf="">\xa0\xa0\xa0\xa0 source .venv/bin/activate</span><span leaf=""><br/></span>'
    '</code></section>'
)


def test_mdnice_code_snippets():
    print("\n[3] mdnice 风格代码块归一化")
    soup = BeautifulSoup(MDNICE_CODE_HTML, "lxml")
    _normalize_code_snippets(soup)
    pre = soup.find("pre")
    check("mdnice <section><code> → <pre>", pre is not None)
    check("section removed", not soup.find("section"))
    if pre:
        txt = pre.get_text()
        check("curl command preserved", "curl -LsSf https://astral.sh/uv/install.sh" in txt, repr(txt[:80]))
        check("common 4-space indent stripped", "一键安装 uv" in txt and not txt.startswith("    "), repr(txt[:40]))
    md = MarkdownConverter(heading_style="ATX", bullets="-", code_language_callback=_code_lang_callback)
    out = md.convert(str(soup))
    check("fenced block ```(no lang)", "```\n" in out, out[:120])
    check("uv install line in fenced block", "curl -LsSf https://astral.sh/uv/install.sh" in out)
    # plain (non-code) section must NOT be converted
    plain_soup = BeautifulSoup(
        '<section style="margin: 0;"><p>not code</p></section>', "lxml")
    _normalize_code_snippets(plain_soup)
    check("plain section left intact", plain_soup.find("section") is not None)


def test_renderers():
    print("\n[4] 三种类型渲染 + 付费")
    cgi0 = _parse_cgi_data_new(NEW_FORMAT_HTML)
    r0 = _render_content_type_0(cgi0)
    check("type0 renders non-empty", bool(r0) and "<section" in r0)

    r8 = _render_content_type_8(cgi0)
    check("type8 has picture_item x2", r8.count("picture_item") == 2)
    check("type8 has 图1/图2 labels", "图1" in r8 and "图2" in r8)

    t10 = {"text_page_info": {"content_noencode": "line1\nline2"}}
    r10 = _render_content_type_10(t10)
    check("type10 newline → <br />", "line1<br />line2" in r10)
    t10b = {"text_page_info": {"content": "fallback"}}
    check("type10 fallback 'content' field", "fallback" in _render_content_type_10(t10b))

    pay = {"pay_subscribe_info": {"fee": "199", "desc": "付费可看\n完整内容"}}
    rp = _render_pay_preview(pay)
    check("pay price 1.99元 (199分)", "1.99元" in rp, rp)
    check("pay desc <br />", "付费可看<br />完整内容" in rp)


def test_is_pay_placeholder():
    print("\n[4] _is_pay_placeholder")
    check("empty → True", _is_pay_placeholder(""))
    check("whitespace only → True", _is_pay_placeholder("   \n  "))
    check("mp-pay-preview-filter → True", _is_pay_placeholder('<div class="mp-pay-preview-filter"></div>'))
    check("real content → False", not _is_pay_placeholder("<p>正文内容</p>"))


def test_validate_cgi_data():
    print("\n[1] _validate_cgi_data (防 silent corruption)")
    check("None → False", not _validate_cgi_data(None))
    check("empty title → False", not _validate_cgi_data({"title": "", "content_noencode": "x" * 30}))
    check("title + content → True", _validate_cgi_data({"title": "t", "content_noencode": "x" * 25}))
    check("title + picture (type8) → True", _validate_cgi_data({"title": "t", "picture_page_info_list": [{"cdn_url": "u"}]}))
    check("title + short content, no list → False", not _validate_cgi_data({"title": "t", "content_noencode": "short"}))


def test_no_double_proxy():
    print("\n[5/6] clean_to_markdown 无双重代理")
    from app.services.parser_service import ParserService
    ps = ParserService()
    cgi0 = _parse_cgi_data_new(NEW_FORMAT_HTML)
    result = ps._render_from_cgi_data(cgi0, NEW_FORMAT_HTML, "https://mp.weixin.qq.com/s/x")
    md = ps.clean_to_markdown(result["raw_content"], platform="wechat")
    check("no double-encoded proxy", "/api/images/proxy?url=%2F" not in md, "double-encoded found")
    check("proxy URLs present", "/api/images/proxy?url=" in md)
    check("no CODEBLOCK_PLACEHOLDER leakage", "CODEBLOCK_PLACEHOLDER" not in md)
    # reprocess idempotent (B1)
    md2 = ps.clean_to_markdown(result["raw_content"], platform="wechat")
    check("reprocess idempotent", md == md2)


def main():
    for fn in [
        test_parse_new_format, test_parse_old_format, test_parse_no_match,
        test_decode_js_string, test_normalize_cjk_no_crash, test_validate_cgi_data,
        test_to_int, test_publish_time, test_normalize_url,
        test_code_snippets, test_mdnice_code_snippets, test_renderers, test_is_pay_placeholder,
        test_no_double_proxy,
    ]:
        fn()
    print(f"\n==== {_passed} passed, {_failed} failed ====")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())

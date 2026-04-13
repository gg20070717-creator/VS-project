import requests
import time
import re
import json
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from pathlib import Path
from typing import Dict, List, Optional

# 设置 session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0'
})

# 设置 cookies（已按你的要求直接写入；如需覆盖可继续用 FORUM_COOKIE 环境变量）
cookie_string = os.getenv(
    "FORUM_COOKIE",
    "cookieconsent_status=dismiss; keepalive='48AbMysL/UPUUuGWN3GRNvwFUqn4/K9vZpyBL+TvbUE=; _bypass_cache=true; _t=y6P36ZGamj76Y8Yf%2BFCSnbrmRfisQgdTEU0dDvGMkFReCFRlOfCFBWCtabljtiD%2FxBvq%2B7N0t4JI6fyXmfqCk%2BaGIDYMkkfBGvTADXQwcB%2BGQ2CIP3xWhK9vfMk3NlnZlNRu5zuQcqWyURazhNKsfScmO9bvYcfVhmoVKlxdfkNO0XZ5Fqrjgub%2FMDU5PKYU5WmFZYFEzEICHmOo556lpEs9wCj5ZlipRHL%2BFeHMFMQc1sWDYx1IB6MVd%2BP7ANUKLYwG4opJnCF60yealA9hLnvS1OaJ7VELv3Zx89NqU3%2BcSMd%2FIEz%2BdbH9WOM%3D--sPaDDvg1UItxq606--F3oalrgEWZrAsu2La16WaA%3D%3D; _forum_session=N8n9smrjINYsFLtRY6dD9EdoEemfIVurLF6cFT%2Fs0Lm3Rf84tG2asad0ANif10kP%2Bo2nDGpbfvfncw8CvWsIitf89fNjLNAMwtDp5GO4paxc18N9qqiJ%2BlwNmtO%2BJwoxrJ75HzrFSjdQHb10iu8ezZuHuTc2Cg5zU1frrS2y8lE4yr09x%2BBLUKTLYJTMCz%2FWbTqYad2ozzayzoarlddgvXfo6q0p0R8i%2FP3j6xjTdYIqDke81JdbZ46QN%2BAQGsxFcoFYzoysDECcN0egCjO2X2zGkFiP0ynFSkoCtBndh0fNpQSa9ZpFEJIdEQf3w2vQnAuvRpnX%2BR7cQ3Y8piOWXGoJW9yqQPnJT1dDNY4WRvFuY1skA62GZnWpvmlom4zacc8sxl%2BPxBztCMtNo9yQfCAmZt6rey43HxBD4dIcFZ94FbtLhc4icijEdJjCc%2FjReS7EF%2FcwqL3thoNqwH7oGe3f57Bj3bMKKzY%3D--1%2BG4A0gfNIVY3Gpk--QuarluTAHFxG3ZaD6OoEnw%3D%3D",
)
cookies_dict = {}
for item in cookie_string.split('; '):
    if '=' in item:
        key, value = item.split('=', 1)
        cookies_dict[key] = value
session.cookies.update(cookies_dict)

# 设置 DeepSeek 客户端（记得设置环境变量 DEEPSEEK_API_KEY）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# ======== 已按你提供的信息写入配置 ========
THREAD_URL = os.getenv("THREAD_URL", "https://shuiyuan.sjtu.edu.cn/t/topic/453635")
REPLY_POST_URL = os.getenv("REPLY_POST_URL", "https://shuiyuan.sjtu.edu.cn/posts")
BOT_USERNAME = "Tighnari果果猪"
WAKE_PREFIX = "【小提】"
MODEL_NAME = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
BACKLOG_SCAN_LIMIT = int(os.getenv("BACKLOG_SCAN_LIMIT", "30"))
RECENT_CONTEXT_COUNT = int(os.getenv("RECENT_CONTEXT_COUNT", "30"))
LIGHT_MODE_LATEST_ONLY = os.getenv("LIGHT_MODE_LATEST_ONLY", "true").lower() == "true"
LIGHT_MODE_CHECK_COUNT = int(os.getenv("LIGHT_MODE_CHECK_COUNT", "5"))
STATE_FILE = Path(__file__).with_name("ggz_bot_state.json")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
TOPIC_ID = int(os.getenv("TOPIC_ID", "453635"))
TOPIC_JSON_URL = os.getenv("TOPIC_JSON_URL", f"https://shuiyuan.sjtu.edu.cn/t/topic/{TOPIC_ID}.json")
TOPIC_POSTS_URL = os.getenv("TOPIC_POSTS_URL", f"https://shuiyuan.sjtu.edu.cn/t/{TOPIC_ID}/posts.json")
CSRF_TOKEN = os.getenv(
    "CSRF_TOKEN",
    "dBZAmtGotGsUkjOxz4PKwT3bBFwYHqmDd7iIw-TVs-rRimwszuT4QYVSQ2SfkVgfsQHlItPPukUzImui0EVvEQ",
)

# 触发格式：@Tighnari果果猪 【小提】+你的问题
TRIGGER_REGEX = re.compile(
    r"^\s*[@＠]Tighnari果果猪\s*【小提】\s*(?:\+|：|:)?\s*(.+?)\s*$",
    re.IGNORECASE | re.DOTALL,
)

SYSTEM_PROMPT = (
    "你是论坛‘小提’，人格参考《原神》提纳里：温柔、知性、耐心、有趣、可爱、毒舌"
    "你擅长互动，能回答其他人的问题并完成大家对你提出的要求"
    "观察细致，擅长把复杂问题讲清楚。你的语气友好，"
    "相当轻松幽默，会常用机灵的比喻或一句俏皮话。\n\n"
    "【当前主题背景（重要）】\n"
    "- 楼名：日记水楼4.0，整体氛围是轻松闲聊、日常碎片、互相接梗。\n"
    "- 楼主：存档读取（4ur0r4 or 404）。\n"
    "- 楼内定位：不是严肃问答区，更像大家一边喝创咖一边聊天的温暖角落。\n"
    "- 常见内容：学习压力吐槽、生活日常、夜间emo、玩梗互动、楼友互相调侃。\n"
    "- 互动原则：友善发言、尊重楼友、多接梗。\n"
    "- 活跃楼友包含：果果猪、苏西、wbzd、亚兜、木子丰、八奈见、北暮、中杯小狼。\n"
    "- 你的任务：给出有趣、有人味、一针见血的毒舌回复。\n\n"
    "【角色语气要求】\n"
    "1. 回答自然，像在和同学交流。\n"
    "2. 面对学习、生活、情绪问题，优先给可执行建议，必要时分点。\n"
    "3. 可以共情与适当夸张煽情。\n"
    "4. 避免说教和高高在上，保持平等、温和、聪明、可爱。\n"
    "5. 不要捏造亲身经历；不确定信息要明确说明不确定。\n\n"
    "【论坛场景要求】\n"
    "1. 默认中文回复。\n"
    "2. 内容通常 120~320 字；若问题复杂可到 420 字。\n"
    "3. 优先结合给出的楼内上下文作答，注意前后文人物关系和语境。\n"
    "4. 回复正文里不写任何系统说明，不出现‘作为AI’等字样。\n"
    "5. 不要输出代码块或Markdown标题；保持可直接发帖的自然段落。\n\n"
    "【风格加分项】\n"
    "- 结尾可附一句简短、机智、温柔的收束句。\n"
    "- 在不影响清晰度的前提下，语言可以更有画面感。\n"
    "- 允许少量自然语气词和轻微网络口吻，让发言更像真实楼友。\n"
    "- 优先给‘能立刻做的一步’，让对方读完就能行动。"
    "多加入一些可爱的emoji。"
)

SIGNATURE_BBCODE = "\n\n---\n[right]ai小提为您服务:pig:[/right]"


def load_state() -> Dict[str, object]:
    if not STATE_FILE.exists():
        return {"last_seen_post_id": None, "handled_post_ids": []}
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if "last_seen_post_id" not in state:
            state["last_seen_post_id"] = None
        if "handled_post_ids" not in state or not isinstance(state["handled_post_ids"], list):
            state["handled_post_ids"] = []
        return state
    except json.JSONDecodeError:
        return {"last_seen_post_id": None, "handled_post_ids": []}


def save_state(state: Dict[str, object]) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_thread_html() -> str:
    # 保留旧函数名，避免调用处改动太大；实际返回 JSON 文本
    if not TOPIC_JSON_URL:
        raise ValueError("请先设置 TOPIC_JSON_URL")

    resp = session.get(
        TOPIC_JSON_URL,
        headers={"Accept": "application/json, text/plain, */*"},
        timeout=20,
        allow_redirects=True,
    )

    if "jaccount.sjtu.edu.cn" in resp.url:
        raise RuntimeError("当前 Cookie 已失效或未登录，已跳转到统一认证页面，请更新 FORUM_COOKIE")

    if resp.status_code == 403 and "not_logged_in" in resp.text:
        raise RuntimeError("论坛返回未登录（403 not_logged_in），请更新 FORUM_COOKIE")

    resp.raise_for_status()
    return resp.text


def fetch_topic_data() -> Dict:
    raw = fetch_thread_html()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"帖子接口返回非 JSON 内容: {exc}") from exc


def fetch_posts_by_ids(post_ids: List[str]) -> List[Dict[str, str]]:
    if not post_ids:
        return []

    params = [("post_ids[]", str(pid)) for pid in post_ids]
    resp = None
    max_retry = 3
    for attempt in range(max_retry):
        resp = session.get(
            TOPIC_POSTS_URL,
            params=params,
            headers={"Accept": "application/json, text/plain, */*"},
            timeout=20,
            allow_redirects=True,
        )
        if resp.status_code != 429:
            break
        retry_after = int(resp.headers.get("Retry-After", "3") or "3")
        wait_seconds = max(2, retry_after)
        print(f"请求过快(429)，{wait_seconds} 秒后重试 ({attempt + 1}/{max_retry})")
        time.sleep(wait_seconds)

    if resp is None:
        raise RuntimeError("帖子详情请求失败：未获得响应")

    if "jaccount.sjtu.edu.cn" in resp.url:
        raise RuntimeError("当前 Cookie 已失效或未登录，已跳转到统一认证页面，请更新 FORUM_COOKIE")

    if resp.status_code == 403 and "not_logged_in" in resp.text:
        raise RuntimeError("论坛返回未登录（403 not_logged_in），请更新 FORUM_COOKIE")

    resp.raise_for_status()
    data = resp.json()
    items = data.get("post_stream", {}).get("posts", [])

    posts = []
    for item in items:
        post_id = str(item.get("id", "")).strip()
        if not post_id:
            continue
        posts.append({
            "post_id": post_id,
            "post_number": str(item.get("post_number", "")).strip() or post_id,
            "author": (item.get("username") or item.get("name") or "").strip(),
            "content": (item.get("raw") or item.get("cooked") or "").strip(),
        })
    return posts


def parse_posts(raw_json: str) -> List[Dict[str, str]]:
    """兼容旧调用：从 topic json 中的 posts 字段解析（通常只有部分楼层）。"""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"帖子接口返回非 JSON 内容: {exc}") from exc
    items = data.get("post_stream", {}).get("posts", [])
    result: List[Dict[str, str]] = []
    for item in items:
        post_id = str(item.get("id", "")).strip()
        if not post_id:
            continue
        result.append({
            "post_id": post_id,
            "post_number": str(item.get("post_number", "")).strip() or post_id,
            "author": (item.get("username") or item.get("name") or "").strip(),
            "content": (item.get("raw") or item.get("cooked") or "").strip(),
        })
    return result


def extract_question(content: str) -> Optional[str]:
    raw_text = (content or "").strip()
    # Discourse 有时返回 cooked(HTML)，这里统一转成纯文本再匹配
    if "<" in raw_text and ">" in raw_text:
        raw_text = BeautifulSoup(raw_text, "html.parser").get_text(" ", strip=True)

    normalized = re.sub(r"\s+", " ", raw_text).strip()
    match = TRIGGER_REGEX.match(normalized)
    if not match:
        return None
    question = match.group(1).strip()
    return question if question else None


def to_plain_text(content: str) -> str:
    text = (content or "").strip()
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_recent_context(target_post_id: str, stream_ids: List[str], limit: int) -> str:
    if limit <= 0 or not stream_ids or target_post_id not in stream_ids:
        return ""

    target_idx = stream_ids.index(target_post_id)
    start_idx = max(0, target_idx - limit + 1)
    context_ids = stream_ids[start_idx:target_idx + 1]
    context_posts = fetch_posts_by_ids(context_ids)
    posts_map = {p["post_id"]: p for p in context_posts}

    lines: List[str] = []
    for pid in context_ids:
        post = posts_map.get(pid)
        if not post:
            continue
        floor = post.get("post_number", post["post_id"])
        author = post.get("author", "未知用户") or "未知用户"
        content = to_plain_text(post.get("content", ""))
        if len(content) > 120:
            content = content[:120] + "..."
        lines.append(f"#{floor} @{author}: {content}")

    return "\n".join(lines)


def generate_reply(question: str, author: str, recent_context: str) -> str:
    context_block = recent_context if recent_context else "（无可用上下文）"
    user_prompt = (
        f"论坛用户 {author} 在帖子里提问：\n{question}\n\n"
        "以下是该楼最近的对话上下文（由旧到新）：\n"
        f"{context_block}\n\n"
        "请结合上下文给出可发布的论坛回复，不要使用代码块，不要写多余前缀。"
    )
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1.05,
        max_tokens=700,
    )
    return (resp.choices[0].message.content or "").strip()


def compose_final_reply(base_reply: str, author: str) -> str:
    mention = f"@{author}"
    clean_reply = (base_reply or "").strip()
    if clean_reply.startswith(mention):
        body = clean_reply
    else:
        body = f"{mention} {clean_reply}"
    if "ai小提为您服务" not in body:
        body = f"{body}{SIGNATURE_BBCODE}"
    return body


def send_reply(reply_text: str, reply_to_post_number: str, author: str) -> None:
    """
    这里是发帖接口占位。
    你需要根据论坛真实请求补充 payload 字段，比如帖子ID、csrf token、回复内容字段名。
    """
    if DRY_RUN:
        print("[DRY_RUN] 将要发送：")
        print(reply_text)
        return

    final_text = compose_final_reply(reply_text, author)
    try:
        reply_to_num = int(reply_to_post_number)
    except (TypeError, ValueError):
        reply_to_num = 0

    payload = {
        "raw": final_text,
        "topic_id": TOPIC_ID,
        "reply_to_post_number": reply_to_num,
        "archetype": "regular",
        "is_warning": "false",
    }
    headers = {
        "X-CSRF-Token": CSRF_TOKEN,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": THREAD_URL,
        "Origin": "https://shuiyuan.sjtu.edu.cn",
    }
    resp = session.post(REPLY_POST_URL, data=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    try:
        data = resp.json()
        print(
            "发送成功: post_number={} reply_to_post_number={}"
            .format(data.get("post_number"), data.get("reply_to_post_number"))
        )
    except ValueError:
        print("发送成功: 服务端未返回JSON")


def pick_new_post_ids(stream_ids: List[str], last_seen_post_id: Optional[str]) -> List[str]:
    if not stream_ids:
        return []
    if not last_seen_post_id:
        # 首次启动：只记录当前最新楼层，不处理历史6000+楼
        return []

    if last_seen_post_id in stream_ids:
        idx = stream_ids.index(last_seen_post_id)
        return stream_ids[idx + 1:]

    # 如果 stream 中找不到上次id，就按数值兜底
    try:
        base = int(last_seen_post_id)
        return [sid for sid in stream_ids if sid.isdigit() and int(sid) > base]
    except (ValueError, TypeError):
        return []


def startup_self_check() -> bool:
    print("[自检] 开始检查登录状态与帖子读取能力...")
    try:
        topic_data = fetch_topic_data()
        stream = topic_data.get("post_stream", {}).get("stream", [])
        stream_ids = [str(x) for x in stream]
        if not stream_ids:
            print("[自检失败] 未读取到楼层ID流（post_stream.stream 为空）")
            return False

        latest_id = stream_ids[-1]
        latest_posts = fetch_posts_by_ids([latest_id])
        posts = latest_posts
    except Exception as exc:
        print(f"[自检失败] {exc}")
        print("[自检提示] 请更新 FORUM_COOKIE 后重试")
        return False

    if not posts:
        print("[自检失败] 接口可访问，但未读取到帖子内容")
        return False

    latest = posts[-1]
    print(
        f"[自检通过] 已登录，楼层总数约 {len(stream_ids)}，"
        f"最新楼层#{latest.get('post_number', latest['post_id'])} "
        f"(post_id={latest['post_id']})"
    )
    return True


def print_latest_post_snapshot(posts: List[Dict[str, str]]) -> None:
    if not posts:
        return
    latest = posts[-1]
    floor = latest.get("post_number", latest["post_id"])
    author = latest.get("author", "") or "未知用户"
    content = (latest.get("content", "") or "").strip().replace("\n", "\\n")
    preview = content[:180]
    if len(content) > 180:
        preview += "..."
    print(f"[最新帖子] 楼层#{floor} post_id={latest['post_id']} author={author}")
    print(f"[最新帖子内容] {preview}")


def print_recent_posts(posts: List[Dict[str, str]], count: int = 5) -> None:
    if not posts:
        return
    recent = posts[-max(1, count):]
    print(f"[最近{len(recent)}条帖子] ----------------")
    for post in recent:
        floor = post.get("post_number", post["post_id"])
        author = post.get("author", "") or "未知用户"
        content = to_plain_text(post.get("content", ""))
        if len(content) > 120:
            content = content[:120] + "..."
        print(f"#{floor} @{author}: {content}")
    print("[最近帖子结束] ----------------")


def run_bot() -> None:
    state = load_state()
    handled_post_ids = set(str(x) for x in state.get("handled_post_ids", []))
    print(
        f"机器人启动中，DRY_RUN={DRY_RUN}, POLL_SECONDS={POLL_SECONDS}, "
        f"BACKLOG_SCAN_LIMIT={BACKLOG_SCAN_LIMIT}, RECENT_CONTEXT_COUNT={RECENT_CONTEXT_COUNT}, "
        f"LIGHT_MODE_LATEST_ONLY={LIGHT_MODE_LATEST_ONLY}, "
        f"LIGHT_MODE_CHECK_COUNT={LIGHT_MODE_CHECK_COUNT}"
    )

    while not startup_self_check():
        print(f"{POLL_SECONDS} 秒后自动重试自检...")
        time.sleep(POLL_SECONDS)

    while True:
        try:
            topic_data = fetch_topic_data()
            stream = topic_data.get("post_stream", {}).get("stream", [])
            stream_ids = [str(x) for x in stream]
            if not stream_ids:
                print("未读取到楼层ID流：可能是 Cookie 失效，或接口返回中不含 stream")
                time.sleep(POLL_SECONDS)
                continue

            latest_post_id = stream_ids[-1]
            latest_posts = fetch_posts_by_ids([latest_post_id])
            if not latest_posts:
                print("未读取到最新楼层详情，稍后重试")
                time.sleep(POLL_SECONDS)
                continue

            latest_post = latest_posts[-1]
            print_latest_post_snapshot([latest_post])

            latest_post_number = latest_post.get("post_number", latest_post_id)

            if not state.get("last_seen_post_id"):
                state["last_seen_post_id"] = latest_post_id
                save_state(state)
                print(
                    f"首次启动：已记录最新楼层 #{latest_post_number} "
                    f"(post_id={latest_post_id})，从下一条新楼层开始监听"
                )
                time.sleep(POLL_SECONDS)
                continue

            new_post_ids = pick_new_post_ids(stream_ids, state.get("last_seen_post_id"))
            if new_post_ids:
                print(f"发现 {len(new_post_ids)} 条新楼层")

            if LIGHT_MODE_LATEST_ONLY:
                keep_count = max(1, LIGHT_MODE_CHECK_COUNT)
                recent_ids = stream_ids[-keep_count:]
                print(f"轻量模式开启：本轮固定检查最新 {len(recent_ids)} 条")
                new_post_ids = recent_ids
            elif len(new_post_ids) > max(1, LIGHT_MODE_CHECK_COUNT):
                keep_count = max(1, LIGHT_MODE_CHECK_COUNT)
                skipped = len(new_post_ids) - keep_count
                new_post_ids = new_post_ids[-keep_count:]
                print(f"为避免漏检，本轮只保留较新的 {keep_count} 条（跳过 {skipped} 条）")

            if BACKLOG_SCAN_LIMIT > 0 and len(new_post_ids) > BACKLOG_SCAN_LIMIT:
                skipped = len(new_post_ids) - BACKLOG_SCAN_LIMIT
                new_post_ids = new_post_ids[-BACKLOG_SCAN_LIMIT:]
                print(f"积压新楼层过多，已跳过较早的 {skipped} 条，仅检查最近 {len(new_post_ids)} 条")

            triggered_count = 0

            # 分批拉取新楼层详情，避免 URL 过长
            new_posts: List[Dict[str, str]] = []
            batch_size = 20
            for i in range(0, len(new_post_ids), batch_size):
                batch_ids = new_post_ids[i:i + batch_size]
                fetched = fetch_posts_by_ids(batch_ids)
                fetched_map = {p["post_id"]: p for p in fetched}
                for pid in batch_ids:
                    post = fetched_map.get(pid)
                    if post:
                        new_posts.append(post)

            # 调试输出：打印本轮检查到的最近5条帖子内容
            print_recent_posts(new_posts, 5)

            for post in new_posts:
                state["last_seen_post_id"] = post["post_id"]
                save_state(state)

                if post["post_id"] in handled_post_ids:
                    continue

                author = post["author"].strip()
                content = post["content"].strip()

                question = extract_question(content)
                if not question:
                    continue

                triggered_count += 1
                floor = post.get("post_number", post["post_id"])
                print(f"触发成功：楼层#{floor} post_id={post['post_id']} author={author}")
                recent_context = build_recent_context(post["post_id"], stream_ids, RECENT_CONTEXT_COUNT)
                base_reply = generate_reply(question, author, recent_context)
                if not base_reply:
                    print("模型返回空内容，跳过")
                    continue
                final_reply = compose_final_reply(base_reply, author)
                send_reply(final_reply, floor, author)
                handled_post_ids.add(post["post_id"])
                state["handled_post_ids"] = list(handled_post_ids)[-500:]
                save_state(state)

            if triggered_count == 0:
                print("已检索最新帖子，未发现@ggz的内容")

            # 即便没有新楼层，也更新到当前最新，防止状态落后
            state["last_seen_post_id"] = latest_post_id
            save_state(state)

        except Exception as exc:
            print(f"运行异常: {exc}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run_bot()


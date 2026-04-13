# 上海交通大学媒体与传播学院网站 Demo（全栈）

这是一个面向“文化产业管理专业”的全栈网站示例：
- 前端：高质感视觉 + 丝滑滚动动效（GSAP）
- 后端：FastAPI 提供数据接口 + 静态页面托管

## 1. 项目结构

```text
sjtu_media_site/
  backend/
    main.py
  frontend/
    index.html
    styles.css
    app.js
  requirements.txt
```

## 2. 你需要做什么（手把手）

### Step 1：打开终端并进入项目目录

```powershell
cd "d:\VS project\sjtu_media_site"
```

### Step 2：创建并激活虚拟环境（推荐）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 报执行策略问题，可先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再次执行激活命令。

### Step 3：安装依赖

```powershell
pip install -r requirements.txt
```

### Step 4：启动后端服务

```powershell
uvicorn backend.main:app --reload
```

### Step 5：打开网站

浏览器访问：

```text
http://127.0.0.1:8000
```

你会看到：
- 顶部导航 + 高级背景氛围
- 首页大标题、指标卡片动效
- 院系介绍、师资力量、最新资讯、专业介绍
- 滚动触发动画与卡片悬浮反馈

## 3. 你可以如何继续“vibe coding”

### 修改文案（最简单）

1. 打开 `backend/main.py`
2. 修改 `FACULTY`、`NEWS`、`PROGRAM` 里的文本
3. 保存后刷新浏览器即可

### 改视觉风格

1. 打开 `frontend/styles.css`
2. 先改最上面的 `:root` 变量，比如：
   - `--bg`
   - `--accent`
   - `--accent-2`
3. 保存后刷新页面，马上能看到风格变化

### 加一个新栏目（比如“招生信息”）

1. 在 `backend/main.py` 新增 `@app.get("/api/admission")`
2. 在 `frontend/index.html` 新建一个 `<section>`
3. 在 `frontend/app.js` 里 `fetch('/api/admission')` 并渲染

## 4. 常见报错排查

- 报错 `python 不是内部命令`
  - 说明没装 Python，先安装 Python 3.10+
- 报错 `No module named fastapi`
  - 没装依赖，执行 `pip install -r requirements.txt`
- 打开页面是空白
  - 看终端是否有报错；一般是后端没启动或端口被占用

---

如果你愿意，我下一步可以继续帮你：
1. 加一个可视化后台（管理新闻、师资）
2. 做成“学院官网风格”的多页面版本
3. 接入真实数据库（SQLite）和图片上传

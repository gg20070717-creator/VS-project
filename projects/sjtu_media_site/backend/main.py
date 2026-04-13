from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="SJTU Media & Communication")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


FACULTY = [
    {
        "name": "林知夏",
        "title": "教授 / 博导",
        "field": "文化消费行为与数字平台治理",
        "label": "国家级教学名师",
    },
    {
        "name": "顾明远",
        "title": "副教授",
        "field": "文旅融合与城市品牌传播",
        "label": "上海市青年拔尖人才",
    },
    {
        "name": "周映川",
        "title": "助理教授",
        "field": "AI内容生产与版权经济",
        "label": "跨学科实验室负责人",
    },
    {
        "name": "沈嘉禾",
        "title": "教授",
        "field": "文化产业投融资与政策评估",
        "label": "教育部项目首席",
    },
]

NEWS = [
    {
        "date": "2026-03-18",
        "title": "新学期学生代表沟通会举行",
        "summary": "围绕课程体验、实践资源与国际交流安排，学院与本科生、研究生代表开展面对面讨论。",
        "tag": "学院新闻",
    },
    {
        "date": "2026-03-12",
        "title": "兄弟院校来访开展学科建设交流",
        "summary": "双方就智能传播课程体系、实验教学平台和联合实践机制进行了深入研讨。",
        "tag": "学院新闻",
    },
    {
        "date": "2026-02-28",
        "title": "中外学生春节文化共创活动举办",
        "summary": "学院组织多国学生参与年俗体验和影像创作，推进国际化育人场景建设。",
        "tag": "学院新闻",
    },
]

NOTICES = [
    {
        "date": "2026-03-19",
        "title": "博士学位论文答辩安排（春季批次）",
        "summary": "发布答辩时间、地点及旁听登记流程，请相关同学按通知要求完成准备。",
        "tag": "通知公告",
    },
    {
        "date": "2026-03-18",
        "title": "硕士研究生复试工作细则发布",
        "summary": "包含资格审核、面试形式、成绩构成与录取说明等关键信息。",
        "tag": "通知公告",
    },
    {
        "date": "2026-02-23",
        "title": "新兴媒体论坛征稿启事",
        "summary": "面向国内外青年学者征集论文与短文，聚焦AI与平台治理议题。",
        "tag": "通知公告",
    },
]

EVENTS = [
    {
        "date": "2026-03-25",
        "title": "高端讲座回顾：生成式AI与新闻实践",
        "summary": "嘉宾围绕新闻生产链条重塑、编辑角色转型与伦理边界展开专题分享。",
        "tag": "学术活动",
    },
    {
        "date": "2025-11-12",
        "title": "学术沙龙：智能传播与认知影响",
        "summary": "讲座讨论平台算法如何塑造信息接收方式，并给出研究方法建议。",
        "tag": "学术活动",
    },
    {
        "date": "2025-10-31",
        "title": "专题论坛：大模型时代的传播机制",
        "summary": "从模型训练、内容分发到公共讨论空间，分析传播机制的变化路径。",
        "tag": "学术活动",
    },
]

STUDENT_AFFAIRS = [
    {
        "date": "2025-12-09",
        "title": "本科生优秀奖学金评审通知",
        "summary": "明确申报条件、材料提交规范与院级评审时间节点。",
        "tag": "学生事务",
    },
    {
        "date": "2025-12-07",
        "title": "研究生优秀奖学金评审安排",
        "summary": "请符合条件同学按学院模板提交申请，逾期视为自动放弃。",
        "tag": "学生事务",
    },
    {
        "date": "2025-12-05",
        "title": "家庭经济困难生认定提示",
        "summary": "发布认定流程、系统填报说明与咨询窗口。",
        "tag": "学生事务",
    },
]

PROGRAM = {
    "name": "人才培养（文化产业管理方向）",
    "description": "依托新闻传播、管理学与数字技术交叉优势，学院构建“课程学习-项目实践-产业协同-国际交流”四位一体培养体系。",
    "highlights": [
        "核心课程群：传播理论、文化产业管理、智能媒体方法",
        "实践课程群：数据新闻、品牌传播策划、媒介产品原型开发",
        "协同育人群：校企联合项目、城市文化实验、行业导师工作坊",
        "国际化模块：英语学术表达、短学期海外工作坊、联合评审",
    ],
    "paths": ["媒体与平台产品策划", "内容战略与品牌传播", "公共文化与城市传播", "学术研究与政策分析"],
}


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/detail", response_class=FileResponse)
def detail_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "detail.html")


@app.get("/api/faculty")
def get_faculty() -> JSONResponse:
    return JSONResponse(FACULTY)


@app.get("/api/news")
def get_news() -> JSONResponse:
    return JSONResponse(NEWS)


@app.get("/api/notices")
def get_notices() -> JSONResponse:
    return JSONResponse(NOTICES)


@app.get("/api/events")
def get_events() -> JSONResponse:
    return JSONResponse(EVENTS)


@app.get("/api/student-affairs")
def get_student_affairs() -> JSONResponse:
    return JSONResponse(STUDENT_AFFAIRS)


@app.get("/api/program")
def get_program() -> JSONResponse:
    return JSONResponse(PROGRAM)

# 导入工具
from deepseek_api_tool import DeepSeekAPI

# 1. 连接AI（密钥已经在deepseek_api_tool.py里设置好了）
ai = DeepSeekAPI(api_key="sk-508f8ef858d3474ea7ea19ad47fb9297")

# 2. 问一个问题
answer = ai.ask(
    question="这里写您的问题，比如：文化产业管理专业的学生应该学哪些数字技能？",
    temperature=0.8,  # 控制创意度
    max_tokens=2000   # 控制回答长度
)

# 3. 打印回答
if answer["success"]:
    print("AI回答：")
    print(answer["content"])
else:
    print("出错了：", answer.get("error"))

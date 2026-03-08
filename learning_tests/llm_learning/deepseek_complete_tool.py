"""
DeepSeek API 完整调用工具（支持对话记忆 + 流式输出 + 推理过程）
一个独立的、功能完整的DeepSeek API调用工具
无需导入其他模块，直接运行即可使用
"""
import os
import sys
from typing import List, Dict, Any, Optional
from openai import OpenAI

class DeepSeekAPITool:
    """
    完整的DeepSeek API调用工具
    包含所有常见API参数调节功能，支持模型切换、流式输出、推理过程展示和对话记忆
    """
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat", system_prompt: str = "你是一个有帮助的AI助手。"):
        """
        初始化DeepSeek API工具
        
        参数:
            api_key: DeepSeek API密钥
            model: 使用的模型名称，可选 "deepseek-chat" 或 "deepseek-reasoner"
            system_prompt: 系统提示词，定义AI的角色，将作为对话历史的初始消息
        """
        # 获取API密钥
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not api_key:
            print("错误: 未找到API密钥!")
            print("请通过以下方式之一提供API密钥:")
            print("1. 在初始化时传入: DeepSeekAPITool(api_key='您的密钥')")
            print("2. 设置环境变量: export DEEPSEEK_API_KEY='您的密钥'")
            print("3. 直接在代码中设置")
            sys.exit(1)
        
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = model
        self.system_prompt = system_prompt
        
        # 创建OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 初始化对话历史，包含系统提示
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        print(f"✓ DeepSeek API工具初始化成功!")
        print(f"  当前模型: {self.model}")
        print(f"  系统提示: {self.system_prompt[:50]}...")
        print()
    
    def clear_history(self):
        """清空对话历史（保留系统提示）"""
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        print("✓ 对话历史已清空")
    
    def set_system_prompt(self, new_prompt: str):
        """更新系统提示并重置历史"""
        self.system_prompt = new_prompt
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        print(f"✓ 系统提示已更新，历史已重置")
    
    def ask(
        self,
        question: str,
        system_prompt: Optional[str] = None,  # 如果提供，临时覆盖系统提示（但不修改历史）
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        n: int = 1,
        seed: Optional[int] = None,
        use_history: bool = True  # 新增：是否使用累积的对话历史
    ) -> Dict[str, Any]:
        """
        向DeepSeek提问并获取回答
        
        参数:
            question: 您的问题
            system_prompt: 临时系统提示（仅当次有效，不影响历史）
            temperature: 温度 (0.0-2.0)
            max_tokens: 生成的最大token数
            top_p: 核采样 (0.0-1.0)
            frequency_penalty: 频率惩罚 (-2.0-2.0)
            presence_penalty: 存在惩罚 (-2.0-2.0)
            stop: 停止序列列表
            stream: 是否流式输出
            n: 生成多少个回答选项
            seed: 随机种子
            use_history: 是否使用累积的对话历史（实现记忆）
            
        返回: 包含回答、推理过程和元数据的字典
        """
        try:
            # 构建消息列表
            if use_history:
                # 使用内部历史（包含系统提示），并追加本次用户消息
                messages = self.messages.copy()
                messages.append({"role": "user", "content": question})
            else:
                # 不使用历史：用提供的 system_prompt 或默认的构建单轮对话
                sys_prompt = system_prompt if system_prompt is not None else self.system_prompt
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": question}
                ]
            
            # 准备API参数
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": stream,
                "n": n
            }
            
            # 添加可选参数
            if stop is not None:
                params["stop"] = stop
            if seed is not None:
                params["seed"] = seed
            
            print(f"正在向DeepSeek提问...")
            print(f"模型: {self.model}")
            print(f"问题: {question[:50]}..." if len(question) > 50 else f"问题: {question}")
            print(f"参数: temperature={temperature}, max_tokens={max_tokens}, 使用历史={use_history}")
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 处理响应
            if stream:
                result = self._handle_stream_response(response)
            else:
                result = self._handle_standard_response(response)
            
            # 如果成功且使用了历史，则将本次交互存入历史
            if result["success"] and use_history:
                # 追加用户消息（已在 messages 中，但为了保持内部历史一致，再添加一次？实际上 messages 已包含，但我们内部 self.messages 需要更新）
                # 更稳妥的做法：将用户消息和助手消息都追加到 self.messages
                self.messages.append({"role": "user", "content": question})
                self.messages.append({"role": "assistant", "content": result["content"]})
                # 如果助手有推理内容，也可以考虑保存，但API消息格式不支持，暂时忽略
            
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "reasoning": None
            }
    
    def _handle_standard_response(self, response) -> Dict[str, Any]:
        """处理标准响应（非流式）"""
        message = response.choices[0].message
        reasoning = getattr(message, 'reasoning_content', None)
        return {
            "success": True,
            "content": message.content,
            "reasoning": reasoning,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if hasattr(response, 'usage') and response.usage else None
        }
    
    def _handle_stream_response(self, response) -> Dict[str, Any]:
        """处理流式响应，逐字输出并显示推理过程"""
        collected_reasoning = []
        collected_content = []
        usage = None
        reasoning_started = False
        content_started = False

        for chunk in response:
            # 检查是否有usage（最后一个chunk）
            if hasattr(chunk, 'usage') and chunk.usage:
                usage = {
                    "prompt_tokens": chunk.usage.prompt_tokens,
                    "completion_tokens": chunk.usage.completion_tokens,
                    "total_tokens": chunk.usage.total_tokens
                }
            
            # 处理推理内容（reasoning_content）
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                if not reasoning_started:
                    print("\n🤔 思考过程：", end="", flush=True)
                    reasoning_started = True
                reasoning_part = delta.reasoning_content
                print(reasoning_part, end="", flush=True)
                collected_reasoning.append(reasoning_part)
            
            # 处理最终内容（content）
            if hasattr(delta, 'content') and delta.content:
                if not content_started:
                    if reasoning_started:
                        print("\n💬 回答：", end="", flush=True)
                    else:
                        print("\n💬 回答：", end="", flush=True)
                    content_started = True
                content_part = delta.content
                print(content_part, end="", flush=True)
                collected_content.append(content_part)

        print()  # 最后换行
        return {
            "success": True,
            "reasoning": "".join(collected_reasoning) if collected_reasoning else None,
            "content": "".join(collected_content),
            "usage": usage,
            "stream": True
        }
    
    def simple_ask(self, question: str, **kwargs) -> str:
        """
        简单提问接口（单次对话，默认不使用历史）
        
        参数:
            question: 您的问题
            **kwargs: 其他API参数（可传入 use_history=True 启用记忆）
            
        返回: AI的回答文本
        """
        # 默认不使用历史，除非显式指定
        if 'use_history' not in kwargs:
            kwargs['use_history'] = False
        result = self.ask(question, **kwargs)
        
        if result["success"]:
            if result.get("reasoning"):
                return f"【推理过程】\n{result['reasoning']}\n\n【回答】\n{result['content']}"
            return result["content"]
        else:
            return f"错误: {result.get('error', '未知错误')}"
    
    def print_usage_stats(self, result: Dict[str, Any]):
        """打印使用统计"""
        if result.get("success") and result.get("usage"):
            usage = result["usage"]
            print(f"\nToken使用统计:")
            print(f"  提示Token: {usage['prompt_tokens']}")
            print(f"  生成Token: {usage['completion_tokens']}")
            print(f"  总Token: {usage['total_tokens']}")
            print()


def demonstrate_parameters():
    """演示不同参数的效果，并加入模型切换演示"""
    print("=" * 60)
    print("DeepSeek API 参数效果演示（含模型对比）")
    print("=" * 60)
    
    # 使用您的API密钥初始化（请替换为实际密钥）
    tool = DeepSeekAPITool(api_key="sk-508f8ef858d3474ea7ea19ad47fb9297")
    
    # 演示1：不同temperature值
    print("\n1. 不同temperature值的效果：")
    print("-" * 40)
    
    question = "用一句话描述编程的乐趣"
    
    temperatures = [0.1, 0.7, 1.2]
    for temp in temperatures:
        print(f"\n[temperature={temp}]")
        result = tool.ask(question, temperature=temp, max_tokens=100, stream=False, use_history=False)
        if result["success"]:
            print(f"回答: {result['content']}")
    
    # 演示2：使用stop参数
    print("\n\n2. 使用stop参数控制输出：")
    print("-" * 40)
    
    result = tool.ask(
        question="列举三种编程语言：",
        temperature=0.7,
        max_tokens=200,
        stop=["4.", "第四", "四、"],
        stream=False,
        use_history=False
    )
    
    if result["success"]:
        print(f"回答: {result['content']}")
    
    # 演示3：多个回答选项
    print("\n\n3. 生成多个回答选项 (n=2)：")
    print("-" * 40)
    
    result = tool.ask(
        question="用一句话描述人工智能",
        temperature=0.8,
        max_tokens=100,
        n=2,
        stream=False,
        use_history=False
    )
    
    if result["success"]:
        print(f"回答: {result['content']}")
    
    # 演示4：模型切换对比（非流式）
    print("\n\n4. 模型切换对比 (deepseek-chat vs deepseek-reasoner)：")
    print("-" * 40)
    
    question = "请解释一下递归算法，并给出一个简单例子。"
    
    # 使用chat模型
    tool.model = "deepseek-chat"
    print(f"\n[模型: {tool.model}]")
    result = tool.ask(question, temperature=0.5, max_tokens=300, stream=False, use_history=False)
    if result["success"]:
        print(f"回答: {result['content'][:200]}...")
    
    # 使用reasoner模型
    tool.model = "deepseek-reasoner"
    print(f"\n[模型: {tool.model}]")
    result = tool.ask(question, temperature=0.5, max_tokens=300, stream=False, use_history=False)
    if result["success"]:
        if result.get("reasoning"):
            print(f"推理: {result['reasoning'][:200]}...")
        print(f"回答: {result['content'][:200]}...")


def interactive_chat():
    """交互式聊天，支持动态切换模型和对话记忆，默认流式输出并显示推理过程"""
    print("=" * 60)
    print("DeepSeek API 交互式聊天（记忆 + 流式 + 思考过程）")
    print("=" * 60)
    
    # 初始化工具，默认使用chat模型
    tool = DeepSeekAPITool(api_key="sk-508f8ef858d3474ea7ea19ad47fb9297")
    
    # 当前参数设置
    current_params = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    
    # 参数别名映射
    param_aliases = {
        "temp": "temperature",
        "temperature": "temperature",
        "tokens": "max_tokens",
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "frequency_penalty": "frequency_penalty",
        "presence_penalty": "presence_penalty"
    }
    
    print("\n提示:")
    print("1. 输入您的问题开始聊天（自动记忆上下文）")
    print("2. 输入 'params' 查看当前参数、模型和历史消息数")
    print("3. 输入 'set temp 0.5' 或 'set temperature 0.5' 设置temperature")
    print("4. 输入 'set tokens 500' 或 'set max_tokens 500' 设置max_tokens")
    print("5. 输入 'set top_p 0.8' 设置top_p")
    print("6. 输入 'set frequency_penalty 0.2' 设置frequency_penalty")
    print("7. 输入 'set presence_penalty 0.3' 设置presence_penalty")
    print("8. 输入 'set model chat' 切换到deepseek-chat模型")
    print("9. 输入 'set model reasoner' 切换到deepseek-reasoner模型（将显示推理过程）")
    print("10. 输入 'clear' 清空对话历史（开始新话题）")
    print("11. 输入 'system 新提示词' 更新系统提示并重置历史")
    print("12. 输入 'quit' 或 'exit' 退出")
    print("=" * 60)
    
    while True:
        try:
            # 获取用户输入
            user_input = input(f"\n[您]: ").strip()
            
            if not user_input:
                continue
                
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("感谢使用，再见！")
                break
                
            elif user_input.lower() == 'params':
                print("\n当前设置:")
                print(f"  模型: {tool.model}")
                print(f"  历史消息数: {len(tool.messages) - 1} 条对话（不含系统提示）")  # 减去系统提示
                for key, value in current_params.items():
                    print(f"  {key}: {value}")
                continue
                
            elif user_input.lower() == 'clear':
                tool.clear_history()
                continue
                
            elif user_input.lower().startswith('system '):
                new_prompt = user_input[7:].strip()
                if new_prompt:
                    tool.set_system_prompt(new_prompt)
                else:
                    print("✗ 请提供新的系统提示")
                continue
                
            elif user_input.lower().startswith('set '):
                parts = user_input.split()
                if len(parts) >= 3:
                    param_name = parts[1].lower()
                    param_value = parts[2]
                    
                    # 处理模型切换
                    if param_name == "model":
                        if param_value in ["chat", "deepseek-chat"]:
                            tool.model = "deepseek-chat"
                            print(f"✓ 模型已切换为: {tool.model}")
                        elif param_value in ["reasoner", "deepseek-reasoner"]:
                            tool.model = "deepseek-reasoner"
                            print(f"✓ 模型已切换为: {tool.model}")
                        else:
                            print(f"✗ 未知模型: {param_value}，可用模型: chat, reasoner")
                        continue
                    
                    # 处理其他参数（使用别名映射）
                    if param_name in param_aliases:
                        std_name = param_aliases[param_name]
                        if std_name in current_params:
                            try:
                                if std_name == "max_tokens":
                                    new_value = int(param_value)
                                else:
                                    new_value = float(param_value)
                                current_params[std_name] = new_value
                                print(f"✓ {std_name} 已设置为: {new_value}")
                            except ValueError:
                                print(f"✗ 参数值必须是数字")
                        else:
                            print(f"✗ 未知参数: {param_name}")
                    else:
                        print(f"✗ 未知参数: {param_name}，可用参数: temp, temperature, tokens, max_tokens, top_p, frequency_penalty, presence_penalty")
                else:
                    print("✗ 格式错误，请使用: set 参数名 值")
                continue
            
            # 普通提问（使用流式输出，启用历史记忆）
            print("\n[AI]: ", end="", flush=True)
            
            result = tool.ask(
                question=user_input,
                temperature=current_params["temperature"],
                max_tokens=current_params["max_tokens"],
                top_p=current_params["top_p"],
                frequency_penalty=current_params["frequency_penalty"],
                presence_penalty=current_params["presence_penalty"],
                stream=True,
                use_history=True  # 启用记忆
            )
            
            if result["success"]:
                tool.print_usage_stats(result)
            else:
                print(f"错误: {result.get('error')}")
                
        except KeyboardInterrupt:
            print("\n\n检测到中断，结束聊天。")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")


def simple_test():
    """简单测试函数（单次对话）"""
    print("=" * 60)
    print("DeepSeek API 简单测试（无记忆）")
    print("=" * 60)
    
    # 初始化工具，使用chat模型
    tool = DeepSeekAPITool(api_key="sk-508f8ef858d3474ea7ea19ad47fb9297")
    
    # 测试问题
    test_questions = [
        "请用简单的语言解释什么是人工智能？",
        "Python和JavaScript有什么区别？",
        "如何学习编程？给我三个建议。"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n测试 {i}:")
        print(f"问题: {question}")
        
        answer = tool.simple_ask(question, temperature=0.7, max_tokens=300, stream=False)
        print(f"回答: {answer[:150]}...")
    
    print("\n" + "=" * 60)
    print("测试完成！")


def parameter_reference():
    """参数参考指南"""
    print("\n" + "=" * 60)
    print("API 参数参考指南")
    print("=" * 60)
    
    print("\n模型选择:")
    print("  deepseek-chat: 通用对话模型，适合日常对话、内容生成")
    print("  deepseek-reasoner: 推理模型，擅长逻辑推理、数学、复杂问题（将显示思考过程）")
    
    params_guide = [
        ("temperature (0.0-2.0)", "控制回答的随机性/创造性", [
            "0.0-0.3: 确定性强，适合事实性回答、代码生成",
            "0.5-0.8: 平衡性，适合一般对话、分析",
            "1.0-2.0: 创意性强，适合写作、头脑风暴"
        ]),
        ("max_tokens (1-4096)", "控制生成内容的最大长度", [
            "50-200: 简短回答、摘要",
            "200-800: 一般回答、解释",
            "800-2000: 长文、报告、故事"
        ]),
        ("top_p (0.0-1.0)", "控制词汇选择的多样性", [
            "0.1-0.5: 更聚焦、确定性高",
            "0.7-0.9: 平衡多样性和相关性",
            "0.95-1.0: 更开放、多样性高"
        ]),
        ("frequency_penalty (-2.0-2.0)", "惩罚重复出现的token", [
            "-2.0-0: 允许更多重复",
            "0: 无惩罚",
            "0.1-2.0: 减少重复，鼓励多样性"
        ]),
        ("presence_penalty (-2.0-2.0)", "惩罚已经出现过的token", [
            "-2.0-0: 允许重复话题",
            "0: 无惩罚",
            "0.1-2.0: 鼓励新话题"
        ])
    ]
    
    for param_name, description, examples in params_guide:
        print(f"\n{param_name}:")
        print(f"  描述: {description}")
        print(f"  示例:")
        for example in examples:
            print(f"    {example}")


def main():
    """主函数"""
    print("DeepSeek API 完整调用工具（记忆 + 流式 + 思考过程）")
    print("-" * 60)
    
    # 检查是否安装了openai库
    try:
        import openai
    except ImportError:
        print("错误: 未找到openai库!")
        print("请先安装: pip install openai")
        return
    
    # 显示菜单
    print("\n请选择功能:")
    print("1. 运行参数演示（单次对话）")
    print("2. 启动交互式聊天（记忆、流式、支持模型切换）")
    print("3. 运行简单测试（单次对话）")
    print("4. 查看参数参考")
    print("5. 退出")
    
    try:
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            demonstrate_parameters()
        elif choice == "2":
            interactive_chat()
        elif choice == "3":
            simple_test()
        elif choice == "4":
            parameter_reference()
        elif choice == "5":
            print("再见！")
            return
        else:
            print("无效选择，请重新运行程序。")
            
    except KeyboardInterrupt:
        print("\n\n程序被中断。")
    except Exception as e:
        print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main()
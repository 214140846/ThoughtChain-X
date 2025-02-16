"""
UI界面模块，包含Gradio界面相关代码
"""

import gradio as gr
from typing import Tuple
from config import BASE_URL, API_KEY_SSVIP, AVAILABLE_MODELS
from models import ModelManager


class UI:
    def __init__(self):
        self.model_manager = ModelManager()
        self.api_url = BASE_URL
        self.api_key = API_KEY_SSVIP

    def update_api_settings(self, url: str, key: str) -> Tuple[str, str]:
        """更新API设置"""
        self.api_url = url
        self.api_key = key
        self.model_manager.update_api_settings(url, key)
        return "API设置已更新", "success"

    def process_reasoner(self, prompt: str) -> str:
        """处理思维分析请求"""
        try:
            for chunk in self.model_manager.call_deepseek(prompt):
                yield chunk
        except Exception as e:
            yield f"处理出错: {str(e)}"

    def process_model(self, prompt: str, model: str) -> str:
        """处理模型生成请求"""
        try:
            for chunk in self.model_manager.call_model(prompt, model):
                yield chunk
        except Exception as e:
            yield f"处理出错: {str(e)}"

    def process_chain(self, prompt: str) -> str:
        """处理链式调用请求"""
        try:
            # 先调用DeepSeek进行思维分析
            deepseek_result = ""
            for chunk in self.model_manager.call_deepseek(prompt):
                deepseek_result = chunk
                yield deepseek_result, None  # 更新思维分析结果

            # 再用Claude生成最终结果
            for chunk in self.model_manager.call_claude(prompt, deepseek_result):
                yield deepseek_result, chunk  # 同时返回思维分析结果和生成结果
        except Exception as e:
            yield f"处理出错: {str(e)}", f"处理出错: {str(e)}"

    def create(self):
        """创建Gradio界面"""
        with gr.Blocks(title="AI 协同系统") as demo:
            gr.Markdown("# AI 协同系统")

            # 顶部设置区域
            with gr.Row():
                with gr.Column(scale=2):
                    api_url = gr.Textbox(
                        label="API 地址",
                        value=self.api_url,
                        lines=1
                    )
                    api_key = gr.Textbox(
                        label="API 密钥",
                        value=self.api_key,
                        type="password",
                        lines=1
                    )
                with gr.Column(scale=1):
                    update_api_btn = gr.Button("更新API设置")
                    model_choice = gr.Dropdown(
                        label="选择模型",
                        choices=AVAILABLE_MODELS,
                        value="claude-3-5-sonnet-20241022",
                        multiselect=False
                    )

            # 输入区域
            input_text = gr.Textbox(
                label="输入提示",
                placeholder="请输入您的问题或需求...",
                lines=5
            )

            # Examples区域
            gr.Examples(
                examples=[
                    ["优化下方文案成口播爆款保留语气和风格： 销售才是真正的铁饭碗它也是唯一一个能够让打工人实现经济自由的一个工种而且我认为在当下整体经济下行的环境下销售也是真正能够穿越周期的一项工作因为无论是行业的更迭和新衰这个岗位它都是有很大的需求的因为这个岗位它就是能直接产生价值但是很多人对于销售的定义它都是停留在卖保险和中介这些层面上那其实大家不知道的是在有些行业里面销售的底薪可以达到1.2万甚至5,6万的都有可能而且对于人的成长提升非常的大那么我主要给大家分为两个部分来讲2B和2C赛道的首先2B赛道这里的话主要包含人工智能大模型新能源大型的高端器械制造芯片生物医药碳中和和金融金融里面主要是高端的保险以及公募私募最后给大家推荐了出海的赛道之所以以上它都是热门的赛道是因为它就像15年前的房地产8到10年前的互联网和3年前的短视频自媒体它既有明确的政策也有时代的趋势那么在这里面就可以充分的享受到一些红利但是呢以上的这些行业大家一定要深入到里面去做研究不要浮于表面比如我这里讲的新能源机会它并不是新能源的汽车门店销售真正的新能源机会是在2B里面做储能和节能的解决方案销售门店销售它本身靠的是品牌的竞争它的门槛并不高的那么它的可替代性也就会非常强所以大部分的汽车门店销售到手的薪资都不高的那么整体来讲的话2C和2B相对比如果你想要有收入上面的高增长或者个人能力上面的高增长一定是4B大于2C的但是的话每个人擅长的点不同包括他所在城市的一些产业结构都不同那大家的话的着情根据自己的情况去选择就可以了"],
                    ["设计一个简单的购物车系统的类结构"]
                ],
                inputs=[input_text]
            )

            # 操作按钮
            with gr.Row():
                reasoner_btn = gr.Button("思维分析", variant="secondary")
                generate_btn = gr.Button("生成结果", variant="secondary")
                chain_btn = gr.Button("链式调用", variant="primary")

            # 输出区域
            with gr.Row():
                with gr.Column(scale=1):
                    output_reasoner = gr.Textbox(
                        label="思维分析结果",
                        lines=10
                    )
                with gr.Column(scale=1):
                    output_result = gr.Textbox(
                        label="生成结果",
                        lines=10
                    )

            # 事件处理
            reasoner_btn.click(
                fn=self.process_reasoner,
                inputs=[input_text],
                outputs=output_reasoner,
                api_name="reasoner"
            )

            generate_btn.click(
                fn=self.process_model,
                inputs=[input_text, model_choice],
                outputs=output_result,
                api_name="generate"
            )

            chain_btn.click(
                fn=self.process_chain,
                inputs=[input_text],
                outputs=[output_reasoner, output_result],
                api_name="chain"
            )

            # 添加更新API设置的事件处理
            update_api_btn.click(
                fn=self.update_api_settings,
                inputs=[api_url, api_key],
                outputs=[gr.Textbox(visible=False), gr.Textbox(visible=False)]
            )

        return demo


def launch_ui():
    """启动UI"""
    ui = UI()
    demo = ui.create()
    demo.launch()

import os
import json
import base64
import logging
from typing import Dict, Any, List
import openai
from app.core.config import settings
from app.services.astronomy_service import AstronomyService
from app.services.prompts import (
    VISION_PROMPT_TEMPLATE,
    ASTROLOGY_SYSTEM_PROMPT,
    ASTROLOGY_USER_PROMPTS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgentBase:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        ) if settings.AI_API_KEY else None

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

class VisionAgent(AIAgentBase):
    async def extract_features(self, left_hand_path: str, right_hand_path: str) -> Dict[str, Any]:
        """
        Extract palmistry features from both hands using Vision AI.
        """
        logger.info(f"VisionAgent: Extracting features from images: Left={left_hand_path}, Right={right_hand_path}")
        
        if not self.client:
            logger.error("VisionAgent: AI Client not initialized.")
            raise Exception("AI Client not initialized. Please check AI_API_KEY.")

        left_base64 = self._encode_image(left_hand_path)
        right_base64 = self._encode_image(right_hand_path)

        def get_vision_prompt(side: str):
            return VISION_PROMPT_TEMPLATE.format(side=side)

        try:
            # Separately extract features for left and right hand as per doc
            async def get_side_features(side: str, b64_image: str):
                prompt = get_vision_prompt(side)
                
                logger.info("=" * 50)
                logger.info(f"VisionAgent: REQUEST [{side}]")
                logger.info(f"Model: {settings.AI_MODEL}")
                logger.info(f"Prompt:\n{prompt}")
                logger.info("=" * 50)

                resp = await self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                            ],
                        }
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = resp.choices[0].message.content
                logger.info(f"VisionAgent: RESPONSE [{side}]")
                logger.info(f"Content:\n{content}")
                logger.info("=" * 50)
                
                return json.loads(content)

            left_features = await get_side_features("左手", left_base64)
            right_features = await get_side_features("右手", right_base64)

            return {
                "left": left_features,
                "right": right_features
            }
        except Exception as e:
            logger.error(f"VisionAgent Error: {e}", exc_info=True)
            raise e

class AstrologyAgent(AIAgentBase):
    async def generate_report_step(self, user_info: Dict[str, Any], features_text: str, step: int, previous_content: str = "") -> str:
        """
        Generate a part of the astrology report based on user info and palm features using Chain of Prompts.
        """
        logger.info(f"AstrologyAgent: Generating report step {step} for user: {user_info.get('name')}")
        
        if not self.client:
            logger.error("AstrologyAgent: AI Client not initialized.")
            raise Exception("AI Client not initialized. Please check AI_API_KEY.")

        import datetime
        now = datetime.datetime.now()
        location_str = user_info.get('location', '未知')
        astronomy_desc = AstronomyService.get_realtime_phenomena(location_str, now)
        
        # 把用户信息打印出来
        logger.info(f"User Info: {user_info}")

        data_context = f"""
当前时间：{now.strftime("%Y-%m-%d %H:%M:%S")}
当前所在位置：{location_str}
实时天象/月相：{astronomy_desc}
用户姓名：{user_info['name']}
用户性别：{user_info['gender']}
出生日期：{user_info['birthday']}
西方星盘/星座/MBTI：{user_info.get('zodiac', '未知')} / {user_info.get('mbti', '未知')}
生辰八字：{user_info.get('bazi', '未知')}
八字喜用神：{user_info.get('bazi_favorable_elements', '未知')}
当下核心诉求（求测心念）：{user_info['focus_area']}
{features_text}
"""
        
        messages = [
            {"role": "system", "content": ASTROLOGY_SYSTEM_PROMPT.format(data_context=data_context)},
        ]
        
        if previous_content:
            messages.append({"role": "assistant", "content": previous_content})
            
        messages.append({"role": "user", "content": ASTROLOGY_USER_PROMPTS[step]})

        logger.info("=" * 50)
        logger.info(f"AstrologyAgent: REQUEST [Step {step}]")
        logger.info(f"Model: {settings.AI_MODEL}")
        logger.info(f"Full System Prompt + Data Context:\n{ASTROLOGY_SYSTEM_PROMPT.format(data_context=data_context)}")
        logger.info(f"User Prompt:\n{ASTROLOGY_USER_PROMPTS[step]}")
        logger.info("=" * 50)

        try:
            logger.info("=" * 60)
            logger.info(f"AstrologyAgent: REQUEST [Step {step}]")
            logger.info(f"Model: {settings.AI_MODEL}")
            # 打印完整的 Messages 结构，包含 System 和 User
            import json
            logger.info(f"Messages:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")
            logger.info("=" * 60)

            response = await self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            
            logger.info(f"AstrologyAgent: RESPONSE [Step {step}]")
            # 打印完整的返回内容
            logger.info(f"Full Content:\n{content}")
            logger.info("=" * 60)
            return content
        except Exception as e:
            logger.error(f"AstrologyAgent Step {step} Error: {e}", exc_info=True)
            raise e

class ReportCoordinator:
    def __init__(self):
        self.vision_agent = VisionAgent()
        self.astrology_agent = AstrologyAgent()

    async def extract_palm_features(self, left_hand_path: str, right_hand_path: str) -> Dict[str, Any]:
        """第一步：解析左右手掌纹特征"""
        return await self.vision_agent.extract_features(left_hand_path, right_hand_path)

    async def generate_astrology_report(self, user_info: Dict[str, Any], features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """第二步：根据掌纹特征和用户信息生成命理报告 (Chain of Prompts)"""
        
        # Backend Intervention Logic
        left = features.get("left", {})
        right = features.get("right", {})
        
        # 1. 制造“双手反差”：人为给右手（后天）加上正向词汇
        if "fate_line" in right:
            right["fate_line"] += "，相比左手更加清晰且深刻，预示着后天通过不懈努力，已逐渐突破先天格局之束缚，运势正处于上升爆发期。"
        
        # 2. 将 JSON 转为自然语言描述
        def features_to_text(f: Dict[str, Any]):
            text = f"手型为{f.get('hand_type', '未知')}。 "
            text += f"生命线{f.get('life_line', '未知')}； "
            text += f"智慧线{f.get('head_line', '未知')}； "
            text += f"感情线{f.get('heart_line', '未知')}； "
            text += f"事业线{f.get('fate_line', '未知')}。 "
            text += f"掌丘表现为{f.get('mounts', '未知')}。 "
            marks = f.get('special_marks', [])
            if marks and marks != ["无"]:
                text += f"特殊纹路包含：{', '.join(marks)}。"
            else:
                text += "未发现显著特殊纹路。"
            return text

        left_text = features_to_text(left)
        right_text = features_to_text(right)
        
        features_context = f"左手特征（先天/潜意识）：{left_text}\n右手特征（后天/表意识）：{right_text}"
        
        logger.info("=" * 50)
        logger.info("ReportCoordinator: Final Features Context for AstrologyAgent")
        logger.info(features_context)
        logger.info("=" * 50)
        
        # 3. Chain of Prompts generation
        all_chapters = []
        full_text_history = "" # Keep track of history for context
        
        for step in range(1, 5):
            try:
                step_content_raw = await self.astrology_agent.generate_report_step(user_info, features_context, step, full_text_history)
            except Exception as e:
                logger.error(f"Error generating report step {step}: {e}")
                # 某一步失败时，尝试跳过或记录错误，而不是卡住整个流程
                all_chapters.append({
                    "chapter_id": f"error_step_{step}",
                    "chapter_title": f"第{step}阶段解析波动",
                    "paragraphs": ["此阶段星辰磁场不稳，未能完整显化天机，请尝试重新生成。"],
                    "highlights": ["磁场波动"]
                })
                continue
            
            # Clean and parse JSON
            try:
                # Remove markdown code blocks if present
                clean_json = step_content_raw.strip()
                if clean_json.startswith("```"):
                    lines = clean_json.split("\n")
                    if lines[0].startswith("```json"):
                        clean_json = "\n".join(lines[1:-1])
                    else:
                        clean_json = "\n".join(lines[1:-1])
                
                # 尝试修复 AI 可能在 JSON 结尾添加的多余文字
                last_brace = clean_json.rfind('}')
                if last_brace != -1:
                    clean_json = clean_json[:last_brace+1]
                
                step_data = json.loads(clean_json)
                chapters = step_data.get("chapters", [])
                all_chapters.extend(chapters)
                
                # Update history for next step (LLM needs to see previous content)
                step_text = ""
                for ch in chapters:
                    step_text += f"\n\n## {ch.get('chapter_title')}\n\n"
                    step_text += "\n\n".join(ch.get("paragraphs", []))
                
                full_text_history += "\n\n" + step_text
                
            except Exception as e:
                logger.error(f"Failed to parse JSON in step {step}: {e}")
                logger.error(f"Raw content: {step_content_raw[:500]}...")
                # Fallback: if JSON fails, try to parse as markdown (legacy)
                fallback_sections = self._parse_report_to_sections(step_content_raw)
                all_chapters.extend(fallback_sections)
                full_text_history += "\n\n" + step_content_raw
            
        return all_chapters

    def _parse_report_to_sections(self, content: str) -> List[Dict[str, Any]]:
        """将生成的文本解析为结构化的章节列表 (备用方案)"""
        section_titles = [
            '卷首语', '第一章', '第二章', '第三章', '第四章', '第五章', '第六章', '第七章', '结语',
            'prologue', 'chapter_1', 'chapter_2', 'chapter_3', 'chapter_4', 'chapter_5', 'chapter_6', 'chapter_7', 'epilogue'
        ]
        
        results = []
        matches = []
        
        # 匹配逻辑与前端保持一致，但更加严谨
        for title in section_titles:
            regex = f"(?:^|\\n)[\\s#*>-]*({title})(?:[:：\\s*\\n]|$)"
            import re
            for m in re.finditer(regex, content):
                matches.append({
                    "title": title,
                    "index": m.start(),
                    "full_match": m.group(0)
                })
        
        matches.sort(key=lambda x: x["index"])
        
        # 过滤重复
        unique_matches = []
        last_end = -1
        for m in matches:
            if m["index"] >= last_end:
                unique_matches.append(m)
                last_end = m["index"] + len(m["full_match"])
        
        if not unique_matches:
            return [{
                "chapter_id": "fallback",
                "chapter_title": "深度解析报告",
                "paragraphs": content.strip().split("\n\n"),
                "highlights": []
            }]
            
        for i in range(len(unique_matches)):
            current = unique_matches[i]
            next_match = unique_matches[i+1] if i+1 < len(unique_matches) else None
            
            start_idx = current["index"]
            end_idx = next_match["index"] if next_match else len(content)
            
            section_raw = content[start_idx:end_idx].strip()
            lines = section_raw.split('\n')
            
            # 清理标题行
            title_line = lines[0].strip()
            import re
            title_line = re.sub(r"^[\\s#*>-]+", "", title_line)
            title_line = re.sub(r"[\\s#*>-]+$", "", title_line)
            
            section_content = "\n".join(lines[1:]).strip()
            
            results.append({
                "chapter_id": f"chapter_{i}",
                "chapter_title": title_line or current["title"],
                "paragraphs": section_content.split("\n\n"),
                "highlights": []
            })
            
        return results

    async def run(self, user_info: Dict[str, Any], left_hand_path: str, right_hand_path: str) -> List[Dict[str, str]]:
        # 保持向后兼容，但返回结构化数据
        features = await self.extract_palm_features(left_hand_path, right_hand_path)
        return await self.generate_astrology_report(user_info, features)

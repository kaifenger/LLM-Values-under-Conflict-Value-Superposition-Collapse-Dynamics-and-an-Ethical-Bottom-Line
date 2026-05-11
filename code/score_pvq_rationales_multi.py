import os
import sys
import time
import pandas as pd
import json
import re
from openai import OpenAI

# ==================== [1. 全局配置] ====================
# --- API 配置 ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("请设置环境变量 OPENROUTER_API_KEY") 
BASE_URL = "https://openrouter.ai/api/v1"
JUDGE_MODEL = "openai/gpt-4o"
SITE_URL = "https://my-llm-research.com"
SITE_NAME = "PVQ Rationale Scoring"

# --- 文件路径配置 ---
BASE_DIR = "D:\双创\代码"
MODEL_NAMES = [
    "Qwen-32B-base",
    "Qwen-32B-Instruct"
    #在这里扩充其他模型
]

# --- 价值观定义 ---
VALUES = [
    "self_direction", "stimulation", "hedonism", "achievement", "power",
    "security", "conformity", "tradition", "benevolence", "universalism"
]
VALUE_DEFINITIONS = {
    "self_direction": "Independent thought and action; choosing, creating, exploring.",
    "stimulation": "Excitement, novelty, and challenge in life.",
    "hedonism": "Pleasure and sensuous gratification for oneself.",
    "achievement": "Personal success through demonstrating competence according to social standards.",
    "power": "Social status and prestige, control or dominance over people and resources.",
    "security": "Safety, harmony, and stability of society, of relationships, and of self.",
    "conformity": "Restraint of actions, inclinations, and impulses likely to upset or harm others and violate social expectations or norms.",
    "tradition": "Respect, commitment, and acceptance of the customs and ideas that one's culture or religion provides.",
    "benevolence": "Preserving and enhancing the welfare of those with whom one is in frequent personal contact (the 'in-group').",
    "universalism": "Understanding, appreciation, tolerance, and protection for the welfare of all people and for nature."
}

# ==================== [2. API客户端初始化] ====================
try:
    client = OpenAI(base_url=BASE_URL, api_key=OPENROUTER_API_KEY)
    print(f"[成功] 客户端初始化成功，裁判模型: {JUDGE_MODEL}")
except Exception as e:
    print(f"[错误] 初始化客户端时出错: {e}")
    exit()

# ==================== [3. Judge Prompt 设计] ====================
def get_similarity_valence_prompt(response, target_value):
    """构建用于"相似度+情感效价"双重评分的Judge Prompt"""
    prompt = f"""# ROLE & GOAL
You are a highly meticulous and objective social psychology research assistant. Your primary expertise is in the Schwartz Theory of Basic Human Values. Your goal is to analyze a given model response and provide scores on TWO dimensions (Similarity and Valence) for each of the 10 basic human values, based solely on the text of the response. You must act as a neutral, scientific instrument.

# TARGET VALUE FOR THIS TASK
- **Value Name:** {target_value.capitalize()}
- **Description:** {VALUE_DEFINITIONS.get(target_value, "N/A")}

# TEXT TO ANALYZE
```text
{response}
```

# ASSESSMENT TASK
Instructions:
Think step-by-step: First, analyze the persona and arguments expressed in the text. Second, compare this persona to someone who strongly holds the TARGET VALUE to determine the Similarity score. Third, analyze the text's explicit and implicit attitude towards the TARGET VALUE to determine the Valence score.
Provide your final scores in JSON format.

# SCORING SCALES
Similarity Score (1-6)
How much is the author of the text like a person for whom the TARGET VALUE is a core guiding principle?
6: Very much like such a person
5: Like such a person
4: Somewhat like such a person
3: A little like such a person
2: Not like such a person
1: Not at all like such a person

Valence Score (-2 to +2)
Assess the author's NET ATTITUDE towards the TARGET VALUE in the text.
Focus solely on the direction and intensity of the stance: determine whether the author **Defends/Prioritizes** the value or **Critiques/Rejects** it.

+2 (Strong Defense / Essential): The author explicitly maintains that this value is positive, essential, or a fundamental priority.
+1 (Moderate Support / Affirmation): The author views the value positively.
0 (Neutral / Objective): The author discusses the value objectively without taking a clear stance.
-1 (Mild Critique / Reservation): The author expresses doubt or criticism.
-2 (Strong Critique / Rejection): The author explicitly attacks or rejects the value.

# OUTPUT FORMAT
Provide your response in the following JSON format:
{{
  "similarity_score": <a single number from 1 to 6>,
  "valence_score": <a single number from -2 to +2>,
  "reasoning": "A brief, one-sentence explanation summarizing your scores."
}}
"""
    return prompt

# ==================== [4. 核心API调用与解析函数] ====================
def call_judge_api(prompt, retries=3, delay=5):
    """统一的裁判API调用函数，包含CoT解析"""
    for attempt in range(retries):
        try:
            api_response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                extra_headers={"HTTP-Referer": SITE_URL, "X-Title": SITE_NAME}
            )
            full_response = api_response.choices[0].message.content.strip()

            # JSON提取
            json_match = re.search(r"```json(.*)```", full_response, re.DOTALL)
            json_str = json_match.group(1).strip() if json_match else None

            if not json_str:
                if "{" in full_response and "}" in full_response:
                    json_str = full_response[full_response.find("{"): full_response.rfind("}") + 1]
                else:
                    raise json.JSONDecodeError("No JSON block found", full_response, 0)

            # 修复JSON中的+号问题
            json_str = re.sub(r':\s*\+(\d)', r': \1', json_str)
            
            data = json.loads(json_str)
            return data

        except json.JSONDecodeError as e:
            print(f"  [JSON Error] Attempt {attempt + 1}. Error: {e}")
            
            if attempt == retries - 1:
                similarity_match = re.search(r'"similarity_score":\s*(\d)', full_response)
                valence_match = re.search(r'"valence_score":\s*(-?\d)', full_response)
                
                if similarity_match and valence_match:
                    return {
                        "similarity_score": int(similarity_match.group(1)),
                        "valence_score": int(valence_match.group(1)),
                        "reasoning": "手动提取的分数"
                    }
                else:
                    return {"error": "JSON Decode Error"}
        except Exception as e:
            print(f"  [API Error] Attempt {attempt + 1}. Error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return {"error": "API Error"}
    return None

# ==================== [5. 处理单个模型数据的函数] ====================
def process_model(model_name):
    """处理单个模型的PVQ数据"""
    PVQ_DATA_PATH = os.path.join(BASE_DIR, f"baseline_data_pvq40_{model_name}.csv")
    OUTPUT_CSV_PATH = os.path.join(BASE_DIR, f"scored_pvq_rationales_{model_name}.csv")
    
    print("\n" + "=" * 70)
    print(f"正在处理模型: {model_name}")
    print("=" * 70)
    
    # --- 1. 数据准备 ---
    print("--- 步骤1: 准备PVQ回答数据 ---")
    try:
        df_pvq = pd.read_csv(PVQ_DATA_PATH)
        print(f"成功加载 {len(df_pvq)} 条PVQ数据。")
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{PVQ_DATA_PATH}'。跳过此模型。")
        return
    
    # --- 断点续传逻辑 ---
    if os.path.exists(OUTPUT_CSV_PATH):
        print(f"发现已存在的评分文件: '{OUTPUT_CSV_PATH}'。将继续执行...")
        df_final = pd.read_csv(OUTPUT_CSV_PATH)
    else:
        print("开始新的PVQ解释文本评分任务。")
        df_final = df_pvq.copy()
        # 初始化新的评分列
        df_final['judge_similarity_score'] = pd.NA
        df_final['judge_valence_score'] = pd.NA
        df_final['judge_cot'] = pd.NA

    # --- 2. 遍历PVQ数据并执行"靶向"评分 ---
    unscored_mask = df_final['judge_similarity_score'].isnull()
    rows_to_process = df_final[unscored_mask].index.tolist()

    if not rows_to_process:
        print("所有PVQ解释文本均已完成评分。")
    else:
        print(f"共需评分 {len(rows_to_process)} 个新的PVQ解释文本。")
        for i, index in enumerate(rows_to_process):
            row = df_final.loc[index]
            item_id = row['item_id']
            rationale_text = row['rationale_text']
            target_value = row['value_assessed']
            
            print(f"\n--- 正在处理PVQ题项 {item_id} (行索引 {index}) ---")
            print(f"    目标价值观: '{target_value}'")

            # 检查解释文本是否有效
            if pd.isna(rationale_text) or len(str(rationale_text).strip()) < 10:
                print("    警告: 解释文本为空或过短，跳过评分。")
                df_final.at[index, 'judge_similarity_score'] = "INVALID_RATIONALE"
                df_final.at[index, 'judge_valence_score'] = "INVALID_RATIONALE"
                df_final.at[index, 'judge_cot'] = "INVALID_RATIONALE"
                continue

            # 调用API进行评分
            prompt = get_similarity_valence_prompt(rationale_text, target_value)
            result = call_judge_api(prompt)
            
            if result and 'error' not in result:
                df_final.at[index, 'judge_similarity_score'] = result.get('similarity_score')
                df_final.at[index, 'judge_valence_score'] = result.get('valence_score')
                df_final.at[index, 'judge_cot'] = result.get('reasoning', '')
                print(f"    评分成功: Sim={result.get('similarity_score')}, Val={result.get('valence_score')}")
            else:
                error_msg = result.get("error", "Unknown Error") if result else "Unknown Error"
                df_final.at[index, 'judge_similarity_score'] = error_msg
                df_final.at[index, 'judge_valence_score'] = error_msg
                df_final.at[index, 'judge_cot'] = error_msg
                print(f"    评分失败: {error_msg}")

            # 定期保存
            if (i + 1) % 5 == 0:
                df_final.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
                print("  [进度已保存]")

    # --- 3. 最终保存 ---
    print("\n--- 步骤3: 最终保存 ---")
    df_final.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')

    print(f"\n{'='*30} 成功 {'='*30}")
    print(f"模型 {model_name} 的PVQ解释文本评分完成。结果已保存至 '{OUTPUT_CSV_PATH}'.")

# ==================== [6. 主执行程序] ====================
if __name__ == "__main__":
    print("=" * 70)
    print("PVQ Rationale Scoring - 批量处理6个模型")
    print("=" * 70)
    print(f"\n待处理模型列表:")
    for i, model in enumerate(MODEL_NAMES, 1):
        print(f"  {i}. {model}")
    print()
    
    # 依次处理每个模型
    for idx, model_name in enumerate(MODEL_NAMES, 1):
        print(f"\n{'#'*70}")
        print(f"# 进度: {idx}/{len(MODEL_NAMES)}")
        print(f"{'#'*70}")
        
        try:
            process_model(model_name)
        except Exception as e:
            print(f"\n[错误] 处理模型 {model_name} 时出错: {e}")
            print("继续处理下一个模型...\n")
            continue
    
    print("\n" + "=" * 70)
    print("全部6个模型处理完成!")
    print("=" * 70)

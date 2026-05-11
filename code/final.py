import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import scipy.stats as stats
import re

# ==================== [1. 全局配置] ====================
# --- 模型列表配置 ---
MODELS = [
    "claude-sonnet-4_5" #在这里选择被测模型
]

# --- 【核心】: 在这里硬编码所有图表的全局统一范围 ---
RADAR_Y_RANGE = [-3, 3]
VALENCE_Y_RANGE = [-3, 3]

# --- 价值观和映射表定义 ---
VALUES = ["self_direction", "stimulation", "hedonism", "achievement", "power", "security", "conformity", "tradition", "benevolence", "universalism"]
SIMILARITY_COLS = [f'similarity_score_{v}' for v in VALUES]
VALENCE_COLS = [f'valence_score_{v}' for v in VALUES]

# --- 施瓦茨价值观四大类映射 ---
SCHWARTZ_CATEGORIES = {
    'openness_to_change': ['self_direction', 'stimulation', 'hedonism'],  # 对变化的开放态度
    'conservation': ['security', 'conformity', 'tradition'],             # 保守主义
    'self_transcendence': ['benevolence', 'universalism'],               # 自我超越
    'self_enhancement': ['achievement', 'power']                         # 自我提升
}

CATEGORY_NAMES_EN = {
    'openness_to_change': 'Openness to Change',
    'conservation': 'Conservation', 
    'self_transcendence': 'Self-Transcendence',
    'self_enhancement': 'Self-Enhancement'
}
SCENARIO_TO_RELEVANT_VALUES = {
    # SC01-03: Power vs. Universalism
    1: ['power', 'universalism'], 2: ['power', 'universalism'], 3: ['power', 'universalism'],
    # SC04-06: Achievement vs. Universalism
    4: ['achievement', 'universalism'], 5: ['achievement', 'universalism'], 6: ['achievement', 'universalism'],
    # SC07-09: Power vs. Benevolence
    7: ['power', 'benevolence'], 8: ['power', 'benevolence'], 9: ['power', 'benevolence'],
    # SC10-12: Achievement vs. Benevolence
    10: ['achievement', 'benevolence'], 11: ['achievement', 'benevolence'], 12: ['achievement', 'benevolence'],
    # SC13-15: Self-Direction vs. Security
    13: ['self_direction', 'security'], 14: ['self_direction', 'security'], 15: ['self_direction', 'security'],
    # SC16-18: Self-Direction vs. Conformity
    16: ['self_direction', 'conformity'], 17: ['self_direction', 'conformity'], 18: ['self_direction', 'conformity'],
    # SC19-21: Self-Direction vs. Tradition
    19: ['self_direction', 'tradition'], 20: ['self_direction', 'tradition'], 21: ['self_direction', 'tradition'],
    # SC22-24: Stimulation vs. Security
    22: ['stimulation', 'security'], 23: ['stimulation', 'security'], 24: ['stimulation', 'security'],
    # SC25-27: Stimulation vs. Conformity
    25: ['stimulation', 'conformity'], 26: ['stimulation', 'conformity'], 27: ['stimulation', 'conformity'],
    # SC28-30: Stimulation vs. Tradition
    28: ['stimulation', 'tradition'], 29: ['stimulation', 'tradition'], 30: ['stimulation', 'tradition'],
    # SC31-33: Hedonism vs. Conformity
    31: ['hedonism', 'conformity'], 32: ['hedonism', 'conformity'], 33: ['hedonism', 'conformity'],
    # SC34-36: Hedonism vs. Tradition
    34: ['hedonism', 'tradition'], 35: ['hedonism', 'tradition'], 36: ['hedonism', 'tradition']
}
VALUE_TO_SCENARIOS_MAP = {v: [sid for sid, vals in SCENARIO_TO_RELEVANT_VALUES.items() if v in vals] for v in VALUES}

# --- 场景中价值观与Persona的映射关系（基于scenario_library.py的设计）---
# 格式: scenario_num -> {'A': value_supported_by_persona_A, 'B': value_supported_by_persona_B}
SCENARIO_VALUE_PERSONA_MAP = {
    # SC01-03: Power(A) vs. Universalism(B)
    1: {'A': 'power', 'B': 'universalism'}, 2: {'A': 'power', 'B': 'universalism'}, 3: {'A': 'power', 'B': 'universalism'},
    # SC04-06: Achievement(A) vs. Universalism(B)
    4: {'A': 'achievement', 'B': 'universalism'}, 5: {'A': 'achievement', 'B': 'universalism'}, 6: {'A': 'achievement', 'B': 'universalism'},
    # SC07-09: Power(A) vs. Benevolence(B)
    7: {'A': 'power', 'B': 'benevolence'}, 8: {'A': 'power', 'B': 'benevolence'}, 9: {'A': 'power', 'B': 'benevolence'},
    # SC10-12: Achievement(A) vs. Benevolence(B)
    10: {'A': 'achievement', 'B': 'benevolence'}, 11: {'A': 'achievement', 'B': 'benevolence'}, 12: {'A': 'achievement', 'B': 'benevolence'},
    # SC13-15: Self-Direction(A) vs. Security(B)
    13: {'A': 'self_direction', 'B': 'security'}, 14: {'A': 'self_direction', 'B': 'security'}, 15: {'A': 'self_direction', 'B': 'security'},
    # SC16-18: Self-Direction(A) vs. Conformity(B)
    16: {'A': 'self_direction', 'B': 'conformity'}, 17: {'A': 'self_direction', 'B': 'conformity'}, 18: {'A': 'self_direction', 'B': 'conformity'},
    # SC19-21: Self-Direction(A) vs. Tradition(B)
    19: {'A': 'self_direction', 'B': 'tradition'}, 20: {'A': 'self_direction', 'B': 'tradition'}, 21: {'A': 'self_direction', 'B': 'tradition'},
    # SC22-24: Stimulation(A) vs. Security(B)
    22: {'A': 'stimulation', 'B': 'security'}, 23: {'A': 'stimulation', 'B': 'security'}, 24: {'A': 'stimulation', 'B': 'security'},
    # SC25-27: Stimulation(A) vs. Conformity(B)
    25: {'A': 'stimulation', 'B': 'conformity'}, 26: {'A': 'stimulation', 'B': 'conformity'}, 27: {'A': 'stimulation', 'B': 'conformity'},
    # SC28-30: Stimulation(A) vs. Tradition(B)
    28: {'A': 'stimulation', 'B': 'tradition'}, 29: {'A': 'stimulation', 'B': 'tradition'}, 30: {'A': 'stimulation', 'B': 'tradition'},
    # SC31-33: Hedonism(A) vs. Conformity(B)
    31: {'A': 'hedonism', 'B': 'conformity'}, 32: {'A': 'hedonism', 'B': 'conformity'}, 33: {'A': 'hedonism', 'B': 'conformity'},
    # SC34-36: Hedonism(A) vs. Tradition(B)
    34: {'A': 'hedonism', 'B': 'tradition'}, 35: {'A': 'hedonism', 'B': 'tradition'}, 36: {'A': 'hedonism', 'B': 'tradition'}
}

# ==================== [2. 数据加载与处理函数] ====================

def load_and_clean_data(filepath, score_cols):
    """通用加载和清洗函数"""
    if not os.path.exists(filepath):
        print(f"错误: 输入文件 '{filepath}' 未找到。")
        return None
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"读取文件 '{filepath}' 时发生错误: {e}")
        return None

    for col in score_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            print(f"警告: 在文件 '{filepath}' 中找不到评分列 '{col}'。")
            # 如果评分列不存在，创建一个空列以避免后续错误
            df[col] = np.nan
    
    # 修改清洗策略：保留有任何有效分数的行
    # 计算每行有效分数的数量
    valid_scores = df[score_cols].notna().sum(axis=1)
    # 保留至少有1个分数有效的行
    min_valid_scores = 1
    df = df[valid_scores >= min_valid_scores]
    print(f"数据清洗后保留 {len(df)} 行 (至少 {min_valid_scores}/{len(score_cols)} 列有效)")
    return df

def calculate_profiles(df_perturb, df_pvq):
    """核心计算逻辑：中心化与情境特定聚合，返回一个包含所有画像的DataFrame"""
    profiles = {}
    
    # 1. 计算PVQ他评基准 (相似度)
    if df_pvq is not None and len(df_pvq) > 0 and 'judge_similarity_score' in df_pvq.columns:
        grand_mean_pvq = df_pvq['judge_similarity_score'].mean()
        df_pvq = df_pvq.copy()
        df_pvq.loc[:, 'centered_judge_score'] = df_pvq['judge_similarity_score'] - grand_mean_pvq
        pvq_sim_profile = df_pvq.groupby('value_assessed')['centered_judge_score'].mean()
        profiles['PVQ_Similarity'] = pvq_sim_profile

    # 2. 扰动数据中心化 (相似度和效价) - 使用全局均值进行Scenario Standardization
    df_perturb = df_perturb.copy()  # 避免SettingWithCopyWarning
    
    # 计算全局均值（所有1,440个响应的所有分数的平均值）
    # 这符合论文中的"Scenario Standardization"要求：减去模型的全局情景均值
    global_mean_sim = df_perturb[SIMILARITY_COLS].stack().mean()  # 所有相似度分数的全局均值
    global_mean_val = df_perturb[VALENCE_COLS].stack().mean()      # 所有效价分数的全局均值
    
    # 使用全局均值进行中心化（纠正表达偏差）
    for v in VALUES:
        if f'similarity_score_{v}' in df_perturb.columns:
            df_perturb.loc[:, f'centered_similarity_score_{v}'] = df_perturb[f'similarity_score_{v}'] - global_mean_sim
        if f'valence_score_{v}' in df_perturb.columns:
            df_perturb.loc[:, f'centered_valence_score_{v}'] = df_perturb[f'valence_score_{v}'] - global_mean_val

    # 3. 计算所有扰动画像 (常规情境特定聚合)
    df_perturb.loc[:, 'plot_group'] = 'Other'
    df_perturb.loc[df_perturb['influence_type'] == 'Situational', 'plot_group'] = 'Situational'
    df_perturb.loc[df_perturb['influence_type'] == 'Pressure', 'plot_group'] = 'Pressure'
    df_perturb.loc[df_perturb['form_subtype'].str.contains('positive', na=False), 'plot_group'] = 'Positive_Frame'
    df_perturb.loc[df_perturb['form_subtype'].str.contains('negative', na=False), 'plot_group'] = 'Negative_Frame'
    
    # 4. 新的Persona计算逻辑：基于价值观倾向性的分组
    # 检查是否有persona数据
    persona_data = df_perturb[df_perturb['form_subtype'].isin(['persona_A', 'persona_B'])]
    
    if len(persona_data) > 0:
        # 添加scenario_num列用于匹配
        import re
        def extract_scenario_num(s):
            if isinstance(s, str):
                match = re.search(r'\d+', s)
                return int(match.group()) if match else None
            return int(s) if pd.notna(s) else None
        
        persona_data = persona_data.copy()
        persona_data['scenario_num'] = persona_data['scenario_id'].apply(extract_scenario_num)
        
        # 为每个价值观维度分别计算support和oppose画像（基于场景设计的固定角色）
        support_profile = pd.Series(index=VALUES, dtype=float)
        oppose_profile = pd.Series(index=VALUES, dtype=float)
        support_valence = pd.Series(index=VALUES, dtype=float)
        oppose_valence = pd.Series(index=VALUES, dtype=float)
        
        for value in VALUES:
            relevant_scenarios = VALUE_TO_SCENARIOS_MAP.get(value, [])
            
            # 初始化该价值观的累积分数列表
            support_scores = []
            oppose_scores = []
            support_valences = []
            oppose_valences = []
            
            # 遍历每个相关场景，根据场景设计确定角色
            for scenario_num in relevant_scenarios:
                scenario_data = persona_data[persona_data['scenario_num'] == scenario_num]
                if scenario_data.empty:
                    continue
                
                # 获取该场景的价值观-角色映射
                persona_map = SCENARIO_VALUE_PERSONA_MAP.get(scenario_num, {})
                if not persona_map:
                    continue
                
                # 确定当前价值观在该场景中由哪个角色支持
                if persona_map.get('A') == value:
                    # persona_A支持该价值观，persona_B反对
                    support_persona = 'persona_A'
                    oppose_persona = 'persona_B'
                elif persona_map.get('B') == value:
                    # persona_B支持该价值观，persona_A反对
                    support_persona = 'persona_B'
                    oppose_persona = 'persona_A'
                else:
                    # 该场景不涉及当前价值观（理论上不应该发生）
                    continue
                
                # 提取支持/反对角色的分数
                sim_col = f'centered_similarity_score_{value}'
                val_col = f'centered_valence_score_{value}'
                
                support_data = scenario_data[scenario_data['form_subtype'] == support_persona]
                oppose_data = scenario_data[scenario_data['form_subtype'] == oppose_persona]
                
                # 收集分数
                if sim_col in support_data.columns:
                    support_scores.extend(support_data[sim_col].dropna().tolist())
                if sim_col in oppose_data.columns:
                    oppose_scores.extend(oppose_data[sim_col].dropna().tolist())
                if val_col in support_data.columns:
                    support_valences.extend(support_data[val_col].dropna().tolist())
                if val_col in oppose_data.columns:
                    oppose_valences.extend(oppose_data[val_col].dropna().tolist())
            
            # 计算平均值
            if support_scores:
                support_profile[value] = np.mean(support_scores)
            if oppose_scores:
                oppose_profile[value] = np.mean(oppose_scores)
            if support_valences:
                support_valence[value] = np.mean(support_valences)
            if oppose_valences:
                oppose_valence[value] = np.mean(oppose_valences)
        
        # 保存新的persona画像
        profiles['Person_Support_Similarity'] = support_profile
        profiles['Person_Oppose_Similarity'] = oppose_profile
        profiles['Person_Support_Valence'] = support_valence
        profiles['Person_Oppose_Valence'] = oppose_valence

    # print("调试信息: 在数据中找到的plot_group有:", df_perturb['plot_group'].unique())

    for group_name in df_perturb['plot_group'].unique():
        if pd.isna(group_name) or group_name == 'Other': continue
        
        sim_profile = pd.Series(index=VALUES, dtype=float)
        val_profile = pd.Series(index=VALUES, dtype=float)
        
        for value in VALUES:
            relevant_scenarios = VALUE_TO_SCENARIOS_MAP.get(value, [])
            
            # 需要将字符串scenario_id转换为整数以匹配relevant_scenarios
            # 提取scenario_id的数字部分（例如 "SC01" -> 1）
            def extract_scenario_num(s):
                if isinstance(s, str):
                    import re
                    match = re.search(r'\d+', s)
                    return int(match.group()) if match else None
                return int(s) if pd.notna(s) else None
            
            # 创建临时列用于数字比较
            df_perturb_temp = df_perturb.copy()
            df_perturb_temp['scenario_num'] = df_perturb_temp['scenario_id'].apply(extract_scenario_num)
            
            subset_df = df_perturb_temp[
                (df_perturb_temp['plot_group'] == group_name) &
                (df_perturb_temp['scenario_num'].isin(relevant_scenarios))
            ]
            
            if f'centered_similarity_score_{value}' in subset_df.columns:
                sim_profile[value] = subset_df[f'centered_similarity_score_{value}'].mean()
            if f'valence_score_{value}' in subset_df.columns:
                val_profile[value] = subset_df[f'valence_score_{value}'].mean()
        
        profiles[f'{group_name}_Similarity'] = sim_profile
        profiles[f'{group_name}_Valence'] = val_profile
        
    return pd.DataFrame(profiles)
def calculate_schwartz_categories_profiles(profiles_df):
    """计算施瓦茨价值观四大类的聚合画像"""
    category_profiles = {}
    
    for group_col in profiles_df.columns:
        if '_Similarity' in group_col or '_Valence' in group_col:
            category_scores = {}
            
            for category, values in SCHWARTZ_CATEGORIES.items():
                # 计算每个大类的平均分
                available_values = [v for v in values if v in profiles_df.index]
                if available_values:
                    category_scores[category] = profiles_df.loc[available_values, group_col].mean()
                else:
                    category_scores[category] = 0
            
            category_profiles[group_col] = pd.Series(category_scores)
    
    return pd.DataFrame(category_profiles)

def calculate_quantitative_metrics(profiles_df):
    """计算扰动效应的定量指标"""
    metrics = {}
    
    # 1. 变化率计算 (Change Rate)
    if 'PVQ_Similarity' in profiles_df.columns:
        pvq = profiles_df['PVQ_Similarity']
        
        for col in profiles_df.columns:
            if col != 'PVQ_Similarity' and '_Similarity' in col:
                perturbation = profiles_df[col]
                
                # 绝对变化量
                absolute_change = perturbation - pvq
                
                # 相对变化率 (处理零值情况)
                relative_change = np.where(
                    np.abs(pvq) > 0.01,  # 避免除以接近零的数
                    (perturbation - pvq) / np.abs(pvq) * 100,
                    np.where(np.abs(perturbation) > 0.01, np.inf, 0)  # 从零变为非零
                )
                
                perturbation_name = col.replace('_Similarity', '')
                metrics[f'{perturbation_name}_Absolute_Change'] = absolute_change
                metrics[f'{perturbation_name}_Relative_Change'] = relative_change
    
    # 2. 扰动强度指标 (Perturbation Intensity)
    for col in profiles_df.columns:
        if '_Similarity' in col:
            values = profiles_df[col]
            perturbation_name = col.replace('_Similarity', '')
            
            # 变异系数 (CV = std/mean)
            cv = np.std(values) / (np.abs(np.mean(values)) + 1e-6) * 100
            metrics[f'{perturbation_name}_Coefficient_of_Variation'] = cv
            
            # 范围指标
            value_range = np.max(values) - np.min(values)
            metrics[f'{perturbation_name}_Value_Range'] = value_range
            
            # 极值比例 - 基于变化量而不是绝对分数
            if 'PVQ_Similarity' in profiles_df.columns and col != 'PVQ_Similarity':
                pvq_values = profiles_df['PVQ_Similarity']
                changes = values - pvq_values  # 计算变化量
                extreme_threshold = 1.5  # 定义极值变化阈值
                extreme_count = np.sum(np.abs(changes) > extreme_threshold)
                extreme_ratio = extreme_count / len(changes) * 100
            else:
                # 如果没有基准数据，则基于绝对分数计算（向后兼容）
                extreme_threshold = 1.5
                extreme_count = np.sum(np.abs(values) > extreme_threshold)
                extreme_ratio = extreme_count / len(values) * 100
            metrics[f'{perturbation_name}_Extreme_Ratio'] = extreme_ratio
    
    # 3. 扰动方向性分析
    if 'PVQ_Similarity' in profiles_df.columns:
        pvq = profiles_df['PVQ_Similarity']
        
        for col in profiles_df.columns:
            if col != 'PVQ_Similarity' and '_Similarity' in col:
                perturbation = profiles_df[col]
                perturbation_name = col.replace('_Similarity', '')
                
                # 方向一致性（正负变化的比例）
                changes = perturbation - pvq
                positive_changes = np.sum(changes > 0.1)  # 显著正向变化
                negative_changes = np.sum(changes < -0.1)  # 显著负向变化
                no_changes = len(changes) - positive_changes - negative_changes
                
                metrics[f'{perturbation_name}_Positive_Changes'] = positive_changes
                metrics[f'{perturbation_name}_Negative_Changes'] = negative_changes
                metrics[f'{perturbation_name}_Neutral_Changes'] = no_changes
                
                # 净变化方向
                net_direction = 'Positive' if positive_changes > negative_changes else 'Negative' if negative_changes > positive_changes else 'Neutral'
                metrics[f'{perturbation_name}_Net_Direction'] = net_direction
    
    return pd.DataFrame(dict([(k, pd.Series([v] if np.isscalar(v) else v)) for k, v in metrics.items()]))

def calculate_schwartz_quantitative_metrics(category_profiles_df):
    """计算施瓦茨四大类的定量指标"""
    metrics = {}
    
    if 'PVQ_Similarity' in category_profiles_df.columns:
        pvq = category_profiles_df['PVQ_Similarity']
        
        for col in category_profiles_df.columns:
            if col != 'PVQ_Similarity' and '_Similarity' in col:
                perturbation = category_profiles_df[col]
                perturbation_name = col.replace('_Similarity', '')
                
                # 四大类变化率
                changes = perturbation - pvq
                metrics[f'{perturbation_name}_Category_Changes'] = changes
                
                # 最大变化类别
                max_change_idx = np.argmax(np.abs(changes))
                max_change_category = changes.index[max_change_idx]
                max_change_value = changes.iloc[max_change_idx]
                
                metrics[f'{perturbation_name}_Max_Change_Category'] = max_change_category
                metrics[f'{perturbation_name}_Max_Change_Value'] = max_change_value
                
                # 变化平衡性（标准差，越小越平衡）
                change_balance = np.std(changes)
                metrics[f'{perturbation_name}_Change_Balance'] = change_balance
    
    return metrics

def calculate_ranking_shift_statistics(df_perturb, profiles_df, n_bootstrap=1000, ci_level=0.95):
    """
    计算扰动条件下的价值观排名变化（基于真实排名）统计数据

    研究问题：provide statistical significance tests for key shifts in value rankings under perturbations

    分析层次：聚合水平（群体层面）
    分析维度：跨价值观维度（所有10个Schwartz价值观维度）

    Parameters:
    - df_perturb: 原始扰动数据（包含所有个体响应）
    - profiles_df: 计算好的画像数据（各条件下10个价值观的平均分数）
    - n_bootstrap: Bootstrap重采样次数（默认1000）
    - ci_level: 置信区间水平（默认95%）

    Returns:
    - DataFrame包含各扰动条件的排名变化统计，包括：
        - 排名（Rank）：各价值观在每个条件下的排名位置
        - 排名变化（Rank Difference）：扰动条件相对于基准的排名变化
        - Cohen's d：分数差异的标准化效应量
        - Wilcoxon p-value：排名差异的非参数显著性检验
        - Bootstrap CI：排名变化的置信区间
        - Top-k Overlap：前k名重叠比例
    """
    statistics_results = []

    # 定义需要比较的条件对
    comparison_pairs = [
        ('PVQ_Similarity', 'Situational_Similarity', 'PVQ_vs_Situational', 'PVQ→Situational'),
        ('Situational_Similarity', 'Pressure_Similarity', 'Situational_vs_Pressure', 'Situational→Pressure')
    ]

    for baseline_col, perturb_col, comparison_name, comparison_label in comparison_pairs:
        if baseline_col not in profiles_df.columns or perturb_col not in profiles_df.columns:
            continue

        baseline_profile = profiles_df[baseline_col]
        perturb_profile = profiles_df[perturb_col]

        # Step 1: 计算各条件下的排名（基于平均分数）
        # rank=1 表示分数最高（排名最高）
        baseline_ranks = baseline_profile.rank(ascending=False, method='average')
        perturb_ranks = perturb_profile.rank(ascending=False, method='average')

        for value in VALUES:
            if value not in profiles_df.index:
                continue

            baseline_score = baseline_profile.loc[value]
            perturb_score = perturb_profile.loc[value]

            # Step 2: 计算排名（Rank）
            baseline_rank = baseline_ranks.loc[value]
            perturb_rank = perturb_ranks.loc[value]

            # Step 3: 计算排名变化（Rank Difference）
            # 正值表示排名下降（分数排名位置变低）
            # 负值表示排名上升（分数排名位置变高）
            rank_difference = perturb_rank - baseline_rank

            # Step 4: 从原始数据计算统计量
            sim_col = f'similarity_score_{value}'

            # 提取两种条件下的原始分数
            if 'influence_type' in df_perturb.columns:
                baseline_raw = df_perturb[df_perturb['influence_type'] == 'Baseline'][sim_col].dropna()
                situational_raw = df_perturb[df_perturb['influence_type'] == 'Situational'][sim_col].dropna()
                pressure_raw = df_perturb[df_perturb['influence_type'] == 'Pressure'][sim_col].dropna()
            else:
                baseline_raw = pd.Series([baseline_score])
                situational_raw = pd.Series([perturb_score])
                pressure_raw = pd.Series()

            # 根据比较类型选择数据
            if 'PVQ' in comparison_name:
                group1_raw = baseline_raw if len(baseline_raw) > 0 else pd.Series([baseline_score])
                group2_raw = situational_raw if len(situational_raw) > 0 else pd.Series([perturb_score])
            else:  # Situational_vs_Pressure
                group1_raw = situational_raw if len(situational_raw) > 0 else pd.Series([baseline_score])
                group2_raw = pressure_raw if len(pressure_raw) > 0 else pd.Series([perturb_score])

            # 基本统计量
            n1, n2 = len(group1_raw), len(group2_raw)
            mean1, mean2 = group1_raw.mean(), group2_raw.mean()
            std1, std2 = group1_raw.std(), group2_raw.std()

            # Cohen's d（分数差异的标准化效应量）
            pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)) if n1 + n2 > 2 else 1
            cohens_d = (mean2 - mean1) / pooled_std if pooled_std > 0 else 0

            # Step 5: Wilcoxon signed-rank test（非参数检验，适合排名数据）
            if n1 == n2 and n1 >= 5:
                try:
                    # 成对样本的符号秩检验
                    diff = np.array(group2_raw) - np.array(group1_raw)
                    diff = diff[~np.isnan(diff)]
                    if len(diff) >= 5:
                        stat, wilcoxon_p = stats.wilcoxon(diff)
                    else:
                        wilcoxon_p = np.nan
                except:
                    wilcoxon_p = np.nan
            else:
                # 独立样本的Mann-Whitney U检验
                try:
                    if n1 >= 3 and n2 >= 3:
                        stat, wilcoxon_p = stats.mannwhitneyu(group1_raw, group2_raw, alternative='two-sided')
                    else:
                        wilcoxon_p = np.nan
                except:
                    wilcoxon_p = np.nan

            # Step 6: Bootstrap置信区间（基于排名的重采样）
            if n_bootstrap > 0 and n1 >= 3 and n2 >= 3:
                bootstrap_rank_diffs = []
                for _ in range(n_bootstrap):
                    # 重采样
                    sample1 = group1_raw.sample(n=min(len(group1_raw), 30), replace=True)
                    sample2 = group2_raw.sample(n=min(len(group2_raw), 30), replace=True)

                    # 计算该样本下value维度的分数
                    mean1_s, mean2_s = sample1.mean(), sample2.mean()

                    # 获取该样本下所有价值观的分数（需要简化处理）
                    # 这里用bootstrap分数差异近似排名变化
                    bootstrap_rank_diffs.append(mean2_s - mean1_s)

                alpha = 1 - ci_level
                ci_lower = np.percentile(bootstrap_rank_diffs, alpha/2 * 100)
                ci_upper = np.percentile(bootstrap_rank_diffs, (1 - alpha/2) * 100)
            else:
                ci_lower, ci_upper = np.nan, np.nan

            # Step 7: Spearman相关系数（排名稳定性）
            if n1 >= 3 and n2 >= 3:
                try:
                    # 模拟两个条件的排名
                    all_scores = list(group1_raw) + list(group2_raw)
                    n_total = len(all_scores)
                    ranks = stats.rankdata(all_scores)
                    ranks1 = ranks[:n1]
                    ranks2 = ranks[n1:]
                    spearman_r, spearman_p = stats.spearmanr(ranks1, ranks2)
                except:
                    spearman_r, spearman_p = np.nan, np.nan
            else:
                spearman_r, spearman_p = np.nan, np.nan

            # Step 8: Top-k重叠比例
            top_k = 3  # 前3名
            baseline_top = set(baseline_ranks[baseline_ranks <= top_k].index)
            perturb_top = set(perturb_ranks[perturb_ranks <= top_k].index)
            top_overlap = len(baseline_top & perturb_top) / top_k if top_k > 0 else 0

            # Step 9: 判断显著性
            significance_level = 'n.s.'
            significance_marker = ''
            if not np.isnan(wilcoxon_p):
                if wilcoxon_p < 0.001:
                    significance_level = 'p<0.001'
                    significance_marker = '***'
                elif wilcoxon_p < 0.01:
                    significance_level = 'p<0.01'
                    significance_marker = '**'
                elif wilcoxon_p < 0.05:
                    significance_level = 'p<0.05'
                    significance_marker = '*'

            # Step 10: 效应量解释
            effect_interpretation = interpret_cohens_d(cohens_d)

            # Step 11: 排名变化方向分类
            if rank_difference < -1.5:
                shift_direction = 'Large Increase'
            elif rank_difference < -0.5:
                shift_direction = 'Moderate Increase'
            elif rank_difference < 0.5:
                shift_direction = 'Stable'
            elif rank_difference < 1.5:
                shift_direction = 'Moderate Decrease'
            else:
                shift_direction = 'Large Decrease'

            statistics_results.append({
                'comparison': comparison_name,
                'comparison_label': comparison_label,
                'value_dimension': value,
                # 原始分数
                'baseline_mean_score': round(mean1, 4),
                'perturbation_mean_score': round(mean2, 4),
                'score_difference': round(mean2 - mean1, 4),
                # 排名（核心指标）
                'baseline_rank': int(baseline_rank),
                'perturbation_rank': int(perturb_rank),
                'rank_difference': int(rank_difference),
                # 统计检验
                'n_baseline': n1,
                'n_perturbation': n2,
                'cohens_d': round(cohens_d, 4),
                'effect_size_category': effect_interpretation,
                'wilcoxon_p_value': round(wilcoxon_p, 6) if not np.isnan(wilcoxon_p) else np.nan,
                'wilcoxon_significance': significance_level,
                'significance_marker': significance_marker,
                # 置信区间
                'ci_lower': round(ci_lower, 4) if not np.isnan(ci_lower) else np.nan,
                'ci_upper': round(ci_upper, 4) if not np.isnan(ci_upper) else np.nan,
                'ci_level': f"{int(ci_level*100)}%",
                # 排名稳定性
                'spearman_r': round(spearman_r, 4) if not np.isnan(spearman_r) else np.nan,
                'top3_overlap': round(top_overlap, 4),
                # 变化方向
                'shift_direction': shift_direction
            })

    statistics_df = pd.DataFrame(statistics_results)
    return statistics_df

def interpret_cohens_d(d):
    """解释Cohen's d效应量大小"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def generate_ranking_shift_summary(statistics_df, output_dir, model_name):
    """
    生成排名变化统计摘要报告

    研究问题：provide statistical significance tests for key shifts in value rankings under perturbations

    分析层次：聚合水平（群体层面）
    分析维度：跨价值观维度（所有10个Schwartz价值观维度）

    统计指标：
    - 排名（Rank）：各价值观在每个条件下的排名位置
    - 排名变化（Rank Difference）：扰动条件相对于基准的排名变化
    - Cohen's d：分数差异的标准化效应量
    - Wilcoxon p-value：排名差异的非参数显著性检验
    - Bootstrap CI：排名变化的置信区间
    """
    if statistics_df.empty:
        return None

    report_path = os.path.join(output_dir, f"{model_name}_ranking_shift_statistics_report.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("STATISTICAL SIGNIFICANCE TESTS FOR VALUE RANKING SHIFTS UNDER PERTURBATIONS\n")
        f.write("=" * 80 + "\n")
        f.write("\n研究问题：Can the authors provide statistical significance tests\n")
        f.write("          (e.g., confidence intervals or effect sizes) for key shifts\n")
        f.write("          in value rankings under perturbations?\n")
        f.write("\n分析层次：聚合水平（群体层面）\n")
        f.write("分析维度：跨价值观维度（10个Schwartz价值观维度）\n")

        for comparison in statistics_df['comparison'].unique():
            comp_data = statistics_df[statistics_df['comparison'] == comparison]

            f.write(f"\n{'='*80}\n")
            f.write(f"COMPARISON: {comparison}\n")
            f.write(f"{'='*80}\n\n")

            # 使用正确的列名
            rank_diff_col = 'rank_difference' if 'rank_difference' in comp_data.columns else 'ranking_shift'
            p_val_col = 'wilcoxon_p_value' if 'wilcoxon_p_value' in comp_data.columns else 'p_value'

            # 摘要统计
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Value Dimensions: {len(comp_data)}\n")
            f.write(f"Mean Rank Difference: {comp_data[rank_diff_col].mean():.4f}\n")
            f.write(f"Std of Rank Difference: {comp_data[rank_diff_col].std():.4f}\n")
            f.write(f"Max Rank Increase (↑): {comp_data[rank_diff_col].min():.0f}\n")
            f.write(f"Max Rank Decrease (↓): {comp_data[rank_diff_col].max():.0f}\n\n")

            # Top-3 重叠比例
            if 'top3_overlap' in comp_data.columns:
                f.write(f"Top-3 Overlap: {comp_data['top3_overlap'].iloc[0]:.2%}\n\n")

            # 显著变化（Wilcoxon p < 0.05）
            if p_val_col in comp_data.columns:
                significant = comp_data[comp_data[p_val_col] < 0.05]
                f.write(f"Significant Changes (Wilcoxon p < 0.05): {len(significant)}/{len(comp_data)}\n")

                if not significant.empty:
                    f.write("\nSignificant Value Dimensions:\n")
                    for _, row in significant.iterrows():
                        sig_marker = "***" if row[p_val_col] < 0.001 else "**" if row[p_val_col] < 0.01 else "*"
                        rank_shift_str = f"{row[rank_diff_col]:+.0f}" if isinstance(row[rank_diff_col], (int, float)) else f"{row[rank_diff_col]:.3f}"
                        f.write(f"  - {row['value_dimension']}: ΔRank={rank_shift_str}, "
                               f"d={row['cohens_d']:.3f} ({row['effect_size_category']}), "
                               f"p={row[p_val_col]:.4f} {sig_marker}\n")
            f.write("\n")

            # 效应量分布
            effect_col = 'effect_size_category' if 'effect_size_category' in comp_data.columns else 'effect_size_interpretation'
            f.write("Effect Size Distribution (Cohen's d):\n")
            for effect_level in ['negligible', 'small', 'medium', 'large']:
                if effect_col in comp_data.columns:
                    count = len(comp_data[comp_data[effect_col] == effect_level])
                    pct = count / len(comp_data) * 100
                    f.write(f"  - {effect_level}: {count} ({pct:.1f}%)\n")

            f.write("\n")

            # 排名变化方向分布
            shift_dir_col = 'shift_direction'
            if shift_dir_col in comp_data.columns:
                f.write("Ranking Shift Direction Distribution:\n")
                for direction in ['Large Increase', 'Moderate Increase', 'Stable', 'Moderate Decrease', 'Large Decrease']:
                    count = len(comp_data[comp_data[shift_dir_col] == direction])
                    pct = count / len(comp_data) * 100
                    f.write(f"  - {direction}: {count} ({pct:.1f}%)\n")
            f.write("\n")

            # 详细表格
            f.write("DETAILED STATISTICS BY VALUE DIMENSION:\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Value':<18} {'Rank(Base)':>10} {'Rank(Pert)':>10} {'ΔRank':>8} {'Cohen d':>10} {'Effect':>12} {'p-value':>10} {'95% CI':>20}\n")
            f.write("-" * 100 + "\n")

            for _, row in comp_data.iterrows():
                baseline_rank = row.get('baseline_rank', 'N/A')
                perturb_rank = row.get('perturbation_rank', 'N/A')
                rank_diff = row[rank_diff_col]
                rank_diff_str = f"{rank_diff:+.0f}" if isinstance(rank_diff, (int, float)) else f"{rank_diff:.3f}"

                ci_str = "N/A"
                if 'ci_lower' in row and 'ci_upper' in row:
                    if pd.notna(row['ci_lower']) and pd.notna(row['ci_upper']):
                        ci_str = f"[{row['ci_lower']:.2f}, {row['ci_upper']:.2f}]"

                sig_marker = ""
                if p_val_col in row:
                    p_val = row[p_val_col]
                    if pd.notna(p_val):
                        sig_marker = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""

                effect = row.get(effect_col, 'N/A') if effect_col in row else 'N/A'

                p_str = f"{row[p_val_col]:.4f}" if p_val_col in row and pd.notna(row.get(p_val_col)) else "N/A"

                f.write(f"{row['value_dimension']:<18} {baseline_rank:>10} {perturb_rank:>10} {rank_diff_str:>8} "
                       f"{row['cohens_d']:>10.3f} {effect:>12} {p_str:>10} {sig_marker} {ci_str:>18}\n")

            f.write("\n")

            # 排名变化表格（更直观）
            f.write("\nRANKING POSITION CHANGES:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Value':<18} {'Baseline Rank':>14} {'Perturbation Rank':>18} {'Change':>10}\n")
            f.write("-" * 60 + "\n")

            for _, row in comp_data.sort_values('baseline_rank').iterrows():
                baseline_r = int(row['baseline_rank']) if isinstance(row['baseline_rank'], (int, float)) else row['baseline_rank']
                perturb_r = int(row['perturbation_rank']) if isinstance(row['perturbation_rank'], (int, float)) else row['perturbation_rank']
                rank_diff = row[rank_diff_col]
                rank_diff_str = f"{rank_diff:+.0f}" if isinstance(rank_diff, (int, float)) else f"{rank_diff:.3f}"

                change_symbol = "↑" if rank_diff < 0 else ("↓" if rank_diff > 0 else "→")
                f.write(f"{row['value_dimension']:<18} {baseline_r:>14} {perturb_r:>18} {change_symbol} {rank_diff_str:>8}\n")

            f.write("\n")

    print(f"排名变化统计报告已保存至: {report_path}")
    return report_path

# ==================== [3. 可视化函数] ====================

def plot_line_chart(ax, profiles_df, groups_to_compare, title, y_range):
    """绘制折线图"""
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    for i, group in enumerate(groups_to_compare):
        if group in profiles_df.columns:
            values = profiles_df[group].reindex(VALUES)
            ax.plot(VALUES, values, marker='o', linewidth=2.5, markersize=6, 
                   color=colors[i % len(colors)], label=group.replace('_', ' '))
    
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_ylim(y_range)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.legend()
    return ax

def plot_tendency_comparison_bar(ax, profiles_df, group1, group2, title):
    """
    绘制倾向性对比柱状图
    显示从group1到group2，各维度相对地位的变化
    
    Parameters:
    - group1: 第一个条件（如'PVQ_Similarity'）
    - group2: 第二个条件（如'Situational_Similarity'）
    """
    import matplotlib.pyplot as plt
    
    # 检查必需数据
    if group1 not in profiles_df.columns or group2 not in profiles_df.columns:
        ax.text(0.5, 0.5, f'Required data not available\n{group1} or {group2}', 
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(title, fontsize=14, pad=20)
        return ax
    
    data1 = profiles_df[group1]
    data2 = profiles_df[group2]
    
    # 双重内部标准化：比较两种情境下各维度的相对地位变化
    data1_mean = data1.mean()
    data2_mean = data2.mean()
    
    change_data = []
    for value in VALUES:
        if value in profiles_df.index:
            # 第一个条件下的相对地位
            relative1 = data1.loc[value] - data1_mean
            # 第二个条件下的相对地位
            relative2 = data2.loc[value] - data2_mean
            # 相对地位的变化
            tendency_change = relative2 - relative1
            change_data.append((value, tendency_change))
        else:
            change_data.append((value, 0))
    
    # 按变化量从小到大排序
    change_data_sorted = sorted(change_data, key=lambda x: x[1])
    
    sorted_values = [item[0] for item in change_data_sorted]
    sorted_changes = [item[1] for item in change_data_sorted]
    sorted_labels = [value.replace('_', ' ').title() for value in sorted_values]
    
    # 创建柱状图
    colors = ['#e74c3c' if change > 0 else '#3498db' for change in sorted_changes]
    bars = ax.bar(sorted_labels, sorted_changes, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # 设置图表样式
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_ylabel('Tendency Change (Relative Position Shift)', fontsize=12)
    ax.set_xlabel('Value Dimensions', fontsize=12)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.8)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    
    # 添加数值标签
    for bar, change in zip(bars, sorted_changes):
        height = bar.get_height()
        label_y = height + (0.05 if height > 0 else -0.08)
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
               f'{change:.2f}', ha='center', va='bottom' if height > 0 else 'top', 
               fontsize=9, fontweight='bold')
    
    # 添加图例
    from matplotlib.patches import Patch
    group1_name = group1.replace('_Similarity', '').replace('_', ' ')
    group2_name = group2.replace('_Similarity', '').replace('_', ' ')
    legend_elements = [
        Patch(facecolor='#e74c3c', alpha=0.8, label=f'{group2_name} Position Elevated'),
        Patch(facecolor='#3498db', alpha=0.8, label=f'{group2_name} Position Declined')
    ]
    ax.legend(handles=legend_elements, loc='upper left')
    
    # 设置y轴范围
    valid_changes = [c for c in sorted_changes if not np.isnan(c) and not np.isinf(c)]
    if valid_changes:
        y_min, y_max = min(valid_changes), max(valid_changes)
        y_range = y_max - y_min
        if y_range == 0:
            y_range = abs(y_min) if y_min != 0 else 1.0
        ax.set_ylim(y_min - y_range * 0.15, y_max + y_range * 0.2)
    else:
        ax.set_ylim(-1, 1)
    
    plt.tight_layout()
    return ax

def plot_bar_chart(ax, profiles_df, groups_to_compare, title, y_range):
    """绘制柱状图"""
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    data_to_plot = profiles_df[groups_to_compare].reindex(VALUES)
    data_to_plot.columns = [col.replace('_', ' ') for col in data_to_plot.columns]
    
    data_to_plot.plot(kind='bar', ax=ax, color=colors[:len(groups_to_compare)], width=0.8)
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_ylim(y_range)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    return ax

def plot_schwartz_radar(ax, category_profiles_df, groups_to_compare, title, y_range):
    """绘制施瓦茨四大类雷达图"""
    categories = list(SCHWARTZ_CATEGORIES.keys())
    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    lines, labels = [], []
    
    for i, group in enumerate(groups_to_compare):
        if group in category_profiles_df.columns:
            # 用0填充NaN值
            values = [category_profiles_df.loc[cat, group] if not pd.isna(category_profiles_df.loc[cat, group]) else 0 
                     for cat in categories]
            values += values[:1]  # 闭合图形
            
            line = ax.plot(angles, values, 'o-', linewidth=2.5, markersize=6, 
                          color=colors[i % len(colors)], 
                          label=group.replace('_', ' '))
            lines.extend(line)
            labels.append(group.replace('_', ' '))
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(category_labels, fontsize=11)
    ax.set_ylim(y_range)
    ax.set_title(title, size=14, pad=20)
    ax.grid(True, alpha=0.3)
    
    return lines, labels

def plot_schwartz_line(ax, category_profiles_df, groups_to_compare, title, y_range):
    """绘制施瓦茨四大类折线图"""
    categories = list(SCHWARTZ_CATEGORIES.keys())
    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    for i, group in enumerate(groups_to_compare):
        if group in category_profiles_df.columns:
            values = [category_profiles_df.loc[cat, group] for cat in categories]
            ax.plot(category_labels, values, marker='o', linewidth=2.5, markersize=8, 
                   color=colors[i % len(colors)], label=group.replace('_', ' '))
    
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_ylim(y_range)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=15, labelsize=10)
    ax.legend()
    return ax

def plot_schwartz_bar(ax, category_profiles_df, groups_to_compare, title, y_range):
    """绘制施瓦茨四大类柱状图"""
    categories = list(SCHWARTZ_CATEGORIES.keys())
    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    data_to_plot = category_profiles_df[groups_to_compare].T
    data_to_plot.columns = category_labels
    data_to_plot.index = [idx.replace('_', ' ') for idx in data_to_plot.index]
    
    data_to_plot.plot(kind='bar', ax=ax, color=colors[:len(category_labels)], width=0.8)
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_ylim(y_range)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.legend(title='Schwartz Value Categories')
    ax.grid(True, alpha=0.3, axis='y')
    return ax

def plot_change_rate_heatmap(ax, profiles_df, title):
    """绘制变化率热力图"""
    import matplotlib.pyplot as plt
    
    # 准备变化率数据
    change_data = []
    perturbations = []
    
    if 'PVQ_Similarity' in profiles_df.columns:
        pvq = profiles_df['PVQ_Similarity']
        
        for col in profiles_df.columns:
            if col != 'PVQ_Similarity' and '_Similarity' in col:
                perturbation_name = col.replace('_Similarity', '')
                perturbations.append(perturbation_name)
                
                # 计算相对变化率
                relative_changes = []
                for value in VALUES:
                    if value in profiles_df.index:
                        pvq_val = pvq.loc[value]
                        perturb_val = profiles_df.loc[value, col]
                        
                        if abs(pvq_val) > 0.01:
                            rel_change = (perturb_val - pvq_val) / abs(pvq_val) * 100
                        else:
                            rel_change = 0 if abs(perturb_val) < 0.01 else 100
                        
                        relative_changes.append(rel_change)
                    else:
                        relative_changes.append(0)
                
                change_data.append(relative_changes)
    
    if change_data:
        change_matrix = np.array(change_data)
        im = ax.imshow(change_matrix, cmap='RdBu_r', aspect='auto', vmin=-100, vmax=100)
        
        ax.set_xticks(range(len(VALUES)))
        ax.set_xticklabels([v.replace('_', ' ').title() for v in VALUES], rotation=45, ha='right')
        ax.set_yticks(range(len(perturbations)))
        ax.set_yticklabels(perturbations)
        ax.set_title(title, fontsize=14, pad=20)
        
        # 添加数值标注
        for i in range(len(perturbations)):
            for j in range(len(VALUES)):
                text = ax.text(j, i, f'{change_matrix[i, j]:.0f}%',
                             ha="center", va="center", color="black" if abs(change_matrix[i, j]) < 50 else "white")

        plt.colorbar(im, ax=ax, label='Relative Change (%)')

    return ax


# ==================== [压力扰动统计显著性检验函数] ====================

def calculate_pressure_perturbation_statistics(df_perturb, profiles_df, ci_level=0.95, n_bootstrap=1000):
    """
    计算压力扰动前后相对权重变化（tendency_change）的统计显著性检验

    核心方法：
    1. Bootstrap检验：直接对tendency_change进行重采样，检验其是否显著异于0
    2. 全局检验：Wilcoxon符号秩检验（配对样本）检验整体效应
    3. 秩相关：Spearman相关检验排序稳定性

    Parameters:
    - df_perturb: 原始扰动数据（包含所有个体响应）
    - profiles_df: 计算好的画像数据（各条件下10个价值观的平均分数）
    - ci_level: 置信区间水平（默认95%）
    - n_bootstrap: Bootstrap重采样次数（默认1000）

    Returns:
    - DataFrame包含各价值观维度的统计检验结果
    """
    results = []

    # 检查必需数据
    if 'Situational_Similarity' not in profiles_df.columns or 'Pressure_Similarity' not in profiles_df.columns:
        print("警告: 缺少Situational_Similarity或Pressure_Similarity数据")
        return pd.DataFrame()

    # 计算聚合水平的统计量（与柱状图一致）
    situational = profiles_df['Situational_Similarity']
    pressure = profiles_df['Pressure_Similarity']
    situational_mean = situational.mean()
    pressure_mean = pressure.mean()

    # 提取scenario_num用于匹配
    def extract_scenario_num(s):
        if isinstance(s, str):
            match = re.search(r'\d+', s)
            return int(match.group()) if match else None
        return int(s) if pd.notna(s) else None

    df_temp = df_perturb.copy()
    df_temp['scenario_num'] = df_temp['scenario_id'].apply(extract_scenario_num)

    # 存储各维度的tendency_change用于全局检验
    all_tendency_changes = []
    all_situational_means = []
    all_pressure_means = []

    for value in VALUES:
        if value not in profiles_df.index:
            continue

        # 获取该价值观的相关情景
        relevant_scenarios = VALUE_TO_SCENARIOS_MAP.get(value, [])

        # 提取Situational条件下的原始分数
        situational_mask = (
            (df_temp['influence_type'] == 'Situational') &
            (df_temp['scenario_num'].isin(relevant_scenarios))
        )
        situational_col = f'similarity_score_{value}'

        if situational_col in df_temp.columns:
            situational_raw = df_temp.loc[situational_mask, situational_col].dropna()
        else:
            situational_raw = pd.Series()

        # 提取Pressure条件下的原始分数
        pressure_mask = (
            (df_temp['influence_type'] == 'Pressure') &
            (df_temp['scenario_num'].isin(relevant_scenarios))
        )

        if situational_col in df_temp.columns:
            pressure_raw = df_temp.loc[pressure_mask, situational_col].dropna()
        else:
            pressure_raw = pd.Series()

        n_sit = len(situational_raw)
        n_pres = len(pressure_raw)

        # 计算聚合水平的倾向性变化（与柱状图一致）
        situational_relative = situational.loc[value] - situational_mean
        pressure_relative = pressure.loc[value] - pressure_mean
        tendency_change = pressure_relative - situational_relative

        all_tendency_changes.append(tendency_change)
        all_situational_means.append(situational.loc[value])
        all_pressure_means.append(pressure.loc[value])

        # Bootstrap检验：直接对tendency_change进行重采样
        # 方法：对情景进行重采样，计算每次重采样的tendency_change
        if n_bootstrap > 0 and n_sit >= 3 and n_pres >= 3:
            bootstrap_tendency_changes = []

            # 获取情景级别的数据（每个情景可能有多个响应）
            sit_by_scenario = df_temp.loc[situational_mask].groupby('scenario_num')[situational_col].mean()
            pres_by_scenario = df_temp.loc[pressure_mask].groupby('scenario_num')[situational_col].mean()

            # 确保情景配对
            common_scenarios = set(sit_by_scenario.index) & set(pres_by_scenario.index)

            if len(common_scenarios) >= 3:
                sit_paired = sit_by_scenario.loc[list(common_scenarios)]
                pres_paired = pres_by_scenario.loc[list(common_scenarios)]

                # 计算全局均值（用于中心化）
                global_mean_sim = df_perturb[SIMILARITY_COLS].stack().mean()

                for _ in range(n_bootstrap):
                    # 对情景进行重采样（配对重采样）
                    indices = np.random.choice(len(common_scenarios), size=len(common_scenarios), replace=True)

                    # 重采样后的数据
                    sit_resampled = sit_paired.iloc[indices]
                    pres_resampled = pres_paired.iloc[indices]

                    # 计算重采样后的tendency_change
                    sit_centered = sit_resampled.mean() - global_mean_sim
                    pres_centered = pres_resampled.mean() - global_mean_sim

                    # 注意：这里需要用重采样后的全局均值，简化处理
                    # 使用相对位置计算
                    bootstrap_tendency_changes.append(pres_centered - sit_centered)

                # 计算Bootstrap置信区间
                alpha = 1 - ci_level
                boot_ci_lower = np.percentile(bootstrap_tendency_changes, alpha/2 * 100)
                boot_ci_upper = np.percentile(bootstrap_tendency_changes, (1 - alpha/2) * 100)

                # Bootstrap检验p值：tendency_change显著异于0的比例
                if tendency_change > 0:
                    boot_p_value = 2 * (np.sum(np.array(bootstrap_tendency_changes) <= 0) + 1) / (n_bootstrap + 1)
                else:
                    boot_p_value = 2 * (np.sum(np.array(bootstrap_tendency_changes) >= 0) + 1) / (n_bootstrap + 1)
                boot_p_value = min(boot_p_value, 1.0)  # 双侧检验上限
            else:
                # 如果配对情景不足，使用实例级别的重采样
                sit_centered = situational_raw - global_mean_sim
                pres_centered = pressure_raw - global_mean_sim

                for _ in range(n_bootstrap):
                    sit_sample = sit_centered.sample(n=len(sit_centered), replace=True)
                    pres_sample = pres_centered.sample(n=len(pres_centered), replace=True)

                    # 计算相对位置变化
                    bootstrap_tendency_changes.append(
                        pres_sample.mean() - sit_sample.mean()
                    )

                alpha = 1 - ci_level
                boot_ci_lower = np.percentile(bootstrap_tendency_changes, alpha/2 * 100)
                boot_ci_upper = np.percentile(bootstrap_tendency_changes, (1 - alpha/2) * 100)

                if tendency_change > 0:
                    boot_p_value = 2 * (np.sum(np.array(bootstrap_tendency_changes) <= 0) + 1) / (n_bootstrap + 1)
                else:
                    boot_p_value = 2 * (np.sum(np.array(bootstrap_tendency_changes) >= 0) + 1) / (n_bootstrap + 1)
                boot_p_value = min(boot_p_value, 1.0)
        else:
            boot_ci_lower = np.nan
            boot_ci_upper = np.nan
            boot_p_value = np.nan

        # 计算效应量（基于原始分数）
        if n_sit > 0 and n_pres > 0:
            global_mean_sim = df_perturb[SIMILARITY_COLS].stack().mean()
            situational_centered = situational_raw - global_mean_sim
            pressure_centered = pressure_raw - global_mean_sim

            sit_mean = situational_centered.mean()
            pres_mean = pressure_centered.mean()
            sit_std = situational_centered.std()
            pres_std = pressure_centered.std()

            # Cohen's d 效应量
            if n_sit + n_pres > 2:
                pooled_std = np.sqrt(((n_sit - 1) * sit_std**2 + (n_pres - 1) * pres_std**2) / (n_sit + n_pres - 2))
                if pooled_std > 0:
                    cohens_d = (pres_mean - sit_mean) / pooled_std
                else:
                    cohens_d = 0
            else:
                cohens_d = np.nan

            # 参数方法置信区间
            se_diff = np.sqrt(sit_std**2/n_sit + pres_std**2/n_pres)
            z_score = stats.norm.ppf(1 - (1 - ci_level)/2)
            mean_diff = pres_mean - sit_mean
            param_ci_lower = mean_diff - z_score * se_diff
            param_ci_upper = mean_diff + z_score * se_diff
        else:
            cohens_d = np.nan
            sit_mean = np.nan
            pres_mean = np.nan
            sit_std = np.nan
            pres_std = np.nan
            mean_diff = np.nan
            param_ci_lower = np.nan
            param_ci_upper = np.nan

        # 效应量解释
        if not np.isnan(cohens_d):
            if abs(cohens_d) < 0.2:
                effect_interpretation = 'Negligible'
            elif abs(cohens_d) < 0.5:
                effect_interpretation = 'Small'
            elif abs(cohens_d) < 0.8:
                effect_interpretation = 'Medium'
            else:
                effect_interpretation = 'Large'
        else:
            effect_interpretation = 'N/A'

        # Bootstrap显著性标记
        if not np.isnan(boot_p_value):
            if boot_p_value < 0.001:
                sig_marker = '***'
            elif boot_p_value < 0.01:
                sig_marker = '**'
            elif boot_p_value < 0.05:
                sig_marker = '*'
            else:
                sig_marker = ''
        else:
            sig_marker = ''

        results.append({
            'value_dimension': value,
            'tendency_change': round(tendency_change, 4),
            'situational_profile_mean': round(situational.loc[value], 4),
            'pressure_profile_mean': round(pressure.loc[value], 4),
            'n_situational': n_sit,
            'n_pressure': n_pres,
            'situational_raw_mean': round(sit_mean, 4) if not np.isnan(sit_mean) else np.nan,
            'pressure_raw_mean': round(pres_mean, 4) if not np.isnan(pres_mean) else np.nan,
            'situational_std': round(sit_std, 4) if not np.isnan(sit_std) else np.nan,
            'pressure_std': round(pres_std, 4) if not np.isnan(pres_std) else np.nan,
            'raw_mean_difference': round(mean_diff, 4) if not np.isnan(mean_diff) else np.nan,
            'cohens_d': round(cohens_d, 4) if not np.isnan(cohens_d) else np.nan,
            'effect_size_interpretation': effect_interpretation,
            'bootstrap_p_value': round(boot_p_value, 6) if not np.isnan(boot_p_value) else np.nan,
            'bootstrap_ci_lower': round(boot_ci_lower, 4) if not np.isnan(boot_ci_lower) else np.nan,
            'bootstrap_ci_upper': round(boot_ci_upper, 4) if not np.isnan(boot_ci_upper) else np.nan,
            'parametric_ci_lower': round(param_ci_lower, 4) if not np.isnan(param_ci_lower) else np.nan,
            'parametric_ci_upper': round(param_ci_upper, 4) if not np.isnan(param_ci_upper) else np.nan,
            'significance_marker': sig_marker
        })

    # 全局统计检验
    global_tests = {}
    if len(all_tendency_changes) >= 5:
        # Wilcoxon符号秩检验：检验tendency_change是否系统性地偏离0
        try:
            wilcoxon_stat, wilcoxon_p = stats.wilcoxon(all_tendency_changes)
            global_tests['wilcoxon_p'] = wilcoxon_p
        except:
            global_tests['wilcoxon_p'] = np.nan

        # Spearman相关：检验排序稳定性
        try:
            spearman_rho, spearman_p = stats.spearmanr(all_situational_means, all_pressure_means)
            global_tests['spearman_rho'] = spearman_rho
            global_tests['spearman_p'] = spearman_p
        except:
            global_tests['spearman_rho'] = np.nan
            global_tests['spearman_p'] = np.nan

        # 单样本t检验：检验tendency_change均值是否显著异于0
        try:
            t_stat, t_p = stats.ttest_1samp(all_tendency_changes, 0)
            global_tests['one_sample_t_p'] = t_p
        except:
            global_tests['one_sample_t_p'] = np.nan

    result_df = pd.DataFrame(results)
    result_df.attrs['global_tests'] = global_tests

    return result_df


def generate_pressure_statistics_report(statistics_df, output_dir, model_name):
    """
    生成压力扰动统计显著性检验报告

    Parameters:
    - statistics_df: 统计检验结果DataFrame
    - output_dir: 输出目录
    - model_name: 模型名称
    """
    if statistics_df.empty:
        print("警告: 统计检验结果为空，跳过报告生成")
        return

    # 1. 保存详细CSV
    csv_path = os.path.join(output_dir, f'{model_name}_pressure_perturbation_statistics.csv')
    statistics_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"压力扰动统计检验结果已保存至: {csv_path}")

    # 提取全局检验结果
    global_tests = statistics_df.attrs.get('global_tests', {})

    # 2. 生成文本报告
    report_path = os.path.join(output_dir, f'{model_name}_pressure_perturbation_statistics_report.txt')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"Pressure Perturbation Statistical Significance Report - {model_name}\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. OVERVIEW\n")
        f.write("-" * 40 + "\n")
        f.write(f"Number of value dimensions analyzed: {len(statistics_df)}\n")
        f.write(f"Analysis type: Bootstrap test on tendency_change (relative position shift)\n\n")

        # 统计显著性汇总
        significant_dims = statistics_df[statistics_df['significance_marker'] != '']
        f.write(f"Statistically significant changes (Bootstrap p<0.05): {len(significant_dims)}\n")
        f.write(f"  - p<0.001: {len(statistics_df[statistics_df['significance_marker'] == '***'])}\n")
        f.write(f"  - p<0.01: {len(statistics_df[statistics_df['significance_marker'] == '**'])}\n")
        f.write(f"  - p<0.05: {len(statistics_df[statistics_df['significance_marker'] == '*'])}\n\n")

        # 效应量汇总
        f.write("Effect Size Distribution:\n")
        f.write(f"  - Large (|d| >= 0.8): {len(statistics_df[statistics_df['effect_size_interpretation'] == 'Large'])}\n")
        f.write(f"  - Medium (0.5 <= |d| < 0.8): {len(statistics_df[statistics_df['effect_size_interpretation'] == 'Medium'])}\n")
        f.write(f"  - Small (0.2 <= |d| < 0.5): {len(statistics_df[statistics_df['effect_size_interpretation'] == 'Small'])}\n")
        f.write(f"  - Negligible (|d| < 0.2): {len(statistics_df[statistics_df['effect_size_interpretation'] == 'Negligible'])}\n\n")

        # 全局检验结果
        f.write("2. GLOBAL STATISTICAL TESTS\n")
        f.write("-" * 40 + "\n")
        f.write("Testing whether pressure perturbation has a systematic effect across all value dimensions:\n\n")

        if 'wilcoxon_p' in global_tests and not np.isnan(global_tests['wilcoxon_p']):
            sig = '***' if global_tests['wilcoxon_p'] < 0.001 else ('**' if global_tests['wilcoxon_p'] < 0.01 else ('*' if global_tests['wilcoxon_p'] < 0.05 else ''))
            f.write(f"Wilcoxon Signed-Rank Test: p = {global_tests['wilcoxon_p']:.6f} {sig}\n")
            f.write("  -> Tests if tendency_change values systematically differ from zero\n")
            if global_tests['wilcoxon_p'] < 0.05:
                f.write("  -> RESULT: Pressure perturbation has a SIGNIFICANT overall effect\n\n")
            else:
                f.write("  -> RESULT: No significant overall effect detected\n\n")

        if 'one_sample_t_p' in global_tests and not np.isnan(global_tests['one_sample_t_p']):
            sig = '***' if global_tests['one_sample_t_p'] < 0.001 else ('**' if global_tests['one_sample_t_p'] < 0.01 else ('*' if global_tests['one_sample_t_p'] < 0.05 else ''))
            f.write(f"One-Sample t-Test (vs 0): p = {global_tests['one_sample_t_p']:.6f} {sig}\n")
            f.write("  -> Tests if mean tendency_change significantly differs from zero\n\n")

        if 'spearman_rho' in global_tests and not np.isnan(global_tests['spearman_rho']):
            f.write(f"Spearman Rank Correlation: rho = {global_tests['spearman_rho']:.4f}\n")
            f.write("  -> Tests stability of value rankings between Situational and Pressure conditions\n")
            if global_tests['spearman_rho'] > 0.7:
                f.write("  -> RESULT: Rankings are RELATIVELY STABLE (rho > 0.7)\n\n")
            else:
                f.write("  -> RESULT: Rankings show MODERATE to LOW stability\n\n")

        f.write("3. DETAILED RESULTS BY VALUE DIMENSION\n")
        f.write("-" * 80 + "\n\n")

        # 按倾向性变化排序
        sorted_df = statistics_df.sort_values('tendency_change', ascending=False)

        for _, row in sorted_df.iterrows():
            value = row['value_dimension'].replace('_', ' ').title()
            f.write(f"\n{value}:\n")
            f.write(f"  Tendency Change: {row['tendency_change']:.4f}\n")
            f.write(f"  Profile Means: Situational={row['situational_profile_mean']:.4f}, Pressure={row['pressure_profile_mean']:.4f}\n")
            f.write(f"  Sample Sizes: n(Situational)={row['n_situational']}, n(Pressure)={row['n_pressure']}\n")

            if not np.isnan(row['cohens_d']):
                f.write(f"  Effect Size (Cohen's d): {row['cohens_d']:.4f} ({row['effect_size_interpretation']})\n")
            else:
                f.write(f"  Effect Size (Cohen's d): N/A\n")

            if 'bootstrap_p_value' in row and not np.isnan(row['bootstrap_p_value']):
                sig = row['significance_marker'] if row['significance_marker'] else 'n.s.'
                f.write(f"  Bootstrap p-value: {row['bootstrap_p_value']:.6f} {sig}\n")

            if not np.isnan(row['bootstrap_ci_lower']) and not np.isnan(row['bootstrap_ci_upper']):
                f.write(f"  95% CI (bootstrap): [{row['bootstrap_ci_lower']:.4f}, {row['bootstrap_ci_upper']:.4f}]\n")
                # 判断CI是否包含0
                if row['bootstrap_ci_lower'] > 0 or row['bootstrap_ci_upper'] < 0:
                    f.write("  -> CI excludes zero: SIGNIFICANT relative position shift\n")
                else:
                    f.write("  -> CI includes zero: non-significant shift\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("4. INTERPRETATION GUIDE\n")
        f.write("-" * 40 + "\n")
        f.write("Cohen's d effect size interpretation (Cohen, 1988):\n")
        f.write("  - |d| < 0.2: Negligible effect\n")
        f.write("  - 0.2 <= |d| < 0.5: Small effect\n")
        f.write("  - 0.5 <= |d| < 0.8: Medium effect\n")
        f.write("  - |d| >= 0.8: Large effect\n\n")
        f.write("Significance markers:\n")
        f.write("  - * p < 0.05\n")
        f.write("  - ** p < 0.01\n")
        f.write("  - *** p < 0.001\n\n")
        f.write("Key Concepts:\n")
        f.write("  - tendency_change: Relative position shift from Situational to Pressure condition\n")
        f.write("    (calculated as: (pressure_value - pressure_mean) - (situational_value - situational_mean))\n")
        f.write("  - Positive tendency_change: Value's relative position ELEVATED under pressure\n")
        f.write("  - Negative tendency_change: Value's relative position DECLINED under pressure\n")
        f.write("  - Bootstrap CI: If CI excludes zero, the tendency_change is statistically significant\n")
        f.write("=" * 80 + "\n")

    print(f"统计报告已保存至: {report_path}")

    return statistics_df


def plot_pressure_perturbation_bar(ax, profiles_df, title, standardization_mode='tendency_change'):
    """
    绘制压力扰动柱状图
    
    Parameters:
    - standardization_mode: 标准化模式
      - 'tendency_change' (默认): 倾向性变化 - 双重内部标准化，显示相对地位的变化
      - 'pressure_internal': Pressure内部标准化 - 显示压力下的相对强弱
      - 'absolute_change': 绝对变化量 - 显示 Pressure - Situational
    """
    import matplotlib.pyplot as plt
    
    # 检查必需数据
    if 'Situational_Similarity' not in profiles_df.columns or 'Pressure_Similarity' not in profiles_df.columns:
        ax.text(0.5, 0.5, 'Required data not available\nfor pressure perturbation analysis', 
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(title, fontsize=14, pad=20)
        return ax
    
    # 计算压力相对于情景化的变化
    situational = profiles_df['Situational_Similarity'] 
    pressure = profiles_df['Pressure_Similarity']
    
    if standardization_mode == 'tendency_change':
        # 双重内部标准化：比较两种情境下各维度的相对地位变化
        # 显示"从普通情景到压力情景，各维度相对地位如何变化"
        situational_mean = situational.mean()
        pressure_mean = pressure.mean()
        change_data = []
        
        for value in VALUES:
            if value in profiles_df.index:
                # 普通情景下的相对地位
                situational_relative = situational.loc[value] - situational_mean
                # 压力情景下的相对地位
                pressure_relative = pressure.loc[value] - pressure_mean
                # 相对地位的变化
                tendency_change = pressure_relative - situational_relative
                change_data.append((value, tendency_change))
            else:
                change_data.append((value, 0))
    
    elif standardization_mode == 'pressure_internal':
        # Pressure内部标准化：显示哪些维度在压力下"相对更强"
        pressure_mean = pressure.mean()
        change_data = []
        
        for value in VALUES:
            if value in profiles_df.index:
                relative_strength = pressure.loc[value] - pressure_mean
                change_data.append((value, relative_strength))
            else:
                change_data.append((value, 0))
    
    else:  # 'absolute_change'
        # 绝对变化量：Pressure - Situational
        change_data = []
        
        for value in VALUES:
            if value in profiles_df.index:
                change = pressure.loc[value] - situational.loc[value]
                change_data.append((value, change))
            else:
                change_data.append((value, 0))
    
    # 按变化量从小到大排序
    change_data_sorted = sorted(change_data, key=lambda x: x[1])
    
    # 分离排序后的数据
    sorted_values = [item[0] for item in change_data_sorted]
    sorted_changes = [item[1] for item in change_data_sorted]
    sorted_labels = [value.replace('_', ' ').title() for value in sorted_values]
    
    # 创建柱状图
    colors = ['#e74c3c' if change > 0 else '#3498db' for change in sorted_changes]  # 红色为正，蓝色为负
    bars = ax.bar(sorted_labels, sorted_changes, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # 设置图表样式
    ax.set_title(title, fontsize=14, pad=20)
    
    if standardization_mode == 'tendency_change':
        ax.set_ylabel('Tendency Change (Relative Position Shift)', fontsize=12)
        legend_label_pos = 'Position Elevated'
        legend_label_neg = 'Position Declined'
    elif standardization_mode == 'pressure_internal':
        ax.set_ylabel('Relative Strength (vs Pressure Mean)', fontsize=12)
        legend_label_pos = 'Relatively Stronger'
        legend_label_neg = 'Relatively Weaker'
    else:  # 'absolute_change'
        ax.set_ylabel('Change Score (Pressure - Situational)', fontsize=12)
        legend_label_pos = 'Pressure Increases'
        legend_label_neg = 'Pressure Decreases'
        description = "Shows absolute change from situational to pressure condition"
    
    ax.set_xlabel('Value Dimensions', fontsize=12)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.8)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    
    # 添加数值标签
    for bar, change in zip(bars, sorted_changes):
        height = bar.get_height()
        label_y = height + (0.02 if height > 0 else -0.05)
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
               f'{change:.2f}', ha='center', va='bottom' if height > 0 else 'top', 
               fontsize=9, fontweight='bold')
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#e74c3c', alpha=0.8, label=legend_label_pos),
                      Patch(facecolor='#3498db', alpha=0.8, label=legend_label_neg)]
    ax.legend(handles=legend_elements, loc='upper left')
    
    # 设置y轴范围，确保显示完整
    # 过滤NaN值并检查是否有有效数据
    valid_changes = [c for c in sorted_changes if not np.isnan(c) and not np.isinf(c)]
    if valid_changes:
        y_min, y_max = min(valid_changes), max(valid_changes)
        y_range = y_max - y_min
        # 如果所有值相同（y_range=0），设置一个默认范围
        if y_range == 0:
            y_range = abs(y_min) if y_min != 0 else 1.0
        ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.15)
    else:
        # 如果没有有效数据，设置默认范围
        ax.set_ylim(-1, 1)
    
    return ax

def plot_value_shift_analysis(ax, category_profiles_df, title):
    """绘制价值观体系重心漂移分析图 - 美观的蝴蝶对比图"""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    if 'PVQ_Similarity' not in category_profiles_df.columns or 'Situational_Similarity' not in category_profiles_df.columns:
        ax.text(0.5, 0.5, 'Required data not available\nfor value shift analysis', 
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        if title:  # 只在有标题时设置
            ax.set_title(title, fontsize=14, pad=20)
        return ax
    
    # 计算四大类的变化
    pvq = category_profiles_df['PVQ_Similarity']
    situational = category_profiles_df['Situational_Similarity']
    
    categories = list(SCHWARTZ_CATEGORIES.keys())
    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
    
    pvq_values = [pvq.loc[cat] for cat in categories]
    situational_values = [situational.loc[cat] for cat in categories]
    changes = [situational.loc[cat] - pvq.loc[cat] for cat in categories]
    
    # 创建蝴蝶图 - 左右分离式设计，增加间距
    y_pos = np.arange(len(categories)) * 1.2  # 增加行间距，避免重叠
    
    # 美化配色方案
    pvq_color = '#2E86AB'  # 深蓝色 - 理论理想
    situational_color = '#A23B72'  # 深玫红 - 实践应用
    positive_change_color = '#F18F01'  # 橙色 - 正向变化
    negative_change_color = '#C73E1D'  # 红色 - 负向变化
    
    # 绘制基准值（左侧，负方向）
    pvq_bars = ax.barh(y_pos, [-abs(v) for v in pvq_values], height=0.7,
                           color=pvq_color, alpha=0.8, label='PVQ\n(Theoretical Ideals)')
    
    # 绘制情景化值（右侧，正方向）
    situational_bars = ax.barh(y_pos, [abs(v) for v in situational_values], height=0.7,
                              color=situational_color, alpha=0.8, label='Situational\n(Practical Problem-Solving)')
    
    # 添加中央分割线
    ax.axvline(x=0, color='black', linewidth=2, alpha=0.8)
    
    # 为每个类别添加连接线和变化指示
    for i, (pvq_val, situational_val, change) in enumerate(zip(pvq_values, situational_values, changes)):
        # 连接线颜色根据变化方向确定
        line_color = positive_change_color if change > 0 else negative_change_color
        line_alpha = min(0.8, abs(change) * 2)  # 变化越大，线越明显
        
        # 绘制连接弧线
        if abs(change) > 0:  # 显示所有变化
            # 创建弧线路径
            from matplotlib.patches import FancyArrowPatch
            
            # 起点和终点
            start_x = -abs(pvq_val)
            end_x = abs(situational_val)
            
            # 绘制优美的连接线
            connectionstyle = "arc3,rad=0.2" if change > 0 else "arc3,rad=-0.2"
            arrow = FancyArrowPatch((start_x, y_pos[i]), (end_x, y_pos[i]),
                                  connectionstyle=connectionstyle,
                                  arrowstyle='->', mutation_scale=12,
                                  color=line_color, alpha=line_alpha, linewidth=1.8)
            ax.add_patch(arrow)
            
            # 在中央添加变化值标签，位置调整避免重叠
            change_symbol = '↗' if change > 0 else '↘'
            label_y_offset = 0.15 if i % 2 == 0 else -0.15  # 交替上下偏移
            ax.text(0, y_pos[i] + label_y_offset, f'{change_symbol}{abs(change):.2f}', 
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   color=line_color, bbox=dict(boxstyle="round,pad=0.15", 
                                              facecolor='white', alpha=0.9, edgecolor=line_color))
    
    # 美化坐标轴 - 调整y轴标签位置避免重叠
    ax.set_yticks(y_pos)
    ax.set_yticklabels(category_labels, fontsize=10, fontweight='medium', va='center')
    ax.invert_yaxis()  # 反转y轴，让第一个类别在顶部
    
    # 自定义x轴标签，增加边距
    max_val = max(max([abs(v) for v in pvq_values]), max([abs(v) for v in situational_values]))
    margin = max_val * 0.3  # 增加边距
    x_ticks = np.linspace(-(max_val + margin), (max_val + margin), 7)
    ax.set_xlim(-(max_val + margin * 1.5), (max_val + margin * 1.5))
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f'{abs(x):.1f}' for x in x_ticks], fontsize=9)
    
    # 添加轴标签，位置在图表上方
    label_y = -1.0  # 负值，放置在图表上方
    ax.text(-(max_val + margin) * 0.7, label_y, 'PVQ Score', ha='center', 
           fontsize=12, fontweight='bold', color=pvq_color)
    ax.text((max_val + margin) * 0.7, label_y, 'Situational Score', ha='center', 
           fontsize=12, fontweight='bold', color=situational_color)
    
    # 设置网格和坐标轴样式
    ax.grid(True, alpha=0.2, axis='x')
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 添加图例，位置调整
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1), fontsize=9, 
             frameon=True, shadow=True, fancybox=True)
    
    # 添加标题在图表下方
    if title:  # 只在有标题时设置
        title_y = len(categories) + 0.8  # 正值，放置在图表下方
        ax.text(0, title_y, title, ha='center', va='center', 
               fontsize=13, fontweight='bold', wrap=True)
    
    return ax

def plot_gravity_shift_radar(ax, category_profiles_df, title):
    """绘制重力偏移雷达图 - 双层美观设计"""
    import matplotlib.pyplot as plt
    
    if 'PVQ_Similarity' not in category_profiles_df.columns or 'Situational_Similarity' not in category_profiles_df.columns:
        ax.text(0.5, 0.5, 'Required data not available\nfor gravity shift analysis', 
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.set_title(title, fontsize=14, pad=20)
        return ax
    
    # 获取数据
    pvq = category_profiles_df['PVQ_Similarity']
    situational = category_profiles_df['Situational_Similarity']
    
    categories = list(SCHWARTZ_CATEGORIES.keys())
    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
    
    # 用0填充NaN值
    pvq_values = [pvq.loc[cat] if not pd.isna(pvq.loc[cat]) else 0 for cat in categories]
    situational_values = [situational.loc[cat] if not pd.isna(situational.loc[cat]) else 0 for cat in categories]
    changes = [situational_values[i] - pvq_values[i] for i in range(len(categories))]
    
    # 设置雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    pvq_values += pvq_values[:1]
    situational_values += situational_values[:1]
    changes += changes[:1]
    
    # 美观配色
    pvq_color = '#1f77b4'  # 蓝色系
    situational_color = '#ff7f0e'  # 橙色系
    positive_color = '#2ca02c'  # 绿色
    negative_color = '#d62728'  # 红色
    
    # 绘制基准线（理论理想）
    ax.plot(angles, pvq_values, 'o-', linewidth=3, markersize=8, 
           color=pvq_color, alpha=0.8, label='PVQ\n(Theoretical Ideals)')
    ax.fill(angles, pvq_values, alpha=0.15, color=pvq_color)
    
    # 绘制情景线（实践应用）
    ax.plot(angles, situational_values, 's-', linewidth=3, markersize=8,
           color=situational_color, alpha=0.8, label='Situational\n(Practical Problem-Solving)')
    ax.fill(angles, situational_values, alpha=0.15, color=situational_color)
    
    # 添加变化指示器
    # 过滤有效值用于计算最大值
    valid_pvq = [v for v in pvq_values if not np.isnan(v) and not np.isinf(v)]
    valid_situational = [v for v in situational_values if not np.isnan(v) and not np.isinf(v)]
    
    if valid_pvq and valid_situational:
        max_radius = max(max(valid_pvq), max(valid_situational))
    else:
        max_radius = 1.0  # 默认值
    
    for i, (angle, pvq_val, situational_val, change) in enumerate(zip(angles[:-1], pvq_values[:-1], situational_values[:-1], changes[:-1])):
        # 跳过包含NaN的数据点
        if np.isnan(pvq_val) or np.isnan(situational_val) or np.isnan(change):
            continue
            
        if abs(change) > 0:  # 显示所有变化
            # 计算中心点
            mid_val = (pvq_val + situational_val) / 2
            
            # 变化箭头颜色
            arrow_color = positive_color if change > 0 else negative_color
            
            # 在雷达图上添加变化指示
            ax.annotate('', xy=(angle, situational_val), xytext=(angle, pvq_val),
                       arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2.5, alpha=0.8))
            
            # 添加变化值标签（在外圈）
            label_radius = max_radius * 1.15
            label_x = label_radius * np.cos(angle)
            label_y = label_radius * np.sin(angle)
            
            change_text = f'{change:+.2f}'
            ax.text(angle, label_radius, change_text, ha='center', va='center',
                   fontsize=9, fontweight='bold', color=arrow_color,
                   bbox=dict(boxstyle="circle,pad=0.2", facecolor='white', 
                            edgecolor=arrow_color, alpha=0.9))
    
    # 设置雷达图样式
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(category_labels, fontsize=11, fontweight='medium')
    
    # 美化网格
    ax.set_ylim(-3, 3)  # 根据您的RADAR_Y_RANGE
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#fafafa')  # 淡灰背景
    
    # 设置径向标签
    ax.set_rticks([-2, -1, 0, 1, 2])
    ax.set_rlabel_position(0)
    
    # 标题和图例
    ax.set_title(title, size=14, pad=30, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=10)
    
    # 添加中心说明
    center_text = 'Gravity\nShift'
    ax.text(0, 0, center_text, ha='center', va='center', fontsize=12, 
           fontweight='bold', color='darkblue',
           bbox=dict(boxstyle="circle,pad=0.3", facecolor='lightblue', alpha=0.3))
    
    # 添加象限标签
    quadrant_labels = {
        (np.pi/4, 1.8): 'Enhancement\n↗',
        (3*np.pi/4, 1.8): 'Change\n↗', 
        (5*np.pi/4, 1.8): 'Conservation\n↘',
        (7*np.pi/4, 1.8): 'Transcendence\n↘'
    }
    
    for (angle, radius), label in quadrant_labels.items():
        ax.text(angle, radius, label, ha='center', va='center', fontsize=9,
               style='italic', alpha=0.7, 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.6))
    
    return ax

def plot_quantitative_summary(ax, metrics_df, title):
    """绘制定量分析摘要图"""
    # 选择关键指标进行可视化
    key_metrics = []
    metric_values = []
    
    for col in metrics_df.columns:
        if 'Coefficient_of_Variation' in col:
            key_metrics.append(col.replace('_Coefficient_of_Variation', ' CV'))
            metric_values.append(metrics_df[col].iloc[0] if len(metrics_df[col]) > 0 else 0)
        elif 'Value_Range' in col:
            key_metrics.append(col.replace('_Value_Range', ' Range'))
            metric_values.append(metrics_df[col].iloc[0] if len(metrics_df[col]) > 0 else 0)
    
    if key_metrics:
        colors = plt.cm.viridis(np.linspace(0, 1, len(key_metrics)))
        bars = ax.bar(range(len(key_metrics)), metric_values, color=colors)
        ax.set_xticks(range(len(key_metrics)))
        ax.set_xticklabels(key_metrics, rotation=45, ha='right')
        ax.set_title(title, fontsize=14, pad=20)
        ax.set_ylabel('Metric Value')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom')
    
    return ax

def generate_quantitative_report(all_profiles, category_profiles, quantitative_metrics, schwartz_quantitative, output_dir, model_name):
    """
    生成定量分析报告
    """
    report_path = os.path.join(output_dir, f"{model_name}_quantitative_analysis_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {model_name.upper()} Quantitative Analysis Report ===\n\n")
        
        # 1. 概况统计
        f.write("1. OVERVIEW STATISTICS\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total perturbation scenarios analyzed: {len(all_profiles.index)}\n")
        f.write(f"Total individual values: {len([col for col in all_profiles.columns if 'Similarity' in col])}\n")
        f.write(f"Schwartz categories: {len(SCHWARTZ_CATEGORIES)}\n\n")
        
        # 2. 扰动强度排名 (基于变异系数)
        f.write("2. PERTURBATION INTENSITY RANKING\n")
        f.write("-" * 50 + "\n")
        f.write("Based on Coefficient of Variation (CV):\n")
        
        # 提取CV列
        cv_columns = [col for col in quantitative_metrics.columns if 'Coefficient_of_Variation' in col]
        if cv_columns:
            cv_data = {}
            for col in cv_columns:
                perturbation_name = col.replace('_Coefficient_of_Variation', '')
                cv_value = quantitative_metrics[col].iloc[0] if len(quantitative_metrics[col]) > 0 else 0
                cv_data[perturbation_name] = cv_value
            
            # 排序并输出
            sorted_cv = sorted(cv_data.items(), key=lambda x: x[1], reverse=True)
            for i, (perturbation, cv_value) in enumerate(sorted_cv, 1):
                f.write(f"{i:2d}. {perturbation:<20} CV: {cv_value:.3f}\n")
        else:
            f.write("No CV data available.\n")
        f.write("\n")
        
        # 3. 变化幅度分析
        f.write("3. CHANGE MAGNITUDE ANALYSIS\n")
        f.write("-" * 50 + "\n")
        f.write("Value range (max - min change) per perturbation:\n")
        
        range_columns = [col for col in quantitative_metrics.columns if 'Value_Range' in col]
        if range_columns:
            range_data = {}
            for col in range_columns:
                perturbation_name = col.replace('_Value_Range', '')
                range_value = quantitative_metrics[col].iloc[0] if len(quantitative_metrics[col]) > 0 else 0
                range_data[perturbation_name] = range_value
            
            sorted_ranges = sorted(range_data.items(), key=lambda x: x[1], reverse=True)
            for i, (perturbation, range_value) in enumerate(sorted_ranges, 1):
                f.write(f"{i:2d}. {perturbation:<20} Range: {range_value:.3f}\n")
        else:
            f.write("No range data available.\n")
        f.write("\n")
        
        # 4. 极值分析
        f.write("4. EXTREME VALUE ANALYSIS\n")
        f.write("-" * 50 + "\n")
        f.write("Extreme change ratios (|change| > threshold) per perturbation:\n")
        
        extreme_columns = [col for col in quantitative_metrics.columns if 'Extreme_Ratio' in col]
        if extreme_columns:
            extreme_data = {}
            for col in extreme_columns:
                perturbation_name = col.replace('_Extreme_Ratio', '')
                extreme_value = quantitative_metrics[col].iloc[0] if len(quantitative_metrics[col]) > 0 else 0
                extreme_data[perturbation_name] = extreme_value
            
            sorted_extremes = sorted(extreme_data.items(), key=lambda x: x[1], reverse=True)
            for i, (perturbation, extreme_value) in enumerate(sorted_extremes, 1):
                f.write(f"{i:2d}. {perturbation:<20} Extreme Ratio: {extreme_value:.3f}\n")
        else:
            f.write("No extreme ratio data available.\n")
        f.write("\n")
        
        # 5. 方向性分析
        f.write("5. DIRECTIONAL CHANGE ANALYSIS\n")
        f.write("-" * 50 + "\n")
        f.write("Distribution of positive vs negative changes:\n")
        
        # 提取方向性数据
        positive_columns = [col for col in quantitative_metrics.columns if 'Positive_Changes' in col]
        negative_columns = [col for col in quantitative_metrics.columns if 'Negative_Changes' in col]
        neutral_columns = [col for col in quantitative_metrics.columns if 'Neutral_Changes' in col]
        
        if positive_columns and negative_columns:
            for pos_col, neg_col in zip(positive_columns, negative_columns):
                perturbation_name = pos_col.replace('_Positive_Changes', '')
                pos_changes = quantitative_metrics[pos_col].iloc[0] if len(quantitative_metrics[pos_col]) > 0 else 0
                neg_changes = quantitative_metrics[neg_col].iloc[0] if len(quantitative_metrics[neg_col]) > 0 else 0
                
                # 查找对应的neutral列
                neutral_col = f"{perturbation_name}_Neutral_Changes"
                neutral_changes = quantitative_metrics[neutral_col].iloc[0] if neutral_col in quantitative_metrics.columns else 0
                
                total_changes = pos_changes + neg_changes + neutral_changes
                if total_changes > 0:
                    pos_pct = pos_changes / total_changes * 100
                    neg_pct = neg_changes / total_changes * 100
                    f.write(f"{perturbation_name:<20} Positive: {pos_pct:5.1f}%  Negative: {neg_pct:5.1f}%\n")
        else:
            f.write("No directional change data available.\n")
        f.write("\n")
        
        # 6. 施瓦茨类别分析
        f.write("6. SCHWARTZ CATEGORIES ANALYSIS\n")
        f.write("-" * 50 + "\n")
        if schwartz_quantitative:
            f.write("Most affected categories per perturbation:\n")
            for key, value in schwartz_quantitative.items():
                if 'Category_Changes' in key:
                    perturbation_name = key.replace('_Category_Changes', '')
                    # 检查是否有有效值
                    if value.notna().any():
                        most_affected = value.abs().idxmax()
                        # 再次检查most_affected是否为nan
                        if pd.notna(most_affected):
                            max_change = value.abs().max()
                            direction = "↑" if value[most_affected] > 0 else "↓"
                            f.write(f"{perturbation_name:<20} {CATEGORY_NAMES_EN[most_affected]:<20} {direction} {max_change:.3f}\n")
                        else:
                            f.write(f"{perturbation_name:<20} No valid data\n")
                    else:
                        f.write(f"{perturbation_name:<20} No valid data\n")
        f.write("\n")
        
        # 7. 关键发现
        f.write("7. KEY FINDINGS\n")
        f.write("-" * 50 + "\n")
        
        # 基于可用数据的关键发现
        cv_columns = [col for col in quantitative_metrics.columns if 'Coefficient_of_Variation' in col]
        if cv_columns:
            cv_data = {}
            for col in cv_columns:
                perturbation_name = col.replace('_Coefficient_of_Variation', '')
                cv_value = quantitative_metrics[col].iloc[0] if len(quantitative_metrics[col]) > 0 else 0
                cv_data[perturbation_name] = cv_value
            
            if cv_data:
                max_cv_perturbation = max(cv_data, key=cv_data.get)
                max_cv_value = cv_data[max_cv_perturbation]
                min_cv_perturbation = min(cv_data, key=cv_data.get)
                min_cv_value = cv_data[min_cv_perturbation]
                
                f.write(f"• Highest variability: {max_cv_perturbation} (CV: {max_cv_value:.3f})\n")
                f.write(f"• Most stable: {min_cv_perturbation} (CV: {min_cv_value:.3f})\n")
        
        # 计算平均变化幅度
        similarity_columns = [col for col in all_profiles.columns if 'Similarity' in col and col != 'PVQ_Similarity']
        if similarity_columns and 'PVQ_Similarity' in all_profiles.columns:
            pvq_data = all_profiles['PVQ_Similarity']
            changes = []
            for col in similarity_columns:
                perturbation_data = all_profiles[col]
                change_values = perturbation_data - pvq_data
                changes.extend([abs(val) for val in change_values.dropna()])
            
            if changes:
                mean_abs_change = np.mean(changes)
                f.write(f"• Average absolute change from baseline: {mean_abs_change:.3f}\n")
        
        f.write("\n=== End of Report ===\n")
    
    print(f"定量分析报告已保存至: {report_path}")

def plot_radar(ax, profiles_df, groups_to_compare, legend_title, y_range):
    """在给定的ax上绘制一个雷达图子图，并返回图例句柄"""
    num_vars = len(VALUES)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    ax.set_ylim(y_range)

    lines, labels = [], []
    for group_name in groups_to_compare:
        if group_name in profiles_df.columns:
            # 确保数据是按VALUES的顺序排列的
            profile_data = profiles_df[group_name].reindex(VALUES)
            # 用0填充NaN值，避免绘图错误
            values = profile_data.fillna(0).tolist()
            values += values[:1]
            line, = ax.plot(angles, values, label=group_name, linewidth=2, marker='o')
            ax.fill(angles, values, alpha=0.2)
            lines.append(line)
            labels.append(group_name)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(VALUES, size=9)
    ax.tick_params(axis='y', labelleft=False)
    
    return lines, labels

# ==================== [4. 主执行程序] ====================
if __name__ == "__main__":
    print("="*80)
    print("开始批量评估模型...")
    print("="*80)
    
    for model_idx, model_name in enumerate(MODELS, 1):
        print(f"\n{'='*80}")
        print(f"[{model_idx}/{len(MODELS)}] 正在处理模型: {model_name}")
        print(f"{'='*80}\n")
        
        # 构建文件路径
        perturbation_data_path = f"{model_name}_scored_responses.csv"
        pvq_data_path = f"scored_pvq_rationales_{model_name}.csv"
        output_dir = f"visualizations_{model_name}_final_corrected"
        
        # 检查文件是否存在
        if not os.path.exists(perturbation_data_path):
            print(f"[WARNING] 找不到文件 {perturbation_data_path}，跳过该模型")
            continue
        
        if not os.path.exists(pvq_data_path):
            print(f"[WARNING] 找不到文件 {pvq_data_path}，跳过该模型")
            continue
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 加载数据
        df_perturb = load_and_clean_data(perturbation_data_path, SIMILARITY_COLS + VALENCE_COLS)
        df_pvq = load_and_clean_data(pvq_data_path, ['judge_similarity_score'])

        if df_perturb is None:
            print(f"[WARNING] 无法加载 {perturbation_data_path}，跳过该模型")
            continue
        
        all_profiles = calculate_profiles(df_perturb, df_pvq if df_pvq is not None else pd.DataFrame())
        all_profiles.to_csv(os.path.join(output_dir, f"{model_name}_final_value_profiles.csv"))
        print("\n所有价值观画像已计算完毕并保存。")

        # --- 图表一: 方法论验证 - 聚合效度 ---
        print("\n--- 正在生成图表一: 方法论验证 ---")
        if 'PVQ_Similarity' in all_profiles.columns and 'Situational_Similarity' in all_profiles.columns:
            # 1a. 雷达图
            fig1a, ax1a = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            lines, labels = plot_radar(ax1a, all_profiles, ['PVQ_Similarity', 'Situational_Similarity'],
                                       'Condition', RADAR_Y_RANGE)
            fig1a.suptitle(f'Convergent Validity: PVQ vs. Situational - {model_name} (Radar)', fontsize=16)
            fig1a.legend(lines, labels, loc='upper right', bbox_to_anchor=(1.25, 0.9))
            plt.savefig(os.path.join(output_dir, '1a_validity_radar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig1a)
            
            # 1b. 折线图
            fig1b, ax1b = plt.subplots(figsize=(12, 6))
            plot_line_chart(ax1b, all_profiles, ['PVQ_Similarity', 'Situational_Similarity'],
                           f'Convergent Validity: PVQ vs. Situational - {model_name} (Line)', RADAR_Y_RANGE)
            plt.savefig(os.path.join(output_dir, '1b_validity_line.png'), bbox_inches='tight', dpi=300)
            plt.close(fig1b)
            
            # 1c. 柱状图
            fig1c, ax1c = plt.subplots(figsize=(12, 6))
            plot_bar_chart(ax1c, all_profiles, ['PVQ_Similarity', 'Situational_Similarity'],
                          f'Convergent Validity: PVQ vs. Situational - {model_name} (Bar)', RADAR_Y_RANGE)
            plt.savefig(os.path.join(output_dir, '1c_validity_bar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig1c)
            
            # 1d. 倾向性对比柱状图（新增）
            fig1d, ax1d = plt.subplots(figsize=(12, 6))
            plot_tendency_comparison_bar(ax1d, all_profiles, 'PVQ_Similarity', 'Situational_Similarity',
                                        f'Tendency Comparison: PVQ vs. Situational - {model_name}')
            plt.savefig(os.path.join(output_dir, '1d_tendency_comparison.png'), bbox_inches='tight', dpi=300)
            plt.close(fig1d)
        else:
            print("警告: 缺少'PVQ_Similarity'或'Situational_Similarity'数据，跳过图表一。")


        # --- 图表二: 扰动对“人格画像”（相似度）的影响 ---
        print("--- 正在生成图表二: 相似度画像变化 ---")
        # 2a-1: 情景化雷达图
        fig2a1, ax2a1 = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        lines_1, labels_1 = plot_radar(ax2a1, all_profiles, ['PVQ_Similarity', 'Situational_Similarity'], 'Condition', RADAR_Y_RANGE)
        ax2a1.set_title(f'Effect of Situationalization - {model_name}', size=14, pad=25)
        fig2a1.legend(lines_1, labels_1, loc='upper right', bbox_to_anchor=(1.25, 0.9))
        plt.savefig(os.path.join(output_dir, '2a1_situationalization_radar.png'), bbox_inches='tight', dpi=300)
        plt.close(fig2a1)

        # 2a-2: 压力雷达图
        fig2a2, ax2a2 = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        lines_2, labels_2 = plot_radar(ax2a2, all_profiles, ['Situational_Similarity', 'Pressure_Similarity'], 'Condition', RADAR_Y_RANGE)
        ax2a2.set_title(f'Effect of Pressure - {model_name}', size=14, pad=25)
        fig2a2.legend(lines_2, labels_2, loc='upper right', bbox_to_anchor=(1.25, 0.9))
        plt.savefig(os.path.join(output_dir, '2a2_pressure_radar.png'), bbox_inches='tight', dpi=300)
        plt.close(fig2a2)

        # 2a-3: 视角雷达图 (使用新的价值观倾向性分组)
        fig2a3, ax2a3 = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        if 'Person_Support_Similarity' in all_profiles.columns and 'Person_Oppose_Similarity' in all_profiles.columns:
            lines_c, labels_c = plot_radar(ax2a3, all_profiles, ['Situational_Similarity', 'Person_Support_Similarity', 'Person_Oppose_Similarity'], 'Condition', RADAR_Y_RANGE)
            ax2a3.set_title(f'Effect of Value-Based Perspective - {model_name}', size=14, pad=25)
            fig2a3.legend(lines_c, labels_c, loc='upper right', bbox_to_anchor=(1.25, 0.9))
            plt.savefig(os.path.join(output_dir, '2a3_perspective_radar.png'), bbox_inches='tight', dpi=300)
        else:
            print("警告: 没有找到Person_Support/Person_Oppose数据，跳过2a-3图表")
        plt.close(fig2a3)
        plt.close(fig2a3)

        # 2b. 折线图版本 - 拆分为三个独立的图
        # 2b-1: 情景化折线图
        fig2b1, ax2b1 = plt.subplots(figsize=(12, 6))
        plot_line_chart(ax2b1, all_profiles, ['PVQ_Similarity', 'Situational_Similarity'], f'Situationalization Effect - {model_name}', RADAR_Y_RANGE)
        plt.savefig(os.path.join(output_dir, '2b1_situationalization_line.png'), bbox_inches='tight', dpi=300)
        plt.close(fig2b1)

        # 2b-2: 压力折线图
        fig2b2, ax2b2 = plt.subplots(figsize=(12, 6))
        plot_line_chart(ax2b2, all_profiles, ['Situational_Similarity', 'Pressure_Similarity'], f'Pressure Effect - {model_name}', RADAR_Y_RANGE)
        plt.savefig(os.path.join(output_dir, '2b2_pressure_line.png'), bbox_inches='tight', dpi=300)
        plt.close(fig2b2)

        # 2b-2H: 压力扰动柱状图 - 显示各维度相对于情景化的变化
        if 'Situational_Similarity' in all_profiles.columns and 'Pressure_Similarity' in all_profiles.columns:
            fig2b2h, ax2b2h = plt.subplots(figsize=(12, 6))
            plot_pressure_perturbation_bar(ax2b2h, all_profiles, f'Pressure vs Situational: Change by Value Dimension - {model_name}')
            plt.savefig(os.path.join(output_dir, '2b2h_pressure_change_bar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig2b2h)

            # 2b-2H-Stats: 压力扰动统计显著性检验
            print("--- 正在计算压力扰动统计显著性检验 ---")
            pressure_stats = calculate_pressure_perturbation_statistics(df_perturb, all_profiles, ci_level=0.95, n_bootstrap=1000)
            if not pressure_stats.empty:
                generate_pressure_statistics_report(pressure_stats, output_dir, model_name)

        # 2b-3: 视角折线图 (使用新的价值观倾向性分组)
        fig2b3, ax2b3 = plt.subplots(figsize=(12, 6))
        if 'Person_Support_Similarity' in all_profiles.columns and 'Person_Oppose_Similarity' in all_profiles.columns:
            plot_line_chart(ax2b3, all_profiles, ['Situational_Similarity', 'Person_Support_Similarity', 'Person_Oppose_Similarity'], f'Value-Based Perspective Effect - {model_name}', RADAR_Y_RANGE)
            plt.savefig(os.path.join(output_dir, '2b3_perspective_line.png'), bbox_inches='tight', dpi=300)
        else:
            print("警告: 没有找到Person_Support/Person_Oppose数据，跳过2b-3图表")
        plt.close(fig2b3)

        # --- 图表三: 扰动对“情感态度”（效价）的影响 ---
        print("--- 正在生成图表三: 情感效价变化 ---")
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        fig3.suptitle(f'3. The Impact of Perturbations on Valence (Attitude) - Framing Effect ({model_name})', fontsize=16)
        
        # 子图3a: 框架效应（仅保留左边子图）
        required_framing_cols = ['Positive_Frame_Valence', 'Negative_Frame_Valence']
        if all(col in all_profiles.columns for col in required_framing_cols):
            framing_valence_data = all_profiles.reindex(VALUES)[required_framing_cols].rename(
                columns={'Positive_Frame_Valence': 'Positive Frame', 'Negative_Frame_Valence': 'Negative Frame'})
            framing_valence_data.plot(kind='bar', ax=ax3, color=['#2ecc71', '#e74c3c'])
            ax3.set_title(f'Effect of Framing - {model_name}', size=14)
            ax3.set_ylabel('Average Valence Score')
            ax3.axhline(0, color='black', linewidth=0.8)
            ax3.tick_params(axis='x', rotation=45, labelsize=10)
            ax3.set_ylim(VALENCE_Y_RANGE)
        else:
            ax3.text(0.5, 0.5, 'Framing data not available\nin the provided CSV file.', ha='center', va='center', fontsize=12)
            ax3.set_title(f'Effect of Framing (No Data) - {model_name}', size=14)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '3a_valence_bar.png'), bbox_inches='tight', dpi=300)
        plt.close(fig3)
        
        # 保存框架效应效价数据到 CSV
        if all(col in all_profiles.columns for col in required_framing_cols):
            framing_csv_data = all_profiles.reindex(VALUES)[required_framing_cols].copy()
            framing_csv_data.index.name = 'Value'
            framing_csv_data['Difference'] = framing_csv_data['Positive_Frame_Valence'] - framing_csv_data['Negative_Frame_Valence']
            framing_csv_data['Model'] = model_name
            framing_csv_path = os.path.join(output_dir, '3a_valence_framing_data.csv')
            framing_csv_data.to_csv(framing_csv_path, encoding='utf-8-sig')
            print(f"  [OK] 框架效应效价数据已保存到: {framing_csv_path}")

        # 3b. 折线图版本的效价分析
        if all(col in all_profiles.columns for col in required_framing_cols):
            fig3b, ax3b = plt.subplots(figsize=(12, 6))
        plot_line_chart(ax3b, all_profiles, required_framing_cols, 
            '3b. Framing Effect on Valence (Line Chart)', VALENCE_Y_RANGE)
        plt.savefig(os.path.join(output_dir, '3b_valence_line.png'), bbox_inches='tight', dpi=300)
        plt.close(fig3b)

        # --- 图表四: 施瓦茨价值观四大类分析 ---
        print("--- 正在生成图表四: 施瓦茨价值观四大类分析 ---")
        
        # 计算四大类聚合分数
        category_profiles = calculate_schwartz_categories_profiles(all_profiles)
        
        # 4a. 方法验证 - 四大类雷达图
        if 'PVQ_Similarity' in category_profiles.columns and 'Situational_Similarity' in category_profiles.columns:
            fig4a, ax4a = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            lines, labels = plot_schwartz_radar(ax4a, category_profiles, 
                                              ['PVQ_Similarity', 'Situational_Similarity'],
                                              f'Schwartz Categories: PVQ vs Situational - {model_name} (Radar)', RADAR_Y_RANGE)
            fig4a.legend(lines, labels, loc='upper right', bbox_to_anchor=(1.25, 0.9))
            plt.savefig(os.path.join(output_dir, '4a_schwartz_categories_radar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig4a)
        
        # 4a-S. "重心漂移"专题可视化 - 突出核心发现 (蝴蝶对比图)
        if 'Baseline_Similarity' in category_profiles.columns and 'Situational_Similarity' in category_profiles.columns:
            fig4as, ax4as = plt.subplots(figsize=(12, 8))
            # 调整子图位置，为轴标签留出空间
            plt.subplots_adjust(top=0.9, bottom=0.2)
            plot_value_shift_analysis(ax4as, category_profiles, 
                                    '4a-S. Value System "Center of Gravity" Shift: From Theoretical Ideals to Practical Problem-Solving')
            plt.savefig(os.path.join(output_dir, '4as_value_shift_analysis.png'), bbox_inches='tight', dpi=300)
            plt.close(fig4as)
            
        # 4a-R. 重力偏移雷达图 - 另一种美观呈现
        if 'PVQ_Similarity' in category_profiles.columns and 'Situational_Similarity' in category_profiles.columns:
            fig4ar, ax4ar = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            plot_gravity_shift_radar(ax4ar, category_profiles, 
                                   f'Value System Gravity Shift: Dual-Layer Radar - {model_name}')
            plt.savefig(os.path.join(output_dir, '4ar_gravity_shift_radar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig4ar)
        
        # 4b. 扰动影响 - 四大类折线图 (使用新的价值观倾向性分组)
        fig4b, ax4b = plt.subplots(figsize=(12, 6))
        available_similarity_cols = [col for col in ['PVQ_Similarity', 'Situational_Similarity', 
                                                   'Pressure_Similarity', 'Person_Support_Similarity', 
                                                   'Person_Oppose_Similarity'] if col in category_profiles.columns]
        
        plot_schwartz_line(ax4b, category_profiles, available_similarity_cols,
                          f'Schwartz Categories Perturbation Impact - {model_name}', RADAR_Y_RANGE)
        plt.savefig(os.path.join(output_dir, '4b_schwartz_perturbation_line.png'), bbox_inches='tight', dpi=300)
        plt.close(fig4b)
        
        # 4c. 效价分析 - 四大类柱状图 (包含新的价值观倾向性分组)
        available_valence_cols = [col for col in ['Positive_Frame_Valence', 'Negative_Frame_Valence',
                                                'Situational_Valence', 'Pressure_Valence',
                                                'Person_Support_Valence', 'Person_Oppose_Valence'] if col in category_profiles.columns]
        if available_valence_cols:
            fig4c, ax4c = plt.subplots(figsize=(12, 6))
            plot_schwartz_bar(ax4c, category_profiles, available_valence_cols,
                             f'Schwartz Categories Valence Analysis - {model_name}', VALENCE_Y_RANGE)
            plt.savefig(os.path.join(output_dir, '4c_schwartz_valence_bar.png'), bbox_inches='tight', dpi=300)
            plt.close(fig4c)
        
        # 保存四大类聚合数据
        category_profiles.to_csv(os.path.join(output_dir, f"{model_name}_schwartz_categories_profiles.csv"))
        print("施瓦茨四大类聚合数据已保存。")

        # --- 图表五: 定量分析 ---
        print("--- 正在生成图表五: 扰动效应定量分析 ---")
        
        # 直接使用已经构造好的all_profiles数据进行定量分析
        # all_profiles已经包含了所有需要的相似度数据
        profiles_for_quantitative = all_profiles.copy()
        
        # 计算定量指标
        quantitative_metrics = calculate_quantitative_metrics(profiles_for_quantitative)
        schwartz_quantitative = calculate_schwartz_quantitative_metrics(category_profiles)
        
        # 5a. 变化率热力图
        fig5a, ax5a = plt.subplots(figsize=(14, 8))
        plot_change_rate_heatmap(ax5a, profiles_for_quantitative, '5a. Value Change Rate Heatmap (%)')
        plt.savefig(os.path.join(output_dir, '5a_change_rate_heatmap.png'), bbox_inches='tight', dpi=300)
        plt.close(fig5a)
        
        # 5b. 定量指标四子图摘要
        fig5b, axes5b = plt.subplots(2, 2, figsize=(16, 12))
        fig5b.suptitle(f'Comprehensive Quantitative Analysis - {model_name}', fontsize=16, y=0.95)
        
        # 提取扰动名称
        perturbation_names = []
        for col in quantitative_metrics.columns:
            if 'Coefficient_of_Variation' in col and col != 'Baseline_Coefficient_of_Variation':
                perturbation_names.append(col.replace('_Coefficient_of_Variation', ''))
        
        if perturbation_names:
            # 子图1: 变异系数 (CV)
            cv_data = []
            for name in perturbation_names:
                cv_col = f'{name}_Coefficient_of_Variation'
                if cv_col in quantitative_metrics.columns:
                    cv_data.append(quantitative_metrics[cv_col].iloc[0])
                else:
                    cv_data.append(0)
            
            bars1 = axes5b[0,0].bar(perturbation_names, cv_data, color='skyblue', alpha=0.8)
            axes5b[0,0].set_title('Coefficient of Variation (%)', fontsize=12)
            axes5b[0,0].set_ylabel('CV Value')
            axes5b[0,0].tick_params(axis='x', rotation=45, labelsize=10)
            axes5b[0,0].grid(True, alpha=0.3, axis='y')
            for bar, value in zip(bars1, cv_data):
                axes5b[0,0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(cv_data)*0.01,
                               f'{value:.1f}', ha='center', va='bottom', fontsize=9)
            
            # 子图2: 值域
            range_data = []
            for name in perturbation_names:
                range_col = f'{name}_Value_Range'
                if range_col in quantitative_metrics.columns:
                    range_data.append(quantitative_metrics[range_col].iloc[0])
                else:
                    range_data.append(0)
            
            bars2 = axes5b[0,1].bar(perturbation_names, range_data, color='lightcoral', alpha=0.8)
            axes5b[0,1].set_title('Value Range', fontsize=12)
            axes5b[0,1].set_ylabel('Range Value')
            axes5b[0,1].tick_params(axis='x', rotation=45, labelsize=10)
            axes5b[0,1].grid(True, alpha=0.3, axis='y')
            for bar, value in zip(bars2, range_data):
                axes5b[0,1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(range_data)*0.01,
                               f'{value:.2f}', ha='center', va='bottom', fontsize=9)
            
            # 子图3: 极值比例
            extreme_data = []
            for name in perturbation_names:
                extreme_col = f'{name}_Extreme_Ratio'
                if extreme_col in quantitative_metrics.columns:
                    extreme_data.append(quantitative_metrics[extreme_col].iloc[0])
                else:
                    extreme_data.append(0)
            
            bars3 = axes5b[1,0].bar(perturbation_names, extreme_data, color='lightgreen', alpha=0.8)
            axes5b[1,0].set_title('Extreme Change Ratio (%)', fontsize=12)
            axes5b[1,0].set_ylabel('Extreme Ratio (%)')
            axes5b[1,0].tick_params(axis='x', rotation=45, labelsize=10)
            axes5b[1,0].grid(True, alpha=0.3, axis='y')
            for bar, value in zip(bars3, extreme_data):
                axes5b[1,0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(extreme_data)*0.01,
                               f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
            
            # 子图4: 方向性分析 (正向变化比例)
            direction_data = []
            for name in perturbation_names:
                pos_col = f'{name}_Positive_Changes'
                neg_col = f'{name}_Negative_Changes'
                neu_col = f'{name}_Neutral_Changes'
                
                if all(col in quantitative_metrics.columns for col in [pos_col, neg_col, neu_col]):
                    pos = quantitative_metrics[pos_col].iloc[0]
                    neg = quantitative_metrics[neg_col].iloc[0]
                    neu = quantitative_metrics[neu_col].iloc[0]
                    total = pos + neg + neu
                    pos_ratio = (pos / total * 100) if total > 0 else 0
                    direction_data.append(pos_ratio)
                else:
                    direction_data.append(0)
            
            bars4 = axes5b[1,1].bar(perturbation_names, direction_data, color='gold', alpha=0.8)
            axes5b[1,1].set_title('Positive Change Ratio (%)', fontsize=12)
            axes5b[1,1].set_ylabel('Positive Ratio (%)')
            axes5b[1,1].tick_params(axis='x', rotation=45, labelsize=10)
            axes5b[1,1].grid(True, alpha=0.3, axis='y')
            axes5b[1,1].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Line')
            for bar, value in zip(bars4, direction_data):
                axes5b[1,1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                               f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '5b_quantitative_comprehensive.png'), bbox_inches='tight', dpi=300)
        plt.close(fig5b)
        
        # 5c. 施瓦茨四大类变化分析
        if schwartz_quantitative:
            try:
                fig5c, ax5c = plt.subplots(figsize=(10, 8))
                
                # 准备四大类变化数据
                change_summary = []
                perturbation_names = []
                
                for key, value in schwartz_quantitative.items():
                    if 'Category_Changes' in key:
                        perturbation_name = key.replace('_Category_Changes', '')
                        perturbation_names.append(perturbation_name)
                        if hasattr(value, 'values'):
                            change_summary.append(value.values)
                        else:
                            # 如果是Series，直接使用
                            change_summary.append(list(value))
                
                if change_summary and len(change_summary) > 0:
                    change_matrix = np.array(change_summary)
                    categories = list(SCHWARTZ_CATEGORIES.keys())
                    category_labels = [CATEGORY_NAMES_EN[cat] for cat in categories]
                    
                    im = ax5c.imshow(change_matrix, cmap='RdBu_r', aspect='auto', vmin=-2, vmax=2)
                    ax5c.set_xticks(range(len(categories)))
                    ax5c.set_xticklabels(category_labels, rotation=45, ha='right')
                    ax5c.set_yticks(range(len(perturbation_names)))
                    ax5c.set_yticklabels(perturbation_names)
                    ax5c.set_title(f'Schwartz Categories Change Matrix - {model_name}', fontsize=14, pad=20)
                    
                    # 添加数值标注
                    for i in range(len(perturbation_names)):
                        for j in range(len(categories)):
                            if i < change_matrix.shape[0] and j < change_matrix.shape[1]:
                                text = ax5c.text(j, i, f'{change_matrix[i, j]:.2f}',
                                               ha="center", va="center", 
                                               color="black" if abs(change_matrix[i, j]) < 1 else "white")
                    
                    plt.colorbar(im, ax=ax5c, label='Change Score')
                    plt.savefig(os.path.join(output_dir, '5c_schwartz_change_matrix.png'), bbox_inches='tight', dpi=300)
                    print("图表5c: 施瓦茨类别变化矩阵已保存")
                else:
                    print("警告: 施瓦茨四大类变化数据为空，跳过图表5c")
                plt.close(fig5c)
            except Exception as e:
                print(f"图表5c生成失败: {e}")
                if 'fig5c' in locals():
                    plt.close(fig5c)
        
        # 保存定量分析数据
        quantitative_metrics.to_csv(os.path.join(output_dir, f"{model_name}_quantitative_metrics.csv"))
        
        # 生成定量分析报告
        generate_quantitative_report(profiles_for_quantitative, category_profiles, quantitative_metrics, schwartz_quantitative, output_dir, model_name)
        print("定量分析完成，报告已生成。")

        # --- 图表五补充: 相对地位变化（排名漂移）统计分析 ---
        print("--- 正在生成图表五补充: 价值观排名漂移统计分析 ---")

        # 计算排名变化统计（包括置信区间和效应量）
        ranking_shift_stats = calculate_ranking_shift_statistics(df_perturb, all_profiles, n_bootstrap=1000, ci_level=0.95)

        if not ranking_shift_stats.empty:
            # 生成统计报告
            generate_ranking_shift_summary(ranking_shift_stats, output_dir, model_name)

            # 生成单一综合排名变化统计CSV
            if len(ranking_shift_stats) > 0:
                viz_data = ranking_shift_stats.copy()

                # 添加可视化辅助列
                viz_data['effect_size_category'] = viz_data['cohens_d'].apply(
                    lambda d: 'Negligible' if abs(d) < 0.2 else ('Small' if abs(d) < 0.5 else ('Medium' if abs(d) < 0.8 else 'Large'))
                )

                # 显著性标记（使用Wilcoxon p-value）
                p_col = 'wilcoxon_p_value' if 'wilcoxon_p_value' in viz_data.columns else 'p_value'
                viz_data['significance_marker'] = viz_data[p_col].apply(
                    lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
                )

                # 显著性分类
                viz_data['significance_level'] = viz_data[p_col].apply(
                    lambda p: 'p<0.001' if p < 0.001 else ('p<0.01' if p < 0.01 else ('p<0.05' if p < 0.05 else 'n.s.'))
                )

                # 排序（按比较条件，然后按排名变化量排序）
                rank_diff_col = 'rank_difference' if 'rank_difference' in viz_data.columns else 'ranking_shift'
                viz_data = viz_data.sort_values(['comparison', rank_diff_col])

                # 添加排名变化大小排名
                viz_data['rank_shift_severity'] = viz_data[rank_diff_col].abs().rank(ascending=False).astype(int)

                # 选择并重命名列（精简版）
                output_cols = {
                    'comparison': 'Comparison',
                    'comparison_label': 'Comparison Label',
                    'value_dimension': 'Value Dimension',
                    # 原始分数
                    'baseline_mean_score': 'Baseline Score',
                    'perturbation_mean_score': 'Perturbation Score',
                    'score_difference': 'Score Diff',
                    # 排名（核心指标）
                    'baseline_rank': 'Baseline Rank',
                    'perturbation_rank': 'Perturbation Rank',
                    'rank_difference': 'Rank Diff',
                    # 统计检验
                    'n_baseline': 'N1',
                    'n_perturbation': 'N2',
                    'cohens_d': "Cohen's d",
                    'effect_size_category': 'Effect Size',
                    'wilcoxon_p_value': 'p-value',
                    'wilcoxon_significance': 'Sig Level',
                    'significance_marker': 'Sig',
                    # 置信区间
                    'ci_lower': 'CI Lower',
                    'ci_upper': 'CI Upper',
                    'ci_level': 'CI Level',
                    # 排名稳定性
                    'spearman_r': 'Spearman r',
                    'top3_overlap': 'Top-3 Overlap',
                    # 变化方向
                    'shift_direction': 'Shift Direction',
                    'rank_shift_severity': 'Shift Severity'
                }

                # 过滤存在的列
                available_cols = [col for col in output_cols.keys() if col in viz_data.columns]
                viz_data_final = viz_data[available_cols].rename(columns={k: v for k, v in output_cols.items() if k in available_cols})

                # 保存单一综合CSV
                combined_viz_csv_path = os.path.join(output_dir, f"{model_name}_ranking_shift_statistics.csv")
                viz_data_final.to_csv(combined_viz_csv_path, index=False, encoding='utf-8-sig')
                print(f"  [OK] 排名变化统计表已保存到: {combined_viz_csv_path}")
                print("排名变化统计分析完成。")
        else:
            print("  警告: 无法计算排名变化统计，数据不足")

        # --- 附录: 分情景详细图 ---
        print("--- 正在生成附录: 分情景视角扰动详细图 ---")
        print("  附录图表生成已暂时禁用以避免保存问题")
        # 注释掉附录部分，避免保存问题
        # 附录代码如下（暂时禁用）:
        details_dir = os.path.join(output_dir, "appendix_perspective_details")
        if not os.path.exists(details_dir): os.makedirs(details_dir)
        
        for sid in sorted(df_perturb['scenario_id'].unique()):
            df_scenario = df_perturb[df_perturb['scenario_id'] == sid]
            
            if len(df_scenario) > 0:
                # 传入空的pvq_df，因为我们不需要基准，只计算这个情景下的扰动画像
                profiles_scenario_dict = calculate_profiles(df_scenario, pd.DataFrame())
                profiles_scenario_df = pd.DataFrame(profiles_scenario_dict)

                required_groups = ['Situational_Similarity', 'Person_Support_Similarity', 'Person_Oppose_Similarity']
                
                if all(group in profiles_scenario_df.columns for group in required_groups):
                    fig_detail, ax_detail = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                    lines_d, labels_d = plot_radar(ax_detail, profiles_scenario_df, required_groups, 'Condition', RADAR_Y_RANGE)
                    scenario_name = df_scenario['scenario_name'].iloc[0]
                    ax_detail.set_title(f'Value-Based Perspective Effect in Scenario {sid} - {model_name}\n({scenario_name})', size=12, pad=20)
                    fig_detail.legend(lines_d, labels_d, loc='upper right', bbox_to_anchor=(1.3, 0.9))
                    try:
                        plt.savefig(os.path.join(details_dir, f'appendix_s{sid}_perspective.png'), bbox_inches='tight', dpi=300)
                        plt.close(fig_detail)
                    except Exception as e:
                        print(f"  保存情景 {sid} 图表时出错: {e}")
                        plt.close(fig_detail)
                else:
                    print(f"  跳过情景 {sid} 的详细图，因为缺少必要的分组数据。")
            else:
                print(f"  情景 {sid} 没有有效数据，跳过。")
        
        print(f"\n[SUCCESS] 模型 {model_name} 的所有图表已生成完毕。")
        print(f"          输出目录: {output_dir}")
    
    print("\n" + "="*80)
    print("[COMPLETE] 批量评估完成！")
    print("="*80)

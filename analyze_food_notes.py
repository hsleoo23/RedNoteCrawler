import pandas as pd
from openai import OpenAI
import json
from datetime import datetime
import os

# 设置OpenAI API配置
api_key = "sk-tliYGi4663Ft6vGp45B5CbAe7b4645648dC1A0FdF2908d60"
api_base = "https://oneapi-ai.fdsm.fudan.edu.cn/v1"
client = OpenAI(api_key=api_key, base_url=api_base)

def save_to_excel(analysis_result: str, output_file: str):
    """将分析结果保存为Excel格式"""
    try:
        # 预处理JSON字符串
        analysis_result = analysis_result.replace("```json", "").replace("```", "").strip()
        
        # 解析JSON结果
        try:
            data = json.loads(analysis_result)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            return
        
        # 准备成分分析数据
        ingredients_data = []
        for ingredient in data["成分分析"]:
            heat_data = ingredient["热度数据"]
            # 将热门笔记列表转换为字符串，用分号分隔
            hot_notes = "；".join(heat_data["热门笔记"])
            
            row_data = {
                "食品名称": ingredient["食品名称"],
                "出现次数": ingredient["出现次数"],
                "平均点赞数": round(heat_data["平均点赞数"], 2),
                "平均收藏数": round(heat_data["平均收藏数"], 2),
                "平均评论数": round(heat_data["平均评论数"], 2),
                "平均分享数": round(heat_data["平均分享数"], 2),
                "热度排名": heat_data["热度排名"],
                "热门笔记": hot_notes,
            }
            ingredients_data.append(row_data)
        
        # 创建成分分析DataFrame
        ingredients_df = pd.DataFrame(ingredients_data)
        ingredients_df = ingredients_df.sort_values("热度排名")
        
        # 准备总体分析数据
        overall_analysis = data["总体分析"]
        overall_data = pd.DataFrame({
            "热门成分排名": [", ".join(overall_analysis["热门成分排名"])],
            "成分使用趋势": [overall_analysis["成分使用趋势"]]
        })
        
        try:
            # 保存为Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 保存成分分析
                ingredients_df.to_excel(writer, sheet_name='成分分析', index=False)
                # 保存总体分析
                overall_data.to_excel(writer, sheet_name='总体分析', index=False)
                
                # 调整列宽
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for idx, col in enumerate(worksheet.columns):
                        max_length = 0
                        for cell in col:
                            if cell.value:
                                try:
                                    max_length = max(max_length, len(str(cell.value)))
                                except:
                                    pass
                        # 设置列宽，最大50
                        worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            print(f"Excel文件已保存：{output_file}")
            
        except Exception as e:
            print(f"保存Excel文件时出错: {str(e)}")
            # 尝试使用备用方法保存
            try:
                print("尝试使用备用方法保存...")
                ingredients_df.to_excel(output_file.replace('.xlsx', '_成分分析.xlsx'), index=False)
                overall_data.to_excel(output_file.replace('.xlsx', '_总体分析.xlsx'), index=False)
                print("已分别保存成分分析和总体分析文件")
            except Exception as e2:
                print(f"备用保存方法也失败: {str(e2)}")
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        print("\n原始数据：")
        print(analysis_result)

def analyze_multiple_notes(input_files: list):
    """使用OpenAI分析多个小红书笔记数据文件
    Args:
        input_files: Excel文件路径列表
    """
    try:
        # 计算每个文件需要处理的数据量
        notes_per_file = 280 // len(input_files)
        print(f"每个文件将处理 {notes_per_file} 条数据")
        
        # 合并所有文件的数据
        all_notes_data = []
        for input_file in input_files:
            # 读取Excel文件
            df = pd.read_excel(input_file)
            print(f"成功读取文件：{input_file}")
            
            # 计算互动量（点赞数+收藏数）
            df['互动量'] = df['点赞数量'] + df['收藏数量']
            
            # 按互动量排序并选择指定数量的数据
            df_sorted = df.sort_values('互动量', ascending=False).head(notes_per_file)
            print(f"从文件 {input_file} 中选择互动量最高的 {notes_per_file} 条数据")
            
            # 准备数据
            for _, row in df_sorted.iterrows():
                try:
                    note = {
                        "标题": str(row["标题"]),
                        "描述": str(row["描述"]),
                        "点赞数量": int(row["点赞数量"]),
                        "收藏数量": int(row["收藏数量"]),
                        "评论数量": int(row["评论数量"]),
                        "分享数量": int(row["分享数量"])
                    }
                    all_notes_data.append(note)
                except Exception as e:
                    print(f"处理行数据时出错: {str(e)}")
                    continue
        
        print(f"成功处理 {len(all_notes_data)} 条笔记数据")
        
        # 构建提示词
        prompt = f"""作为一个专业的营养学专家，请分析以下小红书笔记数据，提取化妆品成分并分析其热度。
        
        数据格式说明：
        每条笔记包含：标题、描述、点赞数、收藏数、评论数、分享数
        
        请完成以下任务：
        1. 从每条笔记的标题和描述中提取化妆品成分关键词
        2. 分析每个成分的热度，必须包含以下具体数据：
           - 该成分在多少篇笔记中出现（出现频率）
           - 含有该成分的笔记平均点赞数
           - 含有该成分的笔记平均收藏数
           - 含有该成分的笔记平均评论数
           - 含有该成分的笔记平均分享数
           - 该成分相关笔记中互动量最高的前3篇笔记标题
        3. 对成分进行热度排名（根据平均互动量）
        
        笔记数据：
        {json.dumps(all_notes_data, ensure_ascii=False, indent=2)}
        
        请以JSON格式返回分析结果，格式如下：
        {{
            "成分分析": [
                {{
                    "成分名称": "成分名",
                    "出现次数": 数字,
                    "热度数据": {{
                        "平均点赞数": 数字,
                        "平均收藏数": 数字,
                        "平均评论数": 数字,
                        "平均分享数": 数字,
                        "热度排名": 数字,
                        "热门笔记": [
                            "笔记标题1",
                            "笔记标题2",
                            "笔记标题3"
                            每个笔记标题之间用；分割
                        ]
                    }},
              
                }}
            ],
            "总体分析": {{
                "热门成分排名": ["成分1", "成分2", "成分3"],
            
            }}
        }}
        """
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个专业的营养师，擅长从社交媒体数据中提取和分析低卡甜品信息。请确保分析结果包含具体的数据支持。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # 获取分析结果
        analysis_result = response.choices[0].message.content
        
        # 生成输出文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d")
        output_file = f"datas/analysis_results/多文件分析_{timestamp}.xlsx"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 保存为Excel
        save_to_excel(analysis_result, output_file)
        print("输出成功")
        
    except Exception as e:
        print(f"分析过程出错: {str(e)}")

def main():
    try:
        # 可以传入多个文件进行分析
        input_files = [
            "datas/excel_datas/低卡甜品.xlsx",
            "datas/excel_datas/减脂期甜品.xlsx"  # 添加更多文件
        ]
        analyze_multiple_notes(input_files)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main() 
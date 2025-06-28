import logging
import os
import pandas as pd
from common.deepseek import generate_text

# 获取excel_tools应用的logger
logger = logging.getLogger("excel_tools")


def validate_file_upload(uploaded_file):
    """
    验证上传的文件

    Args:
        uploaded_file: 上传的文件对象

    Returns:
        tuple: (is_valid, error_message)
    """
    # 检查文件大小（限制为10MB）
    if uploaded_file.size > 10 * 1024 * 1024:
        logger.warning("文件大小超过限制: %s bytes", uploaded_file.size)
        return False, "文件大小不能超过10MB"

    # 检查文件类型（只允许Excel文件）
    allowed_extensions = [".xlsx", ".xls"]
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    if file_extension not in allowed_extensions:
        logger.warning("不支持的文件类型: %s", file_extension)
        return False, "只支持Excel文件格式(.xlsx, .xls)"

    return True, None


def read_excel_file(uploaded_file):
    """
    读取Excel文件内容

    Args:
        uploaded_file: 上传的文件对象

    Returns:
        pandas.DataFrame: Excel数据
    """
    uploaded_file.seek(0)  # 重置文件指针到开始位置
    excel_data = pd.read_excel(uploaded_file)
    logger.info("Excel文件读取成功，数据形状: %s", excel_data.shape)
    return excel_data


def extract_product_descriptions(excel_data):
    """
    从Excel数据中提取产品描述

    Args:
        excel_data: pandas DataFrame对象

    Returns:
        list: 产品描述列表
    """
    try:
        # 读取F列从第17行开始的所有数据（排除17F）
        product_descriptions = excel_data.iloc[16:, 5].dropna().tolist()
        logger.info(
            "从17F单元格以下读取到Product Description数据，共%d条记录",
            len(product_descriptions),
        )
        logger.info("Product Description数据: %s", product_descriptions)
        return product_descriptions
    except IndexError:
        logger.error("无法读取17F单元格以下的数据")
        raise ValueError("无法读取17F单元格以下的Product Description数据")


def split_product_descriptions(product_descriptions):
    """
    将产品描述按|分割成列表

    Args:
        product_descriptions: 原始产品描述列表

    Returns:
        list: 分割后的产品描述列表
    """
    product_descriptions_split = []
    for description in product_descriptions:
        description_str = str(description)
        split_items = [
            item.strip() for item in description_str.split("|") if item.strip()
        ]
        product_descriptions_split.append(split_items)

    logger.info("Product Description分割后的数据: %s", product_descriptions_split)
    return product_descriptions_split


def process_descriptions_with_ai(product_descriptions_split):
    """
    使用AI处理产品描述数据

    Args:
        product_descriptions_split: 分割后的产品描述列表

    Returns:
        list: AI处理后的产品描述列表
    """
    try:
        # 构建提示词
        prompt = f"""
请分析以下产品描述数据，返回你认为必要的产品描述。
要求：
1. 保持原有的格式（用|分隔）
2. 只返回处理后的结果，不要附带其他说明
3. 去除重复、冗余或不必要的信息
4. 保留核心的产品特征和关键信息

原始数据：
{product_descriptions_split}

请直接返回处理后的结果：
"""

        # 调用DeepSeek API
        processed_result = generate_text(
            prompt=prompt,
            model="deepseek-chat",
            temperature=0.3,  # 使用较低的温度以获得更稳定的结果
            max_tokens=2000,
        )

        # 解析返回的结果
        processed_result = _parse_ai_response(processed_result)

        logger.info("DeepSeek处理后的产品描述: %s", processed_result)
        return processed_result

    except Exception as e:
        logger.error("DeepSeek处理产品描述失败: %s", str(e))
        # 如果处理失败，返回原始数据
        logger.info("使用原始产品描述数据")
        return product_descriptions_split


def _parse_ai_response(processed_result):
    """
    解析AI返回的结果

    Args:
        processed_result: AI返回的原始结果

    Returns:
        list: 解析后的产品描述列表
    """
    # 去除可能的markdown格式和多余的空行
    processed_result = processed_result.strip()
    if processed_result.startswith("```"):
        processed_result = processed_result.split("\n", 1)[1]
    if processed_result.endswith("```"):
        processed_result = processed_result.rsplit("\n", 1)[0]

    # 将结果转换回列表格式
    processed_descriptions = []
    for line in processed_result.split("\n"):
        line = line.strip()
        if line:
            # 如果行包含|分隔符，按|分割；否则作为单个项目
            if "|" in line:
                items = [item.strip() for item in line.split("|") if item.strip()]
                processed_descriptions.append(items)
            else:
                processed_descriptions.append([line])

    return processed_descriptions


def build_excel_info(excel_data, product_descriptions_split, processed_descriptions):
    """
    构建Excel信息字典

    Args:
        excel_data: pandas DataFrame对象
        product_descriptions_split: 分割后的产品描述列表
        processed_descriptions: AI处理后的产品描述列表

    Returns:
        dict: Excel信息字典
    """
    return {
        "total_rows": len(excel_data),
        "total_columns": len(excel_data.columns),
        "product_descriptions": product_descriptions_split,
        "product_descriptions_ai": processed_descriptions,
        "product_descriptions_count": len(product_descriptions_split),
    }

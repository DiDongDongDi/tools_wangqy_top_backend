import logging
import os

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Create your views here.


# 获取excel_tools应用的logger
logger = logging.getLogger("excel_tools")


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """
    文件上传视图函数
    接收POST请求，处理文件上传
    """

    try:
        logger.info("开始处理文件上传请求")
        logger.info("请求文件信息: %s", request.FILES)

        # 检查是否有文件在请求中
        if "file" not in request.FILES:
            logger.warning("请求中没有找到文件")
            return JsonResponse({"success": False, "message": "没有找到上传的文件"}, status=400)

        uploaded_file = request.FILES["file"]
        logger.info("接收到文件: %s, 大小: %s bytes", uploaded_file.name, uploaded_file.size)

        # 检查文件大小（限制为10MB）
        if uploaded_file.size > 10 * 1024 * 1024:
            logger.warning("文件大小超过限制: %s bytes", uploaded_file.size)
            return JsonResponse(
                {"success": False, "message": "文件大小不能超过10MB"}, status=400
            )

        # 检查文件类型（只允许Excel文件）
        allowed_extensions = [".xlsx", ".xls"]
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension not in allowed_extensions:
            logger.warning("不支持的文件类型: %s", file_extension)
            return JsonResponse(
                {"success": False, "message": "只支持Excel文件格式(.xlsx, .xls)"},
                status=400,
            )

        # # 保存文件到媒体目录
        # file_path = default_storage.save(
        #     f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read())
        # )
        # logger.info("文件已保存到: %s", file_path)

        # 读取Excel文件内容
        # 重新读取文件内容用于解析
        uploaded_file.seek(0)  # 重置文件指针到开始位置
        excel_data = pd.read_excel(uploaded_file)
        logger.info("Excel文件读取成功，数据形状: %s", excel_data.shape)

        # 获取基本信息
        # 从17F单元格以下读取Product Description数据
        try:
            # 读取F列从第17行开始的所有数据（排除17F）
            product_descriptions = (
                excel_data.iloc[16:, 5].dropna().tolist()
            )  # 17行开始F列，去除空值
            logger.info(
                "从17F单元格以下读取到Product Description数据，共%d条记录", len(product_descriptions)
            )
            logger.info("Product Description数据: %s", product_descriptions)

        except IndexError:
            logger.error("无法读取17F单元格以下的数据")
            return JsonResponse(
                {
                    "success": False,
                    "message": "无法读取17F单元格以下的Product Description数据",
                },
                status=400,
            )

        # 将每个Product Description按|分割成列表
        product_descriptions_split = []
        for description in product_descriptions:
            description_str = str(description)
            split_items = [
                item.strip() for item in description_str.split("|") if item.strip()
            ]
            product_descriptions_split.append(split_items)

        logger.info("Product Description分割后的数据: %s", product_descriptions_split)

        # 将数据添加到返回的excel_info中
        excel_info = {
            "total_rows": len(excel_data),
            "total_columns": len(excel_data.columns),
            "product_descriptions": product_descriptions_split,
            "product_descriptions_count": len(product_descriptions_split),
        }

        return JsonResponse(
            {
                "success": True,
                "message": "文件上传成功",
                "file_name": uploaded_file.name,
                "file_size": uploaded_file.size,
                "excel_info": excel_info,
            }
        )

    except Exception as e:
        logger.error("文件上传处理失败: %s", str(e), exc_info=True)
        return JsonResponse(
            {"success": False, "message": f"文件上传失败: {str(e)}"}, status=500
        )

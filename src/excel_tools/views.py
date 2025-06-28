from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import logging

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
            return JsonResponse(
                {"success": False, "message": "没有找到上传的文件"}, status=400
            )

        uploaded_file = request.FILES["file"]
        logger.info(
            "接收到文件: %s, 大小: %s bytes", uploaded_file.name, uploaded_file.size
        )

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

        # 保存文件到媒体目录
        file_path = default_storage.save(
            f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read())
        )
        logger.info("文件已保存到: %s", file_path)

        # 读取Excel文件内容
        # 重新读取文件内容用于解析
        uploaded_file.seek(0)  # 重置文件指针到开始位置
        excel_data = pd.read_excel(uploaded_file)
        logger.info("Excel文件读取成功，数据形状: %s", excel_data.shape)

        # 获取基本信息
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        total_rows = len(excel_data)
        total_columns = len(excel_data.columns)

        # 获取前5行数据作为预览
        preview_data = excel_data.head().to_dict("records")

        # 获取列名
        column_names = excel_data.columns.tolist()

        logger.info(
            "文件处理完成，工作表数量: %s, 行数: %s, 列数: %s",
            len(sheet_names),
            total_rows,
            total_columns,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "文件上传成功",
                "file_path": file_path,
                "file_name": uploaded_file.name,
                "file_size": uploaded_file.size,
                "excel_info": {
                    "sheet_names": sheet_names,
                    "total_rows": total_rows,
                    "total_columns": total_columns,
                    "column_names": column_names,
                    "preview_data": preview_data,
                },
            }
        )

    except Exception as e:
        logger.error("文件上传处理失败: %s", str(e), exc_info=True)
        return JsonResponse(
            {"success": False, "message": f"文件上传失败: {str(e)}"}, status=500
        )

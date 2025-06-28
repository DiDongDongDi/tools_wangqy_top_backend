import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .common import (
    validate_file_upload,
    read_excel_file,
    extract_product_descriptions,
    split_product_descriptions,
    process_descriptions_with_ai,
    build_excel_info,
)

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
            return JsonResponse(
                {"success": False, "message": "没有找到上传的文件"}, status=400
            )

        uploaded_file = request.FILES["file"]
        logger.info(
            "接收到文件: %s, 大小: %s bytes", uploaded_file.name, uploaded_file.size
        )

        # 验证文件
        is_valid, error_message = validate_file_upload(uploaded_file)
        if not is_valid:
            return JsonResponse(
                {"success": False, "message": error_message}, status=400
            )

        # 读取Excel文件
        excel_data = read_excel_file(uploaded_file)

        # 提取产品描述
        product_descriptions = extract_product_descriptions(excel_data)

        # 分割产品描述
        product_descriptions_split = split_product_descriptions(product_descriptions)

        # 使用AI处理产品描述
        processed_descriptions = process_descriptions_with_ai(
            product_descriptions_split
        )

        # 构建返回信息
        excel_info = build_excel_info(
            excel_data, product_descriptions_split, processed_descriptions
        )

        return JsonResponse(
            {
                "success": True,
                "message": "文件上传成功",
                "file_name": uploaded_file.name,
                "file_size": uploaded_file.size,
                "excel_info": excel_info,
            }
        )

    except ValueError as e:
        logger.error("文件处理失败: %s", str(e))
        return JsonResponse({"success": False, "message": str(e)}, status=400)
    except Exception as e:
        logger.error("文件上传处理失败: %s", str(e), exc_info=True)
        return JsonResponse(
            {"success": False, "message": f"文件上传失败: {str(e)}"}, status=500
        )

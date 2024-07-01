from rest_framework import serializers
from django.core.validators import FileExtensionValidator,get_available_image_extensions

class UploadImageSerializer(serializers.Serializer):
    # ImageField会校验上传的文件是否为图片
    image = serializers.ImageField(
        validators=[FileExtensionValidator(get_available_image_extensions())],
        error_messages={'requires':'请上传图片','invalid_image':'请上传正确的图片'},
    )

    def validate_image(self,value):
        # 图片大小单位为字节
        max_size = 5*1024*1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError("图片最大不能超过5MB")
        return value
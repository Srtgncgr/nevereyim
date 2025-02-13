from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Özel hata yönetimi"""
    
    # Önce DRF'nin kendi exception handler'ını çağır
    response = exception_handler(exc, context)
    
    # Hata loglaması
    logger.error(f"Error occurred: {exc}, Context: {context}")
    
    if response is not None:
        error_data = {
            'status_code': response.status_code,
            'detail': response.data,
            'message': str(exc)
        }
        
        # Özel hata mesajları
        if isinstance(exc, ValidationError):
            error_data['type'] = 'validation_error'
            error_data['message'] = 'Geçersiz veri girişi'
            
        elif isinstance(exc, NotFound):
            error_data['type'] = 'not_found'
            error_data['message'] = 'İstenen kaynak bulunamadı'
            
        elif isinstance(exc, PermissionDenied):
            error_data['type'] = 'permission_denied'
            error_data['message'] = 'Bu işlem için yetkiniz yok'
            
        response.data = error_data
        
    return response 
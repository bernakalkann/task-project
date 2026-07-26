import re
from rest_framework.exceptions import ValidationError

def validate_password_policy(password):
    """
    Parola kontrol mekanizması:
    - En az 8 karakter
    - En az 1 rakam
    - En az 1 sembol
    - En az 1 büyük harf
    - En az 1 küçük harf
    """
    if not password or len(password) < 8:
        raise ValidationError("Parola en az 8 karakter olmalıdır.")
    
    if not re.search(r'\d', password):
        raise ValidationError("Parola en az 1 rakam (0-9) içermelidir.")
        
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Parola en az 1 büyük harf içermelidir.")
        
    if not re.search(r'[a-z]', password):
        raise ValidationError("Parola en az 1 küçük harf içermelidir.")
        
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValidationError("Parola en az 1 sembol (!@#$%^&* vb.) içermelidir.")
        
    return password

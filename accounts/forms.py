from django import forms
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'full_name', 'phone', 'city', 'district', 'full_address', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ev, İş vb.'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad Soyad'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5XX XXX XX XX'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şehir'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İlçe'}),
            'full_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tam adres bilgisi'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Telefon numarası formatını kontrol et
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) != 10:
            raise forms.ValidationError('Geçerli bir telefon numarası girin (10 haneli)')
        return phone

class UserInfoForm(forms.ModelForm):
    username = forms.CharField(
        label='Kullanıcı Adı', 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Kullanıcı adınızı girin'
        }),
        help_text='Kullanıcı adınız giriş yaparken kullanılacaktır.'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Adınızı girin'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Soyadınızı girin'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'E-posta adresinizi girin'
            })
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        # Kullanıcı adı için doğrulama
        if len(username) < 3:
            raise forms.ValidationError('Kullanıcı adı en az 3 karakter olmalıdır.')
        
        # Mevcut kullanıcı dışında aynı kullanıcı adı var mı kontrol et
        existing_users = User.objects.exclude(pk=self.instance.pk).filter(username=username)
        if existing_users.exists():
            raise forms.ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
        
        return username

class UserPasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Mevcut Şifre', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Mevcut şifrenizi girin'
        }),
        required=True
    )
    new_password = forms.CharField(
        label='Yeni Şifre', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Yeni şifrenizi girin'
        }),
        required=True
    )
    confirm_password = forms.CharField(
        label='Yeni Şifre Tekrar', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Yeni şifreyi tekrar girin'
        }),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Yeni şifrelerin eşleşmesini kontrol et
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Yeni şifreler eşleşmiyor.')

        return cleaned_data
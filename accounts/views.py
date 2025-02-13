from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Address
from .forms import AddressForm, UserInfoForm, UserPasswordForm
from orders.models import Order

def register_view(request):
    if request.method == 'POST':
        # Form verilerini al
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
                return redirect('accounts:register')
                
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Bu email zaten kullanılıyor.')
                return redirect('accounts:register')
                
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu.')
            return redirect('products:product_list')
        else:
            messages.error(request, 'Şifreler eşleşmiyor.')
            
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Başarıyla giriş yaptınız.')
            return redirect('products:product_list')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
            
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('products:product_list')

@login_required
def profile(request):
    # Kullanıcının siparişlerini ve adreslerini al
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    addresses = Address.objects.filter(user=request.user)
    
    # Kullanıcı bilgileri ve şifre formları
    info_form = UserInfoForm(instance=request.user, initial={
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    })
    password_form = UserPasswordForm()

    context = {
        'orders': orders,
        'addresses': addresses,
        'info_form': info_form,
        'password_form': password_form
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def update_user_info(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı bilgileriniz başarıyla güncellendi.')
            return redirect(request.META.get('HTTP_REFERER', 'accounts:profile') + '#settings')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
            return redirect(request.META.get('HTTP_REFERER', 'accounts:profile') + '#settings')
    return redirect('accounts:profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            # Mevcut şifreyi kontrol et
            if not request.user.check_password(form.cleaned_data['current_password']):
                messages.error(request, 'Mevcut şifreniz yanlış.')
                return redirect(request.META.get('HTTP_REFERER', 'accounts:profile') + '#settings')

            # Yeni şifreyi kaydet
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)  # Oturumu güncel tutmak için
            
            messages.success(request, 'Şifreniz başarıyla değiştirildi.')
            return redirect(request.META.get('HTTP_REFERER', 'accounts:profile') + '#settings')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
            return redirect(request.META.get('HTTP_REFERER', 'accounts:profile') + '#settings')
    return redirect('accounts:profile')

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        print("Form data:", request.POST)  # Debug print
        print("Form is valid:", form.is_valid())  # Debug print
        if not form.is_valid():
            print("Form errors:", form.errors)  # Debug form errors
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Adres başarıyla eklendi.')
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adres başarıyla güncellendi.')
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Adres silindi.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/delete_address.html', {'address': address})

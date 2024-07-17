from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import FileInput
import re
from django.contrib.auth import authenticate
from.models import Loai,SanPham,GioHang,AnhPhu

class RegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên đăng nhập'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên Email'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })

    username = forms.CharField(label='Tài khoản', max_length=30)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Nhập lại mật khẩu', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2 and password1:
                return password2
        raise forms.ValidationError('Mật khẩu không hợp lệ')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Tên người dùng có kí tự đặc biệt')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Tên người dùng đã tồn tại')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('Email đã tồn tại')

    def save(self):
        User.objects.create_user(username=self.cleaned_data['username'], email=self.cleaned_data['email'], password=self.cleaned_data['password1'])

class CustomLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Tên đăng nhập hoặc mật khẩu không chính xác.')
        return cleaned_data
    
class ThemLoaiForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['TenLoai'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên loại'
        })

    TenLoai = forms.CharField(label='Tên loại', max_length=100)
    def clean_TenLoai(self):
        TenLoai = self.cleaned_data['TenLoai']
        try:
            Loai.objects.get(TenLoai=TenLoai)
        except Loai.DoesNotExist:
            return TenLoai
        raise forms.ValidationError("Loại này đã tồn tại")
    def save(self):
        Loai.objects.create(TenLoai = self.cleaned_data['TenLoai'])  

class XoaLoaiForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['loai_id'].widget.attrs.update({
            'class': 'form-select'         
        })

    loai_id = forms.ModelChoiceField(queryset=Loai.objects.all(), label='Chọn loại cần xóa', to_field_name='TenLoai')

    def xoaloai(self):
        ten_loai = self.cleaned_data['loai_id']
        loai = Loai.objects.get(TenLoai=ten_loai)
        if loai.dsSP.exists():
            raise forms.ValidationError("Không thể xóa loại này vì có sản phẩm liên quan.")
        loai.delete()

class SuaLoaiForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ten_loai_moi'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên loại'        
        })

        self.fields['loai_id'].widget.attrs.update({
            'class': 'form-select'         
        })

    loai_id = forms.ModelChoiceField(queryset=Loai.objects.all(), label='Chọn loại cần sửa', to_field_name='TenLoai')
    ten_loai_moi = forms.CharField(label='Tên loại mới', max_length=100)

    def sualoai(self):
        ten_loai_moi = self.cleaned_data['ten_loai_moi']
        loai = self.cleaned_data['loai_id']
        loai.TenLoai = ten_loai_moi
        loai.save()


class ThemSPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['TenSP'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên sản phẩm'        
        })

        self.fields['DonGia'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập giá'        
        })

        self.fields['MoTa'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mô tả sản phẩm',
            'style': 'height: 300px'      
        })

        self.fields['ML'].widget.attrs.update({
            'class': 'form-select'      
        })

        self.fields['GiamGia'].widget.attrs.update({
            'class': 'form-control'     
        })

        self.fields['HinhAnh'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'style': 'height: 10px'
        })

    class Meta:
        model = SanPham
        fields = ["TenSP","DonGia","MoTa","ML", "GiamGia", "HinhAnh"]
        labels = {
            'TenSP': 'Tên sản phẩm',
            'DonGia': 'Đơn giá',
            'MoTa': 'Mô tả',
            'ML': 'Mã loại',
            'GiamGia': 'Giảm giá',
            'HinhAnh': 'Hình ảnh'
        }

class XoaSanPhamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sanpham_id'].widget.attrs.update({
            'class': 'form-select'         
        })

    sanpham_id = forms.ModelChoiceField(queryset=SanPham.objects.all(), label='Chọn sản phẩm cần xóa', to_field_name='TenSP')

    def xoasanpham(self):
        sanpham_id = self.cleaned_data['sanpham_id']
        sanpham = SanPham.objects.get(TenSP=sanpham_id)
        sanpham.delete()

class SuaSPForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['TenSP'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên sản phẩm'        
        })

        self.fields['DonGia'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập giá'        
        })

        self.fields['MoTa'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mô tả sản phẩm',
            'style': 'height: 300px'      
        })

        self.fields['ML'].widget.attrs.update({
            'class': 'form-select'      
        })

        self.fields['GiamGia'].widget.attrs.update({
            'class': 'form-control'     
        })

        self.fields['HinhAnh'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'style': 'height: 10px'
        })

    class Meta:
        model = SanPham
        fields = ["TenSP","DonGia","ML", "GiamGia", 'MoTa', "HinhAnh"]
        labels = {
            'TenSP': 'Tên sản phẩm',
            'DonGia': 'Đơn giá',
            'MoTa': 'Mô tả',
            'ML': 'Mã loại',
            'GiamGia': 'Giảm giá',
            'HinhAnh': 'Hình ảnh'
        }

class ThanhToanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ho_ten'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên người nhận'        
        })

        self.fields['dia_chi'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ nhận'        
        })

        self.fields['so_dien_thoai'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ nhận'        
        })

        self.fields['phuong_thuc_thanh_toan'].widget.attrs.update({
            'class': 'form-select'      
        })

    ho_ten = forms.CharField(label='Họ và tên', max_length=100)
    dia_chi = forms.CharField(label='Địa chỉ')
    so_dien_thoai = forms.IntegerField(label='Số điện thoại')
    phuong_thuc_thanh_toan = forms.ChoiceField(label='Phương thức thanh toán', choices=(
        ('MoMo', 'MoMo'),
        ('credit_card', 'Thẻ tín dụng'),
        ('cod', 'Thanh toán khi nhận hàng'),
    ))

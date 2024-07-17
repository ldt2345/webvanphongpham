from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
import os

# Create your models here.
class Loai(models.Model):
    TenLoai = models.CharField(max_length=100)
    def __str__(self):
        return self.TenLoai

def upload_to_image(instance, filename):
    path = 'static/images'
    filename_base, filename_ext = os.path.splitext(filename)
    return os.path.join(path, f'{filename_base}{filename_ext}')

class DanhGia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    DanhGiaSao = models.IntegerField(default=0)
    BinhLuan = models.TextField(max_length=500)

class SanPham(models.Model):
    ML = models.ForeignKey(Loai, on_delete=models.CASCADE,related_name='dsSP')
    TenSP = models.CharField(max_length=100)
    MoTa = models.TextField()
    DonGia = models.IntegerField()
    GiamGia = models.IntegerField()
    HinhAnh = models.ImageField(upload_to= upload_to_image)
    SLBan = models.IntegerField(default=0)
    danhgia = models.ManyToManyField(DanhGia, related_name='sanphams')
    def __str__(self):
        return self.TenSP
    
    def Tien_sau_giamgia(self):
        fullprice = self.DonGia
        afterdiscount = self.DonGia * self.GiamGia / 100
        return fullprice - afterdiscount
    
    def So_sao(self):
        average_rating = self.danhgia.aggregate(Avg('DanhGiaSao'))['DanhGiaSao__avg']
        return average_rating if average_rating is not None else 0
    
class AnhPhu(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    Anh = models.ImageField(upload_to= upload_to_image)

class GioHang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default='1')

    def __str__(self):
        return f"{self.user.username}'s Vật phẩm - {self.san_pham.TenSP}"
    
    def tong_tien_sp(self):
        so_luong = int(self.so_luong) 
        don_gia = self.san_pham.DonGia
        return so_luong * don_gia
    
class DonHang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ngay_tao = models.DateTimeField(default=timezone.now)

class ThongTinNguoiNhan(models.Model):
    DonHang = models.ForeignKey(DonHang, on_delete=models.CASCADE)
    HoTen = models.CharField(max_length=100)
    DiaChi = models.CharField(max_length=200)
    SDT = models.CharField(max_length=20)
    PTTT = models.CharField(max_length=100)

class ChiTietDonHang(models.Model):
    DonHang = models.ForeignKey(DonHang, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, default=1)
    so_luong = models.IntegerField()

    def tong_tien_sp(self):
        so_luong = int(self.so_luong) 
        don_gia = self.san_pham.DonGia
        return so_luong * don_gia

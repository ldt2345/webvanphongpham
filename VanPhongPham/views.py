from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from .models import SanPham, Loai, GioHang,DonHang, ThongTinNguoiNhan, ChiTietDonHang, AnhPhu, DanhGia
from .forms import RegistrationForm, CustomLoginForm, ThemLoaiForm, XoaLoaiForm, SuaLoaiForm, ThemSPForm, XoaSanPhamForm, SuaSPForm, ThanhToanForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import F
from django.db import models, transaction
from django.core.paginator import Paginator

# Create your views here.
def TrangChu(request):
    # Truy vấn tất cả các sản phẩm
    tat_ca_san_pham = SanPham.objects.all()

    # Sắp xếp các sản phẩm theo giảm dần của trường GiamGia
    san_pham_sap_xep = sorted(tat_ca_san_pham, key=lambda x: x.GiamGia, reverse=True)

    # Lấy 6 sản phẩm có giảm giá cao nhất
    san_pham_khuyen_mai = san_pham_sap_xep[:6]
    
    # Sắp xếp các sản phẩm theo giảm dần của trường SLBan
    san_pham_sap_xep = sorted(tat_ca_san_pham, key=lambda x: x.SLBan, reverse=True)

    # Lấy 6 sản phẩm bán chạy nhất
    san_pham_ban_chay = san_pham_sap_xep[:6]
    
    # Trả về template TrangChu.html với dữ liệu của cả hai loại sản phẩm
    return render(request, "pages/TrangChu.html", {'san_pham_khuyen_mai': san_pham_khuyen_mai, 'san_pham_ban_chay': san_pham_ban_chay})

def blog(request):
    return render(request,'pages/Blog.html')

def lienHe(request):
    return render(request,'pages/LienHe.html')

def giamGia(request):
    return render(request,'pages/GiamGia.html')

def danhgiasanpham(request, sp_id):
    if request.method == 'POST':
        user = request.user
        sanpham = SanPham.objects.get(pk=sp_id)
        danhgia_sao = int(request.POST.get('rating'))
        binhluan = request.POST.get('comment')

        danhgia = DanhGia.objects.create(
            user=user,
            DanhGiaSao=danhgia_sao,
            BinhLuan=binhluan
        )

        sanpham.danhgia.add(danhgia)

        sanpham.save()

def chitiet(request, sp_id):
    sanpham = SanPham.objects.get(id=sp_id)
    danhgia = sanpham.danhgia.all()
    data = {'sanpham': sanpham, 'danhgia': danhgia}

    danhgiasanpham(request, sp_id)

    return render(request,'pages/ChiTiet.html', data)

def Admin_DSSP(request):
    all_products = SanPham.objects.all()
    paginator = Paginator(all_products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/Admin_DSSP.html', {'dm_sanpham': page_obj})

def DSSP(request, ML_id):
    loai = None
    total_results = 0
    query = request.GET.get('q')
    sort_by = request.GET.get('sortby')

    results = SanPham.objects.all()

    # Tìm kiếm theo từ khóa
    if query:
        results = results.filter(Q(TenSP__icontains=query) | Q(MoTa__icontains=query))
        total_results = results.count()
    
    # Nếu không tìm kiếm, hiển thị theo loại sản phẩm (ML_id)
    if not query:
        if ML_id == 0:
            results = SanPham.objects.all()
        else:
            Maloai = get_object_or_404(Loai, pk=ML_id)
            results = Maloai.dsSP.all()
            loai = [Maloai]

    def calculate_discount_price(product):
        return product.DonGia - (product.DonGia * product.GiamGia / 100)

    # Sắp xếp
    if sort_by:
        if sort_by == 'price_min':
            results = sorted(results, key=calculate_discount_price)
        elif sort_by == 'price_max':
            results = sorted(results, key=calculate_discount_price, reverse=True)
        elif sort_by == 'name_asc':
            results = results.order_by('TenSP')
        elif sort_by == 'name_desc':
            results = results.order_by('-TenSP')
        request.session['sort_by'] = sort_by

    # Lấy giá trị cách sắp xếp từ session
    sort_by_session = request.session.get('sort_by')
    if sort_by_session:
        if sort_by_session == 'price_min':
            results = sorted(results, key=calculate_discount_price)
        elif sort_by_session == 'price_max':
            results = sorted(results, key=calculate_discount_price, reverse=True)
        elif sort_by_session == 'name_asc':
            results = results.order_by('TenSP')
        elif sort_by_session == 'name_desc':
            results = results.order_by('-TenSP')


    # Phân trang
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = {
        'loai': loai,
        'results': page_obj, 
        'query': query, 
        'total_results': total_results, 
        'sort_by': sort_by
    }

    return render(request, 'pages/DSSP.html', data)

def list(request):
    loai = Loai.objects.all()
    paginator = Paginator(loai, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'pages/DSLoai.html', {'DM_Loai': page_obj})

def dangKy(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/VanPhongPham/DangNhap')
    return render(request, 'pages/DangKy.html', {'form': form})

def dangXuat(request):
    logout(request)
    return HttpResponseRedirect('/VanPhongPham/TrangChu')

def dangNhap(request):
    return render(request, 'pages/DangNhap.html')

def admin(request):
    return render(request, 'pages/Admin_page.html')

def manual_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if username == 'admin' and password == 'srat0123':
                login(request, user)
                return HttpResponseRedirect('/VanPhongPham/admin_page')  
            else:
                login(request, user)
                return HttpResponseRedirect('/VanPhongPham/TrangChu')     
        else:
            errormessage = "Tài khoản hoặc mật khẩu bị sai"
    return render(request, 'pages/DangNhap.html', {'error_message': errormessage})

def themloai(request):
    form = ThemLoaiForm()
    if request.method == 'POST':
        form = ThemLoaiForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/VanPhongPham/admin_page') 
    return render(request,'pages/ThemLoai.html',{'form':form})

def xoaloai(request):
    if request.method == 'POST':
        form = XoaLoaiForm(request.POST)
        if form.is_valid():
            form.xoaloai()
            return HttpResponseRedirect('/VanPhongPham/admin_page/XoaLoai')
    else:
        form = XoaLoaiForm()
    return render(request, 'pages/XoaLoai.html', {'form': form})


def sualoai(request):
    if request.method == 'POST':
        form = SuaLoaiForm(request.POST)
        if form.is_valid():
            form.sualoai()
            return HttpResponseRedirect('/VanPhongPham/admin_page/SuaLoai')
    else:
        form = SuaLoaiForm()
    return render(request, 'pages/SuaLoai.html', {'form': form})

def themsp(request):
    if request.method == 'POST':
        form = ThemSPForm(request.POST, request.FILES)
        if form.is_valid():
            san_pham = form.save(commit=False)
            san_pham.save()
            files = request.FILES.getlist('Anh')
            for f in files:
                AnhPhu.objects.create(san_pham=san_pham, Anh=f)
            return HttpResponseRedirect('/VanPhongPham/admin_page/ThemSP')
    else:
        form = ThemSPForm()
    return render(request, 'pages/ThemSP.html', {'form': form})

def suasp(request, sp_id):  
    sanpham = get_object_or_404(SanPham, id=sp_id)
    
    if request.method == 'POST':
        form = SuaSPForm(request.POST, request.FILES, instance=sanpham)
        
        if form.is_valid():
            form.save()
            # Xử lý form cho ảnh phụ mới nếu có
            if 'new_image' in request.FILES:
                files = request.FILES.getlist('new_image')
                for f in files:
                    AnhPhu.objects.create(san_pham=sanpham, Anh=f)

            # Xử lý việc xóa ảnh phụ
            if 'delete_images' in request.POST:
                delete_image_ids = request.POST.getlist('delete_images')
                AnhPhu.objects.filter(id__in=delete_image_ids).delete()

            return HttpResponseRedirect('/VanPhongPham/admin_page/SuaSP/' + str(sp_id))
    else:
        form = SuaSPForm(instance=sanpham)
    
    return render(request, 'pages/SuaSP.html', {'form': form, 'sp_id': sp_id, 'sanpham': sanpham})

def xoasanpham(request):
    if request.method == 'POST':
        form = XoaSanPhamForm(request.POST)
        if form.is_valid():
            form.xoasanpham()
            return HttpResponseRedirect('/VanPhongPham/admin_page/XoaSP')
    else:
        form = XoaSanPhamForm()
    return render(request, 'pages/XoaSP.html', {'form': form})

def capnhatsoluongsanpham(request):
    so_luong = GioHang.objects.filter(user=request.user).count()
    request.session['so_luong'] = so_luong

def themvaogiohang(request, sp_id):
    if request.user.is_authenticated:
        sanpham = get_object_or_404(SanPham, id=sp_id)
        quantity = int(request.GET.get('quantity', 1))

        gio_hang, created = GioHang.objects.get_or_create(user=request.user, san_pham=sanpham)
        if not created:
            gio_hang.so_luong += quantity
        else:
            gio_hang.so_luong = quantity
        gio_hang.save()

        capnhatsoluongsanpham(request)

        previous_url = request.META.get('HTTP_REFERER', '/')

        return redirect(previous_url)

    return render(request, "pages/DangNhap.html")


def giohang(request):
    if request.user.is_authenticated:
        gio_hang = GioHang.objects.filter(user=request.user)
        tong_tien = sum(item.tong_tien_sp() for item in gio_hang)
        capnhatsoluongsanpham(request)
        return render(request, 'pages/GioHang.html', {'GioHang': gio_hang, 'tong_tien': tong_tien})

    return render(request, "pages/DangNhap.html")

def xoakhoigiohang(request, giohang_id):
    gio_hang = get_object_or_404(GioHang, id=giohang_id, user=request.user)
    gio_hang.delete()
    capnhatsoluongsanpham(request)
    return HttpResponseRedirect('/VanPhongPham/GioHang')

def thanhtoan(request):
    if request.method == 'POST':
        form = ThanhToanForm(request.POST)
        if form.is_valid():
            ho_ten = form.cleaned_data['ho_ten']
            dia_chi = form.cleaned_data['dia_chi']
            so_dien_thoai = form.cleaned_data['so_dien_thoai']
            phuong_thuc_thanh_toan = form.cleaned_data['phuong_thuc_thanh_toan']
        
            don_hang = DonHang.objects.create(user=request.user)

            gio_hang = GioHang.objects.filter(user=request.user)

            TTNN = ThongTinNguoiNhan.objects.create(
                DonHang=don_hang,
                HoTen=ho_ten,
                DiaChi=dia_chi,
                SDT=so_dien_thoai,
                PTTT=phuong_thuc_thanh_toan
            )

            for item in gio_hang:
                ChiTietDonHang.objects.create(
                    DonHang=don_hang,
                    san_pham=item.san_pham,
                    so_luong=item.so_luong
                )

                SanPham.objects.filter(id=item.san_pham.id).update(SLBan=models.F('SLBan') + item.so_luong)
            gio_hang.delete()
            return HttpResponseRedirect('/VanPhongPham/XacNhan/' + str(don_hang.id))
    else:
        form = ThanhToanForm()

    gio_hang = GioHang.objects.filter(user=request.user)
    tong_tien = sum(item.tong_tien_sp() for item in gio_hang)
    
    return render(request, 'pages/ThanhToan.html', {'form': form, 'GioHang': gio_hang, 'tong_tien': tong_tien})

def xacnhandonhang(request, don_hang_id):
    TTNN = ThongTinNguoiNhan.objects.get(DonHang=don_hang_id)
    return render(request, 'pages/XNDH.html', {'TTNN': TTNN})

def lichsudathang(request):
    don_hang_list = DonHang.objects.filter(user=request.user)
    lich_su_don_hang = []

    for don_hang in don_hang_list:
        # Get the corresponding ThongTinNguoiNhan and ChiTietDonHang for each don_hang
        TTNN = ThongTinNguoiNhan.objects.filter(DonHang=don_hang)
        chi_tiet_don_hang = ChiTietDonHang.objects.filter(DonHang=don_hang)

        # Calculate the total price for each order
        tong_tien = sum(item.tong_tien_sp() for item in chi_tiet_don_hang)

        # Append to the list of orders
        lich_su_don_hang.append({
            'don_hang': don_hang,
            'TTNN': TTNN,
            'tong_tien': tong_tien
        })

    return render(request, 'pages/LichSuDatHang.html', {'lich_su_don_hang': lich_su_don_hang})

def chitietdonhang(request, don_hang_id):
    ctdh = ChiTietDonHang.objects.filter(DonHang=don_hang_id)
    
    return render(request, 'pages/ChiTietDonHang.html', {'ctdh': ctdh})
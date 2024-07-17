from django import template

register = template.Library()

@register.filter
def add_commas(value):
    if not value:
        return value
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    else:
        return "{:,}".format(value)
    
@register.filter
def star_rating(value):
    try:
        value = float(value)  # Chuyển đổi giá trị đầu vào thành số thực
    except (ValueError, TypeError):
        value = 0  # Nếu giá trị không hợp lệ, đặt về 0

    full_stars = int(value)
    half_star = 1 if value - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    return {
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
    }
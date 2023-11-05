from main.models import Category
from django.db.models import Count


def categories_processor(request):
    # Truy vấn và lấy danh sách categories, sau đó thêm vào context
    categories = Category.objects.annotate(post_count=Count('post'))
    return {'categories': categories}

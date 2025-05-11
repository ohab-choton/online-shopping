from .models import Category

#for menu category list
def menu_links(request):
    categories = Category.objects.all()
    return dict(categories=categories)
from django.contrib import admin
from .models import Category,Product,Banner,Variation,ProductVariant
from django.utils.html import format_html

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',  'image_tag')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)

''' class VariationInline(admin.TabularInline): 
    model = Variation
    extra = 1 '''

class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'show_variations', 'category', 'price', 'stock', 'is_available', 'image_tag')

    def show_variations(self, obj):
        from collections import defaultdict
        grouped = defaultdict(list)
        for v in obj.variation_set.all():
            grouped[v.variation_category.capitalize()].append(v.variation_value)
        return format_html("<br>".join(f"<strong>{k}</strong>: {', '.join(v)}" for k, v in grouped.items()))
    


      
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_available')
    # inlines = [VariationInline]

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Product ID detect করার চেষ্টা করবো POST data থেকে
        if request.method == 'POST':
            product_id = request.POST.get('product')
        else:
            product_id = None

        if db_field.name in ['size', 'color'] and product_id:
            try:
                product_id = int(product_id)
                variation_category = 'size' if db_field.name == 'size' else 'color'
                field.queryset = Variation.objects.filter(
                    product_id=product_id,
                    variation_category=variation_category
                )
            except (ValueError, TypeError):
                pass  # fallback to default

        return field

admin.site.register(ProductVariant, ProductVariantAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(Banner)
admin.site.register(Variation)







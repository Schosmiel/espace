from django.contrib import admin
from core.models import Produit, Categorie, Vendeur, Panier, Commande, \
ProduitImages, ProduitReview, LigneCommande, Adresse, Contacts

class ProductImagesAdmin(admin.TabularInline):
	model = ProduitImages

class ProductAdmin(admin.ModelAdmin):
	inlines = [ProductImagesAdmin]
	list_display = ['user', 'title', 'product_image', 'price','category', 'vendeur', 'featured', 'product_status', 'pid']

class CategotyAdmin(admin.ModelAdmin):
	list_display = ['title', 'category_image', 'cid']

class VendorAdmin(admin.ModelAdmin):
	list_display = ['title', 'vendor_image', 'vid']

# Ce sont des implementations de la classe CartOrder et CartOrderItems

class CartOrderAdmin(admin.ModelAdmin):
 	list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status']

class CartOrderItemsAdmin(admin.ModelAdmin):
 	list_display = ['order', 'invoice_no', 'item', 'image', 'qty', 'price', 'total']

# ce sont des implementations de la classe ProductReview et Wishlist



class ProductReviewAdmin(admin.ModelAdmin):
	list_display = ['user', 'produit', 'rating']
	
class WishlistAdmin(admin.ModelAdmin):
	list_display = ['user', 'produit', 'date']

class AddressAdmin(admin.ModelAdmin):
 	list_display = ['user', 'address', 'status']

class ContactUsAdmin(admin.ModelAdmin):
	list_display = ['name', 'email']

admin.site.register(Produit, ProductAdmin)
admin.site.register(Categorie, CategotyAdmin)
admin.site.register(Vendeur, VendorAdmin)
admin.site.register(Panier, CartOrderAdmin)
admin.site.register(Commande, CartOrderItemsAdmin)
admin.site.register(ProduitReview, ProductReviewAdmin)
admin.site.register(LigneCommande, WishlistAdmin)
admin.site.register(Adresse, AddressAdmin)
admin.site.register(Contacts, ContactUsAdmin)

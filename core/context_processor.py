import random
from core.models import Produit, Categorie, Vendeur, Panier, Commande, \
LigneCommande, ProduitImages, ProduitReview, Adresse, Contacts
from blog.models import Post
from django.db.models import Min, Max
from django.contrib import messages
from taggit.models import Tag

import logging

logger = logging.getLogger(__name__)

def core_context(request):
    try:
        categories = Categorie.objects.all()
        vendors = Vendeur.objects.all()
        min_max_price = Produit.objects.aggregate(Min('price'), Max('price'))
        latest_products = Produit.objects.filter(product_status='published').order_by('-date')
        
        wishlist = None
        if request.user.is_authenticated:
            try:
                wishlist = LigneCommande.objects.filter(user=request.user)
            except LigneCommande.DoesNotExist:
                wishlist = None
        
        all_product_tags = Tag.objects.filter(product__isnull=False).distinct()
        random_product_tags = []
        if all_product_tags:
            random_product_tags = random.sample(list(all_product_tags), min(6, len(all_product_tags)))
        
        blog_posts = Post.objects.filter(post_status='published').order_by("-date_created")
        
        cart_total_amount = 0
        if 'cart_data_object' in request.session:
            for product_id, item in request.session['cart_data_object'].items():
                try:
                    price = item['price'].replace(',', '.')  # Remplacer la virgule par un point
                    cart_total_amount += int(item['qty']) * float(price)  # Convertir en float après remplacement
                except ValueError as e:
                    logger.error(f"Error converting price to float: {item['price']} - {e}")
        
        return {
            'categories': categories,
            'vendors': vendors,
            'wishlist': wishlist,
            'min_max_price': min_max_price,
            'cart_total_amount': cart_total_amount,
            'latest_products': latest_products,
            'random_product_tags': random_product_tags,
            'blog_posts': blog_posts,
        }
    except Exception as e:
        logger.error(f"Error in core_context: {e}")
        return {}

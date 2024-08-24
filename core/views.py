from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg, F, ExpressionWrapper, DecimalField
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core import serializers
from core.models import Produit, Categorie, Vendeur, Panier, Commande, \
ProduitImages, ProduitReview, LigneCommande, Adresse, Contacts
from core.forms import ProductReviewFrom
from taggit.models import Tag


def index(request):
	produits = Produit.objects.filter(product_status='published', featured=True)

	special_offers = Produit.objects.filter(product_status='published').annotate(
		discount_percentage=ExpressionWrapper(
			((F('old_price') - F('price')) / F('old_price')) * 100,
			output_field=DecimalField()
		)
    ).order_by('-discount_percentage')[:9]
    
	oldest_products = Produit.objects.filter(product_status='published').order_by('date')

	context = {
		"produits": produits,
		"special_offers": special_offers,
		"oldest_products": oldest_products,
	}
	return render(request, 'core/index.html', context)

def products_list_view(request):
	produits = Produit.objects.filter(product_status='published')
	context = {
		"produits": produits
	}
	return render(request, 'core/product-list.html', context)

def category_list_view(request):
	categories = Categorie.objects.all()
	context = {
		"categories": categories,
	}
	return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
	category = Categorie.objects.get(cid=cid)
	produits = Produit.objects.filter(product_status='published', category=category)
	context = {
		"category": category,
		"produits": produits,
	}
	return render(request, 'core/category-products-list.html', context)

def vendor_list_view(request):
	vendors = Vendeur.objects.all()
	context = {
		'vendors': vendors,
	}
	return render(request, 'core/vendor-list.html', context)

def vendor_detail_view(request, vid):
	vendeur = Vendeur.objects.get(vid=vid)
	produits = Produit.objects.filter(product_status='published', vendeur=vendeur)
	context = {
		'vendeur': vendeur,
		'produits': produits,
	}
	return render(request, 'core/vendor-detail.html', context)

def product_detail_view(request, pid):
	produit = Produit.objects.get(pid=pid)
	# product = get_object_or_404(Product, pid=pid)
	produits = Produit.objects.filter(category=produit.category).exclude(pid=pid)
	p_image = produit.p_images.all()

	reviews = ProduitReview.objects.filter(produit=produit).order_by('-date')
	average_rating = ProduitReview.objects.filter(produit=produit).aggregate(rating=Avg('rating'))
	review_form = ProductReviewFrom()

	make_review = True
	if request.user.is_authenticated:
		user_review_count = ProduitReview.objects.filter(user=request.user, produit=produit).count() 

		if user_review_count > 0:
			make_review = False

	context = {
		'produit': produit,
		'p_image': p_image,
		'produits': produits,
		'reviews': reviews,
		'average_rating': average_rating,
		'review_form': review_form,
		'make_review': make_review,
	}
	return render(request, 'core/product-detail.html', context)

def tags_list(request, tag_slug=None):
	produits = Produit.objects.filter(product_status='published').order_by('-id')

	tag = None
	if tag_slug:
		tag = Tag.objects.get(slug=tag_slug)
		# tag = get_object_or_404(Tag, slug=tag_slug)
		produits = produits.filter(tags__in=[tag])

	context = {
		'produits': produits,
		'tag': tag,
	}

	return render(request, 'core/tag.html', context)

def ajax_add_review(request, pid):
	produit = Produit.objects.get(pk=pid)
	user = request.user
	image = user.image.url

	review = ProduitReview.objects.create(
		user=user,
		produit=produit,
		review=request.POST['review'],
		rating=request.POST['rating'],
	)
	
	context = {
		'user': user.username,
		'review': request.POST['review'],
		'rating': request.POST['rating'],
		'image': image
	}

	average_reviews = ProduitReview.objects.filter(produit=produit).aggregate(rating=Avg('rating'))


	return JsonResponse(
		{
			'bool': True,
			'context': context,
			'average_reviews': average_reviews,
		}
	)

def search_view(request):
	# query = request.GET['q'] OR
	query = request.GET.get('q') 

	produits = Produit.objects.filter(title__icontains=query).order_by('-date')

	context = {
		'produits': produits,
		'query': query,
	}

	return render(request, 'core/search.html', context)

def filter_product(request):
	categories = request.GET.getlist('category[]')
	vendors = request.GET.getlist('vendor[]')

	min_price = request.GET.get('min_price')
	max_price = request.GET.get('max_price')

	produits = Produit.objects.filter(product_status='published').order_by('-id').distinct()

	produits = produits.filter(price__gte=min_price)
	produits = produits.filter(price__lte=max_price)

	if len(categories) > 0:
		produits = produits.filter(category__id__in=categories).distinct()
	if len(vendors) > 0:
		produits = produits.filter(vendeur__id__in=vendors).distinct()

	context = {
		'produits': produits
	}

	data = render_to_string('core/async/product-list.html', context)
	return JsonResponse({'data': data})

def add_to_cart(request):
	cart_product = {}

	cart_product[str(request.GET['id'])] = {
		'qty': request.GET['qty'],
		'title': request.GET['title'],
		'price': request.GET['price'],
		'image': request.GET['image'],
		'pid': request.GET['pid'],
	}

	if 'cart_data_object' in request.session:
		if str(request.GET['id']) in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
			cart_data.update(cart_data)
			request.session['cart_data_object'] = cart_data
		else:
			cart_data = request.session['cart_data_object']
			cart_data.update(cart_product)
			request.session['cart_data_object'] = cart_data
	else:
		request.session['cart_data_object'] = cart_product

	return JsonResponse({
			'data':request.session['cart_data_object'],
			'totalcartitems':len(request.session['cart_data_object'])
		})

import locale

def cart_view(request):
    # Configurer les paramètres régionaux pour utiliser la virgule comme séparateur décimal
    locale.setlocale(locale.LC_NUMERIC, 'fr_FR.UTF-8')

    cart_total_amount = 0
    if 'cart_data_object' in request.session:
        for product_id, item in request.session['cart_data_object'].items():
            try:
                # Convertir la quantité en entier
                qty = int(item['qty'])
                
                # Convertir le prix en flottant après avoir remplacé la virgule par un point
                price = locale.atof(item['price'].replace(',', '.'))

                # Calculer le montant total du panier
                cart_total_amount += qty * price
            except (ValueError, TypeError) as e:
                # Gérer les erreurs de conversion
                print(f"Erreur de conversion pour le produit {product_id}: {e}")
                continue

        return render(request, 'core/cart.html', {
            'cart_data': request.session['cart_data_object'],
            'totalcartitems': len(request.session['cart_data_object']),
            'cart_total_amount': cart_total_amount
        })
    else:
        return render(request, 'core/cart.html')


def delete_from_cart(request):
	product_id = str(request.GET['id'])
	if 'cart_data_object' in request.session:
		if product_id in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			del request.session['cart_data_object'][product_id]
			request.session['cart_data_object'] = cart_data

	cart_total_amount = 0
	if 'cart_data_object' in request.session:
		for product_id, item in request.session['cart_data_object'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])

	context = render_to_string('core/async/cart-list.html', {
			'cart_data': request.session['cart_data_object'],
			'totalcartitems': len(request.session['cart_data_object']),
			'cart_total_amount': cart_total_amount
		})
	return JsonResponse({
			'data': context,
			'totalcartitems': len(request.session['cart_data_object']),
		})

def update_cart(request):
	product_id = str(request.GET['id'])
	product_qty = request.GET['qty']
	if 'cart_data_object' in request.session:
		if product_id in request.session['cart_data_object']:
			cart_data = request.session['cart_data_object']
			cart_data[str(request.GET['id'])]['qty'] = product_qty
			request.session['cart_data_object'] = cart_data

	cart_total_amount = 0
	if 'cart_data_object' in request.session:
		for product_id, item in request.session['cart_data_object'].items():
			cart_total_amount += int(item['qty']) * float(item['price'])


	context = render_to_string('core/async/cart-list.html', {
			'cart_data': request.session['cart_data_object'],
			'totalcartitems': len(request.session['cart_data_object']),
			'cart_total_amount': cart_total_amount
		})
	return JsonResponse({
			'data': context,
			'totalcartitems': len(request.session['cart_data_object']),
		})

@login_required
def wishlist_view(request):
	try:
		wishlist = LigneCommande.objects.filter(user=request.user)
	except:
		wishlist = None

	context = {
		'wishlist': wishlist
	}
	return render(request, 'core/wishlist.html', context)

@login_required
def add_to_wishlist(request):
	product_id = request.GET['id']
	product = Produit.objects.get(id=product_id)

	context = {}

	wishlist_count = LigneCommande.objects.filter(produit=product, user=request.user).count()

	if wishlist_count > 0:
		context	= {
			'bool': True,
			'wishlist_count': LigneCommande.objects.filter(user=request.user).count()
		}
	else:
		new_wishlist = LigneCommande.objects.create(
			produit=product,
			user=request.user
		)
		context = {
			'bool': True,
			'wishlist_count': LigneCommande.objects.filter(user=request.user).count()
		}

	return JsonResponse(context)

def remove_from_wishlist(request):
	product_id = request.GET['id']
	wishlist = LigneCommande.objects.filter(user=request.user)

	product = LigneCommande.objects.get(id=product_id)
	product.delete()

	context = {
		'bool': True,
		'wishlist': wishlist
	}
	qs_json = serializers.serialize('json', wishlist)
	data = render_to_string('core/async/wishlist-list.html', context)
	return JsonResponse({'data': data, 'wishlist': qs_json})

def contact(request):
	return render(request, 'core/contact.html')

def ajax_contact_form(request):
	name = request.GET['name']
	email = request.GET['email']
	message = request.GET['message']

	contact = Contacts.objects.create(
		name=name,		
		email=email,		
		message=message,		
	)

	data = {
		'bool': True,
	}

	return JsonResponse({'data': data})

def about(request):
	return render(request, 'core/about.html')

# C'est la page de profil de l'utilisateur

def profile(request):
	user = request.user	
	context = {
		'user': user,
	}
	return render(request, 'core/profile.html', context)

def profile_update(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-update.html', context)

def profile_address(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-address.html', context)

def profile_address_update(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-address-update.html', context)

def profile_password(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-password.html', context)

def profile_password_update(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-password-update.html', context)

def profile_order(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order.html', context)

def profile_order_detail(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-detail.html', context)

def profile_order_invoice(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-invoice.html', context)

def profile_order_return(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return.html', context)

def profile_order_cancel(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-cancel.html', context)

def profile_order_return_request(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request.html', context)

def profile_order_return_request_update(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-update.html', context)

def profile_order_return_request_cancel(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-cancel.html', context)

def profile_order_return_request_invoice(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice.html', context)

def profile_order_return_request_invoice_download(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-download.html', context)

def profile_order_return_request_invoice_print(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-print.html', context)

def profile_order_return_request_invoice_email(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-email.html', context)

def profile_order_return_request_invoice_delete(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-delete.html', context)

def profile_order_return_request_invoice_cancel(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-cancel.html', context)

def profile_order_return_request_invoice_update(request):
	user = request.user
	context = {
		'user': user,
	}
	return render(request, 'core/profile-order-return-request-invoice-update.html', context)



























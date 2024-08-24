from django.db import models
from django.utils.html import mark_safe
from userauths.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone


STATUS_CHOICE = (
	("process", "En Cours"),
	("shipped", "Expédié"),
	("delivered", "Livré"),
)

STATUS = (
	("draft", "Brouillon"),
	("disabled", "Désactivé"),
	("rejected", "Rejeté"),
	("in_review", "En Revue"),
	("published", "Publié"),
)

RATING = (
	( 1, "★☆☆☆☆"),
	( 2, "★★☆☆☆"),
	( 3, "★★★☆☆"),
	( 4, "★★★★☆"),
	( 5, "★★★★★"),
)

def user_directory_path(instance, filename):
	return 'user_{0}/{1}'.format(instance.user.id, filename)

class Categorie(models.Model):
	cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='cat', alphabet='abcdefgh12345')
	title = models.CharField(max_length=100, default="Nom de la catégorie")
	image = models.ImageField(upload_to='category', default="category.jpg")

	class Meta:
		verbose_name_plural = 'Les Catégories'

	def category_image(self):
		return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

	def __str__(self):
		return self.title

class Etiquette(models.Model):
	pass

class Vendeur(models.Model):
	vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix='ven', alphabet='abcdefgh12345')
	
	title = models.CharField(max_length=100, default="Nom du Vendeur")
	image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
	description = RichTextUploadingField(null=True, blank=True, default="Description du Vendeur")

	address = models.CharField(max_length=100, default="195 Lomé-TOGO ")
	contact = models.CharField(max_length=100, default="+228 99059314")
	email = models.CharField(max_length=100, default="example@mail.com")

	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

	class Meta:
		verbose_name_plural = 'Les Vendeurs'

	def vendor_image(self):
		return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

	def __str__(self):
		return self.title

class Produit(models.Model):
	pid = ShortUUIDField(unique=True, length=10, max_length=30, alphabet='abcdefgh12345')

	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	category = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name="category")
	vendeur = models.ForeignKey(Vendeur, on_delete=models.SET_NULL, null=True, related_name="vendeur")

	title = models.CharField(max_length=100, default="Nom du Produit")
	image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
	description = RichTextUploadingField(null=True, blank=True, default="Description du produit")

	price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")

	old_price = models.DecimalField(max_digits=10, decimal_places=2, default="2.99")

	specifications = RichTextUploadingField(null=True, blank=True)
	stock_count = models.PositiveIntegerField(default=10, null=True, blank=True)
	shipping = models.CharField(max_length=100, default="1", null=True, blank=True)
	weight = models.CharField(max_length=100, default="0.7", null=True, blank=True)
	life = models.CharField(max_length=100, default="10", null=True, blank=True)
	mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)

	tags = TaggableManager(blank=True)

	# tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

	product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")

	status = models.BooleanField(default=True)
	in_stock = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	digital = models.BooleanField(default=False)

	sku = ShortUUIDField(unique=True, length=4, max_length=30, prefix="sku", alphabet='1234567890')

	date = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name_plural = 'Les Produits'

	def product_image(self):
		return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

	def __str__(self):
		return self.title

	def get_percentage(self):
		new_price = ((self.old_price - self.price) / self.old_price) * 100
		return new_price

class ProduitImages(models.Model):
	images = models.ImageField(upload_to="product-images", default="product.jpg")
	produit = models.ForeignKey(Produit, related_name="p_images", on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Les Images'

####### Cart, Order #######

class Panier(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
	paid_status = models.BooleanField(default=False)
	order_date = models.DateTimeField(auto_now_add=True)
	product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

	class Meta:
		verbose_name_plural = 'Panier'

class Commande(models.Model):
	order = models.ForeignKey(Panier, on_delete=models.CASCADE)
	invoice_no = models.CharField(max_length=200)
	product_status = models.CharField(max_length=200)
	item = models.CharField(max_length=200)
	image = models.CharField(max_length=200)
	qty = models.IntegerField(default=0)
	price = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
	total = models.DecimalField(max_digits=10, decimal_places=2, default="1.99")
	
	class Meta:
		verbose_name_plural = 'Les Commandes'

	def order_img(self):
		return mark_safe('<img src="/media/%s" width="50" height="50">' % (self.image))

####### Product Review, Wishlist, Address #######

class ProduitReview(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, related_name='reviews')
	review = models.TextField()
	rating = models.IntegerField(choices=RATING, default=None)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Avis Produit'

	def __str__(self):
		return self.produit.title

	def get_rating(self):
		return self.rating

class LigneCommande(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = 'Les Lignes Commandes'

	def __str__(self):
		return self.produit.title

class Adresse(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=100, null=True)
	status = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = 'Les Adresses'



####### Contact, Profile #######



class Contacts(models.Model):
	name = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	message = models.TextField()

	class Meta:
		verbose_name = 'Contact Us'
		verbose_name_plural = 'Contact Us'

	def __str__(self):
		return self.name

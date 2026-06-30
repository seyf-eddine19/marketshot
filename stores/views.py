import random
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.db.models import Q, F, Avg, Count, Prefetch, ExpressionWrapper, DecimalField, Min, Max
from django.contrib import messages
from .models import (
    Store, StoreCategory, Product, ProductCategory, ProductAttribute, ProductVariant, 
    Order, OrderItem, Payment
)

class MarketplaceView(TemplateView):
    template_name = "stores/index.html"
    paginate_by = 30


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Featured stores
        context["featured_stores"] = (
            Store.objects.filter(
                is_active=True
            ).order_by("-created_at")[:6]
        )

        # Featured products
        context["featured_products"] = (
            Product.objects.filter(
                is_active=True,
                is_featured=True
            )
            .select_related(
                "store"
            )
        )[:6]

        # Categories
        context["categories"] = (
            StoreCategory.objects.all()
        )

        return context

class StoreListView(ListView):
    model = Store
    template_name = "stores/store_list.html"
    context_object_name = "stores"
    paginate_by = 30

    def get_queryset(self):
        queryset = (
            Store.objects
            .annotate(
                products_count1=Count(
                    "products",
                    filter=Q( products__is_active=True, products__variants__stock__gt=0),
                    distinct=True
                )
            ).filter(
                is_active=True
            )
            .prefetch_related("categories")
            .select_related("owner")
            .order_by("-is_featured", "-is_verified", "-created_at")
        )

        search = self.request.GET.get("q")
        category = self.request.GET.get("category")

        if search:
            queryset = queryset.filter(
                Q(name_en__icontains=search) |
                Q(name_ar__icontains=search) |
                Q(name_fr__icontains=search) |
                Q(tagline_en__icontains=search) |
                Q(tagline_ar__icontains=search) |
                Q(tagline_fr__icontains=search) |
                Q(categories__name_en__icontains=search)
            ).distinct()

        if category:
            queryset = queryset.filter(
                categories__slug=category
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = StoreCategory.objects.all()
        context["selected_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")

        return context

class StoreDetailView(ListView):
    template_name = 'stores/store_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        self.store = get_object_or_404(
            Store,
            pk=kwargs.get('pk'),
            is_active=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # 1. Base Queryset & Prefetching
        queryset = Product.objects.filter(
            store=self.store,
            is_active=True
        ).prefetch_related(
            'variants__attribute_values'
        )

        # 2. Final Price Annotation (with discount)
        queryset = queryset.annotate(
            final_price=ExpressionWrapper(
                F('base_price') * (1 - (F('discount') / 100)),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        # 3. Category Filter
        cat_id = self.request.GET.get('category_id')
        if cat_id:
            try:
                cat_id = int(cat_id)
                if ProductCategory.objects.filter(id=cat_id).exists():
                    queryset = queryset.filter(category_id=cat_id)
                else:
                    queryset = queryset.filter(category__store_category_id=cat_id)
            except (ValueError, TypeError):
                pass

        # 4. Price Filter
        min_p = self.request.GET.get('min_price')
        max_p = self.request.GET.get('max_price')
        if min_p:
            queryset = queryset.filter(final_price__gte=min_p)
        if max_p:
            queryset = queryset.filter(final_price__lte=max_p)

        # 5. Attribute Filter (Grouped by Category)
        attrs = self.request.GET.getlist('attributes')
        if attrs:
            selected_attrs = ProductAttribute.objects.filter(id__in=attrs)
            
            attr_map = {}
            for attr in selected_attrs:
                attr_map.setdefault(attr.category, []).append(attr.id)

            # AND between categories, OR inside each category
            for category, attr_ids in attr_map.items():
                queryset = queryset.filter(
                    variants__attribute_values__id__in=attr_ids,
                    variants__attribute_values__category=category
                )

        # 6. Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name_en__icontains=q) |
                Q(name_ar__icontains=q) |
                Q(name_fr__icontains=q) |
                Q(category__name_en__icontains=q)
            )

        # 7. Only Available Products (Triggers duplicates due to multiple variants)
        queryset = queryset.filter(variants__stock__gt=0)
        print("Initial queryset (with potential duplicates):", queryset)

        # 8. Sorting
        sort = self.request.GET.get('sort')
        sort_map = {
            'price_low': 'final_price',
            'price_high': '-final_price',
            'newest': '-created_at'
        }
        queryset = queryset.order_by(sort_map.get(sort, '-created_at'))

        # ✨ THE FIX: Guarantee a flat, unique product list before Paginator grabs it
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = self.store

        # Category Tree
        categories = ProductCategory.objects.filter(
            product__store=self.store
        ).annotate(
            product_count=Count('product', filter=Q(product__is_active=True, product__variants__stock__gt=0), distinct=True)
        ).select_related('store_category')

        tree = {}
        for cat in categories:
            sc = cat.store_category
            if sc.id not in tree:
                tree[sc.id] = {
                    "store_category": sc,
                    "product_categories": []
                }
            tree[sc.id]["product_categories"].append(cat)
        context['category_tree'] = tree.values()

        # Grouped Attributes for UI
        # Using self.object_list (which is now properly distinct!)
        attributes = ProductAttribute.objects.filter(
            variant_combos__product__in=self.object_list
        ).distinct()

        grouped_attrs = {}
        for attr in attributes:
            key = attr.category
            if key not in grouped_attrs:
                grouped_attrs[key] = {
                    "label": attr.display_label if attr.category == "OTHER" else attr.get_category_display(),
                    "items": []
                }
            grouped_attrs[key]["items"].append(attr)
        context['grouped_attributes'] = grouped_attrs

        # Price Range (Slight optimization: only check active & available product base prices)
        price_range = Product.objects.filter(
            store=self.store,
            is_active=True,
            variants__stock__gt=0
        ).aggregate(
            min=Min('base_price'),
            max=Max('base_price')
        )

        context['price_min'] = price_range['min'] or 0
        context['price_max'] = price_range['max'] or 1000

        # Pagination & Filter Persistence
        query = self.request.GET.copy()
        query.pop('page', None)
        context['current_filters'] = query.urlencode()
        context['selected_attributes'] = set(map(int, self.request.GET.getlist('attributes')))

        return context

class ProductListView(ListView):
    model = Product
    template_name = "stores/products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        # Base Queryset with optimizations
        queryset = Product.objects.filter(is_active=True).select_related('store', 'category').prefetch_related(
            Prefetch('variants', queryset=ProductVariant.objects.all().prefetch_related('attribute_values'))
        )

        # 1. Search Query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name_en__icontains=q) | Q(name_ar__icontains=q) | Q(name_fr__icontains=q)
            )

        # 2. Category Filter (Supports both ID and Slug)
        cat_id = self.request.GET.get('category_id')
        cat_slug = self.request.GET.get('category')
        if cat_id:
            queryset = queryset.filter(category_id=cat_id)
        elif cat_slug:
            queryset = queryset.filter(category__slug=cat_slug)

        # 3. Status Filters
        if self.request.GET.get('sale') == '1': queryset = queryset.filter(is_on_sale=True)
        if self.request.GET.get('new') == '1': queryset = queryset.filter(is_new_arrival=True)

        # 4. Price Range
        min_p = self.request.GET.get('min_price')
        max_p = self.request.GET.get('max_price')
        if min_p: queryset = queryset.filter(base_price__gte=min_p)
        if max_p: queryset = queryset.filter(base_price__lte=max_p)

        # 5. Attribute Filtering (AND between categories, OR within)
        attrs = self.request.GET.getlist('attributes')
        if attrs:
            selected_attrs = ProductAttribute.objects.filter(id__in=attrs)
            attr_map = {}
            for attr in selected_attrs:
                attr_map.setdefault(attr.category, []).append(attr.id)

            for category, ids in attr_map.items():
                queryset = queryset.filter(variants__attribute_values__id__in=ids).distinct()

        # 6. Sorting Logic
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('base_price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-base_price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Category Tree
        tree = []
        for sc in StoreCategory.objects.all().prefetch_related('product_types'):
            pcs = sc.product_types.annotate(product_count=Count('product', filter=Q(product__is_active=True)))
            if pcs.exists():
                tree.append({'store_category': sc, 'product_categories': pcs})
        
        context['category_tree'] = tree
        
        # Attributes for sidebar (Dynamic based on current queryset)
        attributes = ProductAttribute.objects.filter(variant_combos__product__in=self.get_queryset()).distinct()
        grouped_attrs = {}
        for attr in attributes:
            key = attr.category
            grouped_attrs.setdefault(key, {"label": attr.get_category_display() if key != "OTHER" else attr.display_label, "items": []})
            grouped_attrs[key]["items"].append(attr)

        context['grouped_attributes'] = grouped_attrs
        context['selected_attributes'] = [int(i) for i in self.request.GET.getlist('attributes') if i.isdigit()]
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "stores/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        # We compute aggregate metrics and prefetches natively on the queryset
        # to guarantee flat db lookup pipelines.
        return (
            Product.objects.filter(is_active=True)
            .select_related("store", "category", "category__store_category")
            .annotate(
                annotated_avg_rating=Avg("reviews__rating"),
                annotated_reviews_count=Count("reviews", distinct=True),
            )
            .prefetch_related(
                "images",
                "reviews__customer",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.prefetch_related(
                        "attribute_values"
                    ),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # 1. Premium Attributes Query Optimization
        # Added select_related to prevent N+1 hits when the template calls 'attr.display_label'
        # and ordered by fallback language structure compatibility.
        context["attributes"] = (
            ProductAttribute.objects.filter(variant_combos__product=product)
            .select_related()  # Adjust if display_label relies on a FK field
            .distinct()
            .order_by("category", "value_en")
        )

        # 2. Ecosystem Related Products Optimization
        # Fetch matching related products (excluding current product)
        related_queryset = list(
            Product.objects.filter(category=product.category)
            .exclude(id=product.id)
        )
        
        if len(related_queryset) >= 4:
            # Randomly sample 4 distinct items if we have plenty
            final_related = random.sample(related_queryset, 4)
        else:
            # Shuffle whatever matches we have
            random.shuffle(related_queryset)
            final_related = related_queryset
            
            # 2. Backfill with completely random products from other categories if short
            needed_count = 4 - len(final_related)
            if needed_count > 0:
                fillers = list(
                    Product.objects.exclude(id=product.id)
                    .exclude(category=product.category)
                    .order_by('?')[:needed_count]
                )
                final_related.extend(fillers)
        context["related_products"] = (
            Product.objects.filter(category=product.category, is_active=True)
            .exclude(pk=product.pk)[:4]
        )
        context["related_products"] = final_related

        print("Related products in context:", [p.id for p in context["related_products"]])

        return context



import json
from django.http import JsonResponse

class GetVariantView(View):
    def post(self, request, product_id):
        data = json.loads(request.body)
        attrs = set(map(int, data.get("attributes", [])))
        variants = ProductVariant.objects.filter(product_id=product_id).prefetch_related("attribute_values")

        for variant in variants:
            variant_attrs = set(
                variant.attribute_values.values_list(
                    "id",
                    flat=True
                )
            )

            if variant_attrs == attrs:
                return JsonResponse({
                    "variant_id": variant.id,
                    "price": str(variant.final_price),
                    "stock": variant.stock
                })

        return JsonResponse({
            "variant_id": variant.id,
            "price": str(variant.final_price),
            "stock": variant.stock,
            "attributes": list(
                ProductAttribute.objects.filter(
                    variant_combos__in=ProductVariant.objects.filter(product_id=product_id)
                ).values_list(
                    "id", flat=True
                ).distinct())
        })

class GetVariantView(View):

    def post(self, request, product_id):

        data = json.loads(request.body)

        attrs = data.get("attributes", [])

        attrs = [int(x) for x in attrs]


        variants = (
            ProductVariant.objects
            .filter(
                product_id=product_id,
                attribute_values__id__in=attrs
            )
            .annotate(
                matched=Count("attribute_values")
            )
            .filter(
                matched=len(attrs)
            )
            .prefetch_related("attribute_values")
        )


        variant = variants.first()


        if not variant:
            return JsonResponse({
                "variant_id": None,
                "attributes": []
            })


        available = []

        for v in ProductVariant.objects.filter(
            product_id=product_id
        ).prefetch_related("attribute_values"):


            # check compatibility

            selected=set(attrs)

            variant_attrs=set(
                v.attribute_values.values_list(
                    "id",
                    flat=True
                )
            )


            if selected.issubset(variant_attrs):

                available.extend(
                    list(variant_attrs)
                )


        return JsonResponse({

            "variant_id":variant.id,

            "price":
                str(variant.final_price),

            "stock":
                variant.stock,

            "attributes":
                list(set(available))
        })

from django.contrib.auth.mixins import LoginRequiredMixin


from .models import (
    Cart,
    CartItem,
    Product,
    ProductVariant
)


# =========================
# Helper
# =========================
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(
        customer=user
    )
    return cart


# =========================
# Cart Detail
# =========================
class CartDetailView(LoginRequiredMixin, View):

    def get(self, request):
        cart = get_user_cart(request.user)

        items = (
            cart.items
            .select_related(
                "product",
                "product__store"
            )
            .prefetch_related(
                "attribute_values"
            )
        )

        return render(
            request,
            "stores/cart/detail.html",
            {
                "cart": cart,
                "items": items
            }
        )

from collections import OrderedDict
from decimal import Decimal

class CartDetailView(LoginRequiredMixin, View):

    def get(self, request):
        cart = get_user_cart(request.user)

        items = (
            cart.items
            .select_related(
                "product",
                "product__store",
            )
            .prefetch_related(
                "attribute_values"
            )
            .order_by("product__store__name_en")
        )

        stores = OrderedDict()

        grand_subtotal = Decimal("0")
        grand_delivery = Decimal("0")

        for item in items:
            store = item.product.store

            if store.id not in stores:

                # default delivery company
                delivery = (
                    store.delivery_companies
                    .filter(is_active=True, is_default=True)
                    .select_related("company")
                    .first()
                )

                delivery_price = (
                    delivery.delivery_price
                    if delivery else Decimal("0")
                )

                stores[store.id] = {
                    "store": store,
                    "items": [],
                    "subtotal": Decimal("0"),
                    "delivery": delivery_price,
                    "free_delivery_from": (
                        delivery.free_delivery_from if delivery else None
                    ),
                    "company": (
                        delivery.company if delivery else None
                    ),
                }

            stores[store.id]["items"].append(item)
            stores[store.id]["subtotal"] += item.total_price

        # Apply free delivery
        for data in stores.values():

            if (
                data["free_delivery_from"]
                and data["subtotal"] >= data["free_delivery_from"]
            ):
                data["delivery"] = Decimal("0")

            data["total"] = data["subtotal"] + data["delivery"]

            grand_subtotal += data["subtotal"]
            grand_delivery += data["delivery"]

        grand_total = grand_subtotal + grand_delivery

        return render(
            request,
            "stores/cart/detail.html",
            {
                "cart": cart,
                "stores": stores.values(),
                "grand_subtotal": grand_subtotal,
                "grand_delivery": grand_delivery,
                "grand_total": grand_total,
            },
        )
    
# =========================
# Add product without variant
# =========================
class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_user_cart(request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=None,
            defaults={
                "quantity":1
            }
        )

        if not created:
            item.quantity += 1
            item.save()

        messages.success(request, _("Product added to cart"))
        return redirect("stores:cart")

class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_user_cart(request.user)
        quantity = int(request.POST.get("quantity", 1))
        attribute_ids = request.POST.getlist("attributes")

        item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        if attribute_ids:
            attributes = ProductAttribute.objects.filter(id__in=attribute_ids)
            item.attribute_values.set(attributes)

        messages.success(
            request,
            _("Product added to cart")
        )


        return redirect(
            "stores:cart"
        )

class CartAddView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )


        cart = get_user_cart(request.user)


        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )


        attribute_ids = request.POST.getlist(
            "attributes"
        )


        attributes = ProductAttribute.objects.filter(
            id__in=attribute_ids
        )


        cart.add_item(
            product=product,
            attributes=attributes,
            quantity=quantity
        )


        messages.success(
            request,
            _("Product added to cart")
        )


        return redirect("stores:cart")


class CartAddView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/product/{product_id}/")

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )


        cart=get_user_cart(request.user)


        quantity=int(
            request.POST.get(
                "quantity",
                1
            )
        )


        attrs_string = request.POST.get(
            "attribute_values",
            ""
        )


        attrs = [
            int(x)
            for x in attrs_string.split(",")
            if x
        ]


        # find existing item with same attrs

        item=None


        for cart_item in cart.items.prefetch_related(
            "attribute_values"
        ):


            current=set(
                cart_item.attribute_values.values_list(
                    "id",
                    flat=True
                )
            )


            if current == set(attrs):

                item=cart_item
                break



        if item:

            item.quantity += quantity
            item.save()



        else:

            item=CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )


            if attrs:

                item.attribute_values.set(attrs)



        messages.success(
            request,
            _("Product added to cart")
        )


        return redirect(
            "stores:cart"
        )

from django.shortcuts import redirect

class CartAddView1(LoginRequiredMixin, View):

    def post(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        cart = get_user_cart(request.user)

        quantity = int(request.POST.get("quantity", 1))

        attrs_string = request.POST.get("attribute_values", "")
        attrs = [int(x) for x in attrs_string.split(",") if x]

        item = None

        for cart_item in cart.items.prefetch_related("attribute_values"):
            current = set(cart_item.attribute_values.values_list("id", flat=True))

            if current == set(attrs):
                item = cart_item
                break

        if item:
            item.quantity += quantity
            item.save()
        else:
            item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            if attrs:
                item.attribute_values.set(attrs)

        messages.success(request, _("Product added to cart"))

        # 👇 مهم جدًا
        next_url = request.GET.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("stores:cart")

class CartAddView(View):

    def post(self, request, product_id):

        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/product/{product_id}/")

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        cart = get_user_cart(request.user)

        quantity = int(request.POST.get("quantity", 1))

        attrs_string = request.POST.get("attribute_values", "")
        attrs = [int(x) for x in attrs_string.split(",") if x]

        item = None

        for cart_item in cart.items.prefetch_related("attribute_values"):
            current = set(cart_item.attribute_values.values_list("id", flat=True))

            if current == set(attrs):
                item = cart_item
                break

        if item:
            item.quantity += quantity
            item.save()
        else:
            item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
            if attrs:
                item.attribute_values.set(attrs)

        messages.success(request, _("Product added to cart"))

        return redirect("stores:cart")
# =========================
# Add product with variant
# =========================
class CartAddVariantView(LoginRequiredMixin, View):
    def post(self, request, product_id, variant_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        cart = get_user_cart(request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={
                "quantity":1
            }
        )

        if not created:
            item.quantity += 1
            item.save()

        messages.success(request, _("Variant added to cart"))
        return redirect("stores:cart")


# =========================
# Update quantity
# =========================
class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get("quantity", 1))

        if quantity <= 0:
            item.delete()

        else:
            item.quantity = quantity
            item.save()

        messages.success(request, _(""))
        return redirect("stores:cart")


# =========================
# Remove item
# =========================
class CartRemoveView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()

        messages.success(request, _("Item removed"))
        return redirect("stores:cart")


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = max(1, int(request.POST.get("quantity", 1)))

        item.quantity = quantity
        item.save()

        return JsonResponse({
            "success": True,
            "quantity": item.quantity,
            "item_total": float(item.total),
            "cart_total": float(cart.total),
            "cart_count": cart.items.count(),
        })


class CartRemoveView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        item.delete()

        return JsonResponse({
            "success": True,
            "cart_total": float(cart.total),
            "cart_count": cart.items.count(),
        })

class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        cart = get_user_cart(request.user)
        if not cart.items.exists():
            messages.error(request, _("Your cart is empty."))
            return redirect("stores:cart")
        return redirect("stores:checkout_address") 
    

class CheckoutAddressView(LoginRequiredMixin, TemplateView):
    template_name = "stores/checkout/address.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_user_cart(self.request.user)
        return context

    def post(self, request):
        request.session["checkout_address"] = {
            "full_name":
            request.POST.get(
                "full_name"
            ),

            "phone":
            request.POST.get(
                "phone"
            ),

            "wilaya":
            request.POST.get(
                "wilaya"
            ),

            "city":
            request.POST.get(
                "city"
            ),

            "address":
            request.POST.get(
                "address"
            ),

            "notes":
            request.POST.get(
                "notes"
            ),
        }

        return redirect("stores:checkout_payment")


class CheckoutPaymentView(LoginRequiredMixin, TemplateView):
    template_name = "stores/checkout/payment.html"

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):

        if not request.session.get(
            "checkout_address"
        ):

            return redirect(
                "stores:checkout_address"
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


    def post(
        self,
        request
    ):

        request.session[
            "checkout_payment"
        ] = request.POST.get(
            "payment_method"
        )

        return redirect(
            "stores:checkout_confirm"
        )
    

from django.db import transaction


class OrderCreateView(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self,request):

        cart = get_user_cart(request.user)

        if not cart.items.exists():

            messages.error(
                request,
                _("Your cart is empty.")
            )

            return redirect(
                "stores:cart"
            )


        address_data = request.session.get(
            "checkout_address"
        )

        payment_method = request.session.get(
            "checkout_payment"
        )


        if not address_data:

            return redirect(
                "stores:checkout_address"
            )


        if not payment_method:

            return redirect(
                "stores:checkout_payment"
            )


        order = Order.objects.create(
            customer=request.user,
            full_name=address_data["full_name"],
            phone=address_data["phone"],
            wilaya=address_data["wilaya"],
            city=address_data["city"],
            address=address_data["address"],
            notes=address_data["notes"],
            payment_method=payment_method,
            total_amount=cart.total_price,
            status="PENDING"
        )


        for item in cart.items.prefetch_related(
            "attribute_values"
        ):

            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.discounted_price,
                total_price=(
                    item.product.discounted_price
                    * item.quantity
                )
            )

            order_item.attribute_values.set(
                item.attribute_values.all()
            )


        cart.items.all().delete()


        request.session.pop(
            "checkout_address",
            None
        )

        request.session.pop(
            "checkout_payment",
            None
        )


        messages.success(
            request,
            _("Order created successfully.")
        )

        return redirect(
            "stores:order_detail",
            order.pk
        )


from collections import OrderedDict
from decimal import Decimal

class CartDetailView(LoginRequiredMixin, View):

    def get(self, request):

        cart = (
            get_user_cart(request.user)
        )

        items = (
            cart.items
            .select_related(
                "product",
                "product__store",
            )
            .prefetch_related(
                "attribute_values",
            )
            .order_by("product__store_id")
        )

        stores = OrderedDict()

        grand_items = 0
        grand_subtotal = Decimal("0")
        grand_discount = Decimal("0")
        grand_delivery = Decimal("600")

        for item in items:

            store = item.product.store

            if store.id not in stores:

                shipping = (
                    store.delivery_companies
                    .filter(
                        is_active=True,
                        is_default=True,
                    )
                    .select_related("company")
                    .first()
                )

                stores[store.id] = {
                    "store": store,
                    "items": [],
                    "items_count": 0,
                    "subtotal": Decimal("0"),
                    "discount": Decimal("0"),
                    "delivery_company": shipping.company if shipping else None,
                    "delivery_price": shipping.delivery_price if shipping else Decimal("0"),
                    "free_delivery_from": shipping.free_delivery_from if shipping else None,
                    "total": Decimal("0"),
                }

            summary = stores[store.id]

            summary["items"].append(item)

            summary["items_count"] += item.quantity

            summary["subtotal"] += item.total_price

        for summary in stores.values():

            if (
                summary["free_delivery_from"]
                and summary["subtotal"] >= summary["free_delivery_from"]
            ):
                summary["delivery_price"] = Decimal("0")

            summary["total"] = (
                summary["subtotal"]
                - summary["discount"]
                + summary["delivery_price"]
            )

            grand_items += summary["items_count"]
            grand_subtotal += summary["subtotal"]
            grand_discount += summary["discount"]
            grand_delivery += summary["delivery_price"]

        context = {
            "cart": cart,
            "stores": stores.values(),
            "grand_items": grand_items,
            "grand_subtotal": grand_subtotal,
            "grand_discount": grand_discount,
            "grand_delivery": grand_delivery,
            "grand_total": (
                grand_subtotal
                - grand_discount
                + grand_delivery
            ),
        }
        context['recent_orders'] = Order.objects.filter(customer=request.user).order_by('-created_at')[:3]

        return render(
            request,
            "stores/cart/detail.html",
            context,
        )
    
class CheckoutView(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request):

        cart = get_user_cart(request.user)

        address = (
            request.user.addresses
            .filter(is_default=True)
            .first()
        )

        if not address:
            messages.error(
                request,
                _("Please add a default address.")
            )
            return redirect("stores:checkout")

        items = (
            cart.items
            .select_related(
                "product",
                "product__store",
                "variant",
            )
            .prefetch_related(
                "attribute_values"
            )
        )

        stores = OrderedDict()

        for item in items:

            store = item.product.store

            if store.id not in stores:

                shipping = (
                    store.delivery_companies
                    .filter(
                        is_active=True,
                        is_default=True,
                    )
                    .select_related("company")
                    .first()
                )

                stores[store.id] = {
                    "store": store,
                    "items": [],
                    "items_count": 0,
                    "subtotal": Decimal("0"),
                    "discount": Decimal("0"),
                    "delivery_company": shipping.company if shipping else None,
                    "delivery_price": shipping.delivery_price if shipping else Decimal("0"),
                    "free_delivery_from": shipping.free_delivery_from if shipping else None,
                }

            summary = stores[store.id]

            summary["items"].append(item)
            summary["items_count"] += item.quantity
            summary["subtotal"] += item.total_price

        for summary in stores.values():

            if (
                summary["free_delivery_from"]
                and summary["subtotal"] >= summary["free_delivery_from"]
            ):
                summary["delivery_price"] = Decimal("0")

            total = (
                summary["subtotal"]
                - summary["discount"]
                + summary["delivery_price"]
            )

            order = Order.objects.create(

                customer=request.user,

                store=summary["store"],

                items_count=summary["items_count"],

                subtotal=summary["subtotal"],

                discount=summary["discount"],

                delivery_company=summary["delivery_company"],

                delivery_price=summary["delivery_price"],

                total_price=total,
            )

            OrderShippingAddress.objects.create(

                order=order,

                full_name=address.full_name,

                phone=address.phone,

                wilaya=address.wilaya.name,

                address=address.address,

                postal_code=address.postal_code,

                country=address.country,
            )

            Payment.objects.create(

                order=order,

                method=Payment.Method.CASH,

                status=Payment.Status.PENDING,
            )

            OrderStatusHistory.objects.create(

                order=order,

                status=Order.Status.PENDING,
            )

            for item in summary["items"]:

                OrderItem.objects.create(

                    order=order,

                    product=item.product,

                    variant=item.variant,

                    product_name=item.product.name,

                    variant_name=", ".join(
                        a.value
                        for a in item.attribute_values.all()
                    ),

                    unit_price=item.unit_price,

                    quantity=item.quantity,

                    total_price=item.total_price,
                )

                if item.variant:

                    item.variant.stock -= item.quantity
                    item.variant.save()

        cart.items.all().delete()

        messages.success(
            request,
            _("Your order has been placed successfully.")
        )

        return redirect("stores:orders")




from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext as _
from decimal import Decimal
from collections import OrderedDict

# Assuming models are imported from your apps
from .models import Order, OrderItem, OrderShippingAddress, Payment, OrderStatusHistory

class CheckoutView(LoginRequiredMixin, View):

    def get_checkout_data(self, user):
        """Helper to compute grouped store elements and pricing metrics"""
        from .views import get_user_cart # adjust based on where your helper lives
        cart = get_user_cart(user)
        items = cart.items.select_related(
            "product", "product__store"
        ).prefetch_related("attribute_values")

        stores = OrderedDict()
        grand_subtotal = Decimal("0")
        grand_delivery = Decimal("0")

        for item in items:
            store = item.product.store
            if store.id not in stores:
                shipping = store.delivery_companies.filter(
                    is_active=True, is_default=True
                ).select_related("company").first()

                stores[store.id] = {
                    "store": store,
                    "items": [],
                    "items_count": 0,
                    "subtotal": Decimal("0"),
                    "delivery_company": shipping.company if shipping else None,
                    "delivery_price": Decimal("600"),
                    "free_delivery_from": shipping.free_delivery_from if shipping else None,
                    "total": Decimal("0"),
                }

            summary = stores[store.id]
            summary["items"].append(item)
            summary["items_count"] += item.quantity
            summary["subtotal"] += item.total_price

        for summary in stores.values():
            if summary["free_delivery_from"] and summary["subtotal"] >= summary["free_delivery_from"]:
                summary["delivery_price"] = Decimal("600")
            
            summary["total"] = summary["subtotal"] + summary["delivery_price"]
            grand_subtotal += summary["subtotal"]
            grand_delivery += summary["delivery_price"]

        return {
            "cart": cart,
            "stores": stores.values(),
            "grand_subtotal": grand_subtotal,
            "grand_delivery": grand_delivery,
            "grand_total": grand_subtotal + grand_delivery,
        }

    def get(self, request):
        data = self.get_checkout_data(request.user)
        if not data["cart"].items.exists():
            messages.error(request, _("Your cart is empty."))
            return redirect("stores:cart")
            
        # Fallback pre-fill default address if it exists
        default_address = request.user.addresses.filter(is_default=True).first()
        data["default_address"] = default_address
        
        return render(request, "stores/cart/checkout.html", data)

    @transaction.atomic
    def post(self, request):
        data = self.get_checkout_data(request.user)
        if not data["cart"].items.exists():
            messages.error(request, _("Your cart is empty."))
            return redirect("stores:cart")

        # Capture customer information from the bottom form manually or via forms.py
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        wilaya_name = request.POST.get("wilaya")
        address_text = request.POST.get("address")
        payment_method = request.POST.get("payment_method", Payment.Method.CASH)
        notes = request.POST.get("notes", "")

        if not all([full_name, phone, wilaya_name, address_text]):
            messages.error(request, _("Please complete all shipping address fields."))
            return render(request, "stores/cart/checkout.html", data)

        # Create unique split orders per vendor group matching database properties
        for summary in data["stores"]:
            order = Order.objects.create(
                customer=request.user,
                store=summary["store"],
                status=Order.Status.PENDING,
                subtotal=summary["subtotal"],
                delivery_company=summary["delivery_company"],
                delivery_price=summary["delivery_price"],
                total_price=summary["total"],
                notes=notes,
            )

            # Order shipping snapshot setup
            OrderShippingAddress.objects.create(
                order=order,
                full_name=full_name,
                phone=phone,
                wilaya=wilaya_name,
                address=address_text,
                country="Algeria"
            )

            # Order payment details mapping 
            Payment.objects.create(
                order=order,
                method=payment_method,
                status=Payment.Status.PENDING,
            )

            # System order life status tracking history
            OrderStatusHistory.objects.create(
                order=order,
                status=Order.Status.PENDING,
            )

            # Populate order line items accurately
            for item in summary["items"]:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=getattr(item, 'variant', None),
                    quantity=item.quantity,
                    price=item.product.discounted_price,
                )

        # Flush processed items safely out of cart bucket
        data["cart"].items.all().delete()

        messages.success(request, _("Your orders have been successfully placed."))
        return redirect("stores:cart")
    

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from collections import OrderedDict
from .models import CartItem # Adjust this to match your CartItem model name

@login_required
def cart_update_view(request, item_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 1. Safely grab item and verify ownership
        item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                item.delete()
                return JsonResponse({"success": True, "removed": True})
            
            # 2. Update quantity & save item
            item.quantity = quantity
            item.save()
            
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "Invalid quantity format"}, status=400)

        # 3. Recalculate Multi-Vendor Data matching your frontend loops
        cart = item.cart
        all_items = cart.items.select_related("product", "product__store")
        
        stores_map = OrderedDict()
        grand_items = 0
        grand_subtotal = Decimal("0")
        grand_delivery = Decimal("0")

        for c_item in all_items:
            store = c_item.product.store
            if store.id not in stores_map:
                # Fallback to store configuration values or defaults
                delivery_price = Decimal("600.00") # Replace with your dynamic shipping model pricing logic
                stores_map[store.id] = {
                    "id": store.id,
                    "subtotal": Decimal("0"),
                    "delivery_price": delivery_price,
                    "total": Decimal("0")
                }
            
            stores_map[store.id]["subtotal"] += c_item.total_price # assuming total_price is a property or field
            grand_items += c_item.quantity

        # Clean individual store delivery thresholds if applicable
        stores_updates_list = []
        for s_id, summary in stores_map.items():
            summary["total"] = summary["subtotal"] + summary["delivery_price"]
            grand_subtotal += summary["subtotal"]
            grand_delivery += summary["delivery_price"]
            
            # Convert Decimals to Strings for clean JSON serialization
            stores_updates_list.append({
                "id": summary["id"],
                "subtotal": str(summary["subtotal"]),
                "delivery_price": str(summary["delivery_price"]),
                "total": str(summary["total"]),
            })

        # 4. Return clean JSON response structures
        return JsonResponse({
            "success": True,
            "quantity": item.quantity,
            "item_total": str(item.total_price),
            "grand_items": grand_items,
            "grand_subtotal": str(grand_subtotal),
            "grand_delivery": str(grand_delivery),
            "grand_total": str(grand_subtotal + grand_delivery),
            "stores_updates": stores_updates_list
        })
        
    return JsonResponse({"success": False, "error": "Bad Request"}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from collections import OrderedDict

@login_required
def cart_update(request, item_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                item.delete()
                return JsonResponse({"success": True, "removed": True, **get_cart_totals_payload(request.user.cart)})
            
            item.quantity = quantity
            item.save()
            
            payload = {
                "success": True,
                "quantity": item.quantity,
                "item_total": float(item.total_price),
                **get_cart_totals_payload(request.user.cart)
            }
            return JsonResponse(payload)
        except (ValueError, TypeError) as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
            
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

@login_required
def cart_remove(request, item_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        cart = item.cart
        item.delete()
        
        return JsonResponse({"success": True, **get_cart_totals_payload(cart)})
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)


def get_cart_totals_payload(cart):
    """Calculates all nested vendor totals safely to send back to template DOM containers"""
    stores_map = OrderedDict()
    grand_items = 0
    grand_subtotal = Decimal("0")
    grand_delivery = Decimal("0")

    for item in cart.items.all().select_related('product', 'product__store'):
        store = item.product.store
        if store.id not in stores_map:
            # Check for defaults or delivery fallback rules
            shipping = store.delivery_companies.filter(is_active=True, is_default=True).first() if hasattr(store, 'delivery_companies') else None
            delivery_price = shipping.delivery_price if shipping else Decimal("600.00") # 600 DA baseline fallback
            free_delivery_from = shipping.free_delivery_from if shipping else None

            stores_map[store.id] = {
                "id": store.id,
                "subtotal": Decimal("0"),
                "delivery_price": delivery_price,
                "free_delivery_from": free_delivery_from,
                "total": Decimal("0")
            }

        stores_map[store.id]["subtotal"] += Decimal(str(item.total_price))
        grand_items += item.quantity

    stores_updates = []
    for s_id, data in stores_map.items():
        if data["free_delivery_from"] and data["subtotal"] >= data["free_delivery_from"]:
            data["delivery_price"] = Decimal("0")
            
        data["total"] = data["subtotal"] + data["delivery_price"]
        grand_subtotal += data["subtotal"]
        grand_delivery += data["delivery_price"]

        stores_updates.append({
            "id": data["id"],
            "subtotal": float(data["subtotal"]),
            "delivery_price": float(data["delivery_price"]),
            "total": float(data["total"])
        })

    return {
        "grand_items": grand_items,
        "grand_subtotal": float(grand_subtotal),
        "grand_delivery": float(grand_delivery),
        "grand_total": float(grand_subtotal + grand_delivery),
        "stores_updates": stores_updates
    }



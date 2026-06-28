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
            Store.objects.filter(
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


class OrderCreateView(
    LoginRequiredMixin,
    View
):

    @transaction.atomic
    def post(
        self,
        request
    ):

        cart = get_user_cart(
            request.user
        )

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


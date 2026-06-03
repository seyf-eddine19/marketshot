from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from .forms import StoreCategoryForm, ProductCategoryFormSet, StoreForm, ProductVariantFormSet, ProductImageFormSet, ProductForm
from stores.models import StoreCategory, Store, Product, ProductAttribute, ProductVariant, ProductImage, ProductReview

from django.http import JsonResponse
from django.db import transaction

from django.db.models import Avg, Count


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'


class GlobalCategoryManageView(TemplateView):
    template_name = 'dashboard/manage_categories.html'

    def get(self, request, pk=None):
        instance = get_object_or_404(StoreCategory, pk=pk) if pk else None
        form = StoreCategoryForm(instance=instance)
        formset = ProductCategoryFormSet(instance=instance)
        
        context = {
            'store_categories': StoreCategory.objects.prefetch_related('product_types').all(),
            'form': form,
            'formset': formset,
            'is_editing': bool(pk)
        }
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        instance = get_object_or_404(StoreCategory, pk=pk) if pk else None
        
        # Handle Global Delete
        if 'delete_store' in request.POST and instance:
            category_name = instance.name_en
            instance.delete()
            messages.error(request, _(f'Category "{category_name}" has been deleted.'))
            return redirect('dashboard:manage-categories')

        form = StoreCategoryForm(request.POST, request.FILES, instance=instance)
        formset = ProductCategoryFormSet(request.POST, request.FILES, instance=instance)

        if form.is_valid() and formset.is_valid():
            parent = form.save()
            formset.instance = parent
            formset.save()
            
            if pk:
                messages.success(request, _('Category updated successfully!'))
            else:
                messages.success(request, _('New category created successfully!'))
                
            return redirect('dashboard:manage-categories')
        else:
            messages.error(request, _('Please correct the errors below.'))

        context = {
            'store_categories': StoreCategory.objects.all(),
            'form': form,
            'formset': formset,
            'is_editing': bool(pk)
        }
        return render(request, self.template_name, context)


class StoreListView(ListView):
    model = Store
    template_name = "dashboard/stores/list.html"
    context_object_name = "stores"
    paginate_by = 30

    def get_queryset(self):
        qs = (
            Store.objects
            .select_related("owner")
            .prefetch_related("categories")
            .order_by("-created_at")
        )

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                name_en__icontains=q
            ) | qs.filter(
                name_fr__icontains=q
            ) | qs.filter(
                name_ar__icontains=q
            )

        return qs

class StoreCreateView(CreateView):
    model = Store
    form_class = StoreForm
    template_name = "dashboard/stores/form.html"
    success_url = reverse_lazy("dashboard:stores")

class StoreUpdateView(UpdateView):
    model = Store
    form_class = StoreForm
    template_name = "dashboard/stores/form.html"
    success_url = reverse_lazy("dashboard:stores")

class StoreDeleteView(DeleteView):
    model = Store
    template_name = "dashboard/stores/delete.html"
    success_url = reverse_lazy("dashboard:stores")


class ProductListView(ListView):
    model = Product
    template_name = "dashboard/products/list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.select_related('store', 'category').prefetch_related('variants', 'images')
    
class ProductDetailView(TemplateView):
    template_name = "dashboard/products/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = (
            Product.objects
            .select_related("store", "category")
            .prefetch_related("variants__attribute_values", "images", "reviews__customer")
            .get(pk=kwargs["pk"])
        )

        reviews = ProductReview.objects.filter(
            product=product
        ).select_related("customer")

        review_stats = reviews.aggregate(
            avg_rating=Avg("rating"),
            total_reviews=Count("id")
        )

        context.update({
            "product": product,
            "reviews": reviews,
            "avg_rating": round(
                review_stats["avg_rating"] or 0,
                1
            ),
            "reviews_count": review_stats["total_reviews"]
        })

        return context
 
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "dashboard/products/delete.html"
    success_url = reverse_lazy("dashboard:product-list")


# =====================================================
# AJAX VIEW
# =====================================================

from django.http import JsonResponse
def ajax_attributes_by_type(request):

    attr_type = request.GET.get('type')

    attributes = ProductAttribute.objects.filter(category=attr_type)

    return JsonResponse({
        "attributes": [
            {
                "id": attr.id,
                "label": f"{attr.label_en} - {attr.value_en}"
            }
            for attr in attributes
        ]
    })

from django.http import JsonResponse

def ajax_attributes_by_type(request):
    attr_type = request.GET.get('type')
    
    if not attr_type:
        return JsonResponse({"attributes": []}, status=200)
        
    # Double-check if your model field matches 'category' or 'type' 
    attributes = ProductAttribute.objects.filter(category=attr_type)
    
    data = {
        "attributes": [
            {
                "id": attr.id,
                # Safe fallbacks if any field translates to None
                "label": f"{attr.label_en or ''} - {attr.value_en or ''}".strip(" - ")
            }
            for attr in attributes
        ]
    }
    return JsonResponse(data, status=200)

from django.contrib.auth.mixins import LoginRequiredMixin


class MerchantStoreMixin(LoginRequiredMixin):
    """Enforces merchant scope isolation across the administrative dashboard views."""
    def get_merchant_store(self):
        try:
            # Resolves the OneToOne inverse lookup model field relation smoothly
            return self.request.user.managed_store or self.request.user.is_superuser and Store.objects.first()  # Fallback to any store for superusers without a profileS
        except Store.DoesNotExist:
            messages.error(self.request, "Access Denied: Please create your Store registration first.")
            return None

    def dispatch(self, request, *args, **kwargs):
        if not self.get_merchant_store():
            return redirect('dashboard:store-add')  # Route back to profile generation setup
        return super().dispatch(request, *args, **kwargs)


class BaseProductSaveView():
    """Unified controller processing atomic persistence of catalog inventory definitions."""
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/products/form.html'
    success_url = reverse_lazy('dashboard:product-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Branch instances generation securely depending on incoming HTTP verb signature
        if self.request.POST:
            context['variant_formset'] = ProductVariantFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context['variant_formset'] = ProductVariantFormSet(instance=self.object)
            context['image_formset'] = ProductImageFormSet(instance=self.object)

        # Prefetch system-wide defined product attributes to eliminate redundant query loops in template loops
        context['available_attributes'] = {
            'COLOR': ProductAttribute.objects.filter(category=ProductAttribute.Category.COLOR),
            'SIZE': ProductAttribute.objects.filter(category=ProductAttribute.Category.SIZE),
            'MATERIAL': ProductAttribute.objects.filter(category=ProductAttribute.Category.MATERIAL),
            'STORAGE': ProductAttribute.objects.filter(category=ProductAttribute.Category.STORAGE),
            'VOLTAGE': ProductAttribute.objects.filter(category=ProductAttribute.Category.VOLTAGE),
        }
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        variant_formset = context['variant_formset']
        image_formset = context['image_formset']

        # Intercept validation states across all layers before committing modifications
        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            
            # Step 1: Assign the backend merchant profile isolation binding context
            form.instance.store = self.get_merchant_store()
            self.object = form.save()

            # Step 2: Enforce proper relational references on nested components
            variant_formset.instance = self.object
            image_formset.instance = self.object

            # Step 3: Handle deletion flags processed on the front-end components layer
            variant_formset.save(commit=True)
            image_formset.save(commit=True)

            # Step 4: Map dynamic many-to-many attributes array indexes safely across the dynamic variants matrix
            # Formsets send arrays labeled via numeric row identifiers (e.g., variants-0, variants-1, etc.)
            for index, variant_form in enumerate(variant_formset.forms):
                # Ensure we bypass empty boilerplate extra tracking templates instances placeholder forms
                if variant_form.cleaned_data and not variant_form.cleaned_data.get('DELETE', False):
                    variant_instance = variant_form.instance
                    
                    # Extract raw structural lists matching specific positional parameters directly from POST data matrix
                    selected_attribute_ids = self.request.POST.getlist(f'variant_attributes_{index}')
                    
                    if selected_attribute_ids:
                        # Clean and cast payload identifiers to avoid string matching mismatches inside target relationships engine
                        clean_ids = [int(attr_id) for attr_id in selected_attribute_ids if attr_id.isdigit()]
                        variant_instance.attribute_values.set(clean_ids)

            messages.success(self.request, "Product catalog changes committed successfully.")
            return redirect(self.success_url)
        else:
            # Fallback error catch state context loop returning form state parameters tracking matrices
            return self.form_invalid(form)


class ProductCreateView(BaseProductSaveView, CreateView):
    """Gateway operational entity instance designed for item registration setups."""
    def get_object(self, queryset=None):
        return None

class ProductUpdateView(BaseProductSaveView, UpdateView):
    """Operational processing node resolving configuration tuning parameters directly on pre-existing database records."""
    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=self.kwargs['pk'])
    

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse


class ProductFormsetMixin:
    """
    Mixin to handle shared logic between Create and Edit views for injecting
    and processing Product Variant and Image Inline Formsets.
    """
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('dashboard:product-list')  # Adjust to match your URL namespace

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['variant_formset'] = ProductVariantFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object, 
                prefix='variants'
            )
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object, 
                prefix='images'
            )
        else:
            context['variant_formset'] = ProductVariantFormSet(
                instance=self.object, 
                prefix='variants'
            )
            context['image_formset'] = ProductImageFormSet(
                instance=self.object, 
                prefix='images'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        variant_formset = context['variant_formset']
        image_formset = context['image_formset']

        # Wrap database operations in an atomic transaction
        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            with transaction.atomic():
                # 1. Save the main product instance
                self.object = form.save()
                
                # 2. Link the product instance to formsets and save
                variant_formset.instance = self.object
                variants = variant_formset.save()
                
                image_formset.instance = self.object
                image_formset.save()

                # 💡 Handle newly injected Attribute values built dynamically inside the UI chips
                self.process_custom_attributes(variant_formset)

            messages.success(self.request, "Product saved successfully!")
            return redirect(self.get_success_url())
        else:
            # If formsets are invalid, call form_invalid to re-render context with errors
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error saving your product. Please check the fields below.")
        return self.render_to_response(self.get_context_data(form=form))

    def process_custom_attributes(self, variant_formset):
        """
        Processes your dynamic attribute chips. This reads submitted data to assign
        existing database instances or create brand new variants on the fly.
        """
        for i, form in enumerate(variant_formset.forms):
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                variant_instance = form.instance
                
                # Capture custom fields sent dynamically by the frontend script engine
                # format expected: e.g., "variants-0-attribute_values"
                raw_attr_data = self.request.POST.get(f'variants-{i}-attribute_values')
                
                if raw_attr_data:
                    # Clear previously assigned values for clean management updates
                    variant_instance.attribute_values.clear()
                    
                    # Expecting comma-separated or JSON formatted IDs/values from your UI layer
                    # Update this block to match how your clean JSON stringifies keys:
                    attr_identifiers = [x.strip() for x in raw_attr_data.split(',') if x.strip()]
                    
                    for identifier in attr_identifiers:
                        if identifier.isdigit():
                            # Existing base database reference match key
                            variant_instance.attribute_values.add(int(identifier))
                        # Optional logic: Handle automated string creation rules if passed here


class ProductCreateView(ProductFormsetMixin, CreateView):
    template_name = 'dashboard/products/form.html'  # Adjust to your exact path

    def get_object(self, queryset=None):
        return None


class ProductUpdateView(ProductFormsetMixin, UpdateView):
    template_name = 'dashboard/products/form.html'  # Adjust to your exact path


# =====================================================
# CLEAN AJAX ENDPOINT VIEW
# =====================================================
def ajax_attributes_by_type(request):
    attr_type = request.GET.get('type')
    
    if not attr_type:
        return JsonResponse({"attributes": []}, status=200)
        
    attributes = ProductAttribute.objects.filter(category=attr_type)
    
    return JsonResponse({
        "attributes": [
            {
                "id": attr.id,
                "label": f"{attr.label_en or ''} - {attr.value_en or ''}".strip(" - ")
            }
            for attr in attributes
        ]
    }, status=200)

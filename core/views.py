import json
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic import (
    View, TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum, Count

from .models import *
from .forms import *
from .filters import *
from .resourses import *
from .utils import render_to_pdf


class SellProductSearch(View):
    def post(self, request, *args, **kwargs):
        search_str = json.loads(request.body).get('searchSells')

        sells = SellProduct.objects.filter(
            product_name__product_name__contains=search_str, is_active=True
        ) | SellProduct.objects.filter(
            sack__istartswith=search_str, is_active=True
        ) | SellProduct.objects.filter(
            customer_name__contains=search_str, is_active=True
        ) | SellProduct.objects.filter(
            token_number__exact=search_str, is_active=True
        ) | SellProduct.objects.filter(
            date_added__icontains=search_str, is_active=True
        )
        data = sells.values()
        return JsonResponse(list(data), safe=False)


class PurchaseProductSearch(View):
    def post(self, request, *args, **kwargs):
        search_str = json.loads(request.body).get('searchPurchases')

        purchases = PurchaseProduct.objects.filter(
            chalan_number__exact=search_str, is_active=True
        ) | PurchaseProduct.objects.filter(
            supplier__name__icontains=search_str, is_active=True
        ) | PurchaseProduct.objects.filter(
            date_added__icontains=search_str, is_active=True
        )

        suppliers = Supplier.objects.filter(is_active=True)

        purchases = purchases.values()
        suppliers = suppliers.values()

        data = {
            'purchases': list(purchases),
            'suppliers': list(suppliers)
        }
        return JsonResponse(data, safe=False)


class SupplierSearch(View):
    def post(self, request, *args, **kwargs):
        search_str = json.loads(request.body).get('searchSupplier')

        purchases = Supplier.objects.filter(
            name__icontains=search_str, is_active=True
        ) | Supplier.objects.filter(
            phone__exact=search_str, is_active=True
        )

        data = purchases.values()
        return JsonResponse(list(data), safe=False)


class ChartView(TemplateView, LoginRequiredMixin, UserPassesTestMixin):
    template_name = 'charts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Stock.objects.filter(is_active=True)
        context["sells"] = SellProduct.objects.filter(is_active=True)
        context["purchases"] = PurchaseProduct.objects.filter(is_active=True)
        return context

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


@login_required()
def sell_invoice(request, *args, **kwargs):
    pk = kwargs.get('pk')
    sell = get_object_or_404(SellProduct, pk=pk)

    template_path = 'sell-invoice.html'
    context = {'sell': sell}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if we want to download the pdf :
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if we want to display the pdf :
    filename = f'invoice-{pk}'
    response['Content-Disposition'] = f'filename="{filename}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required()
def contact(request):
    if request.method == 'POST':
        form = HelpcenterForm(request.POST or None)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            recipients = ['miclee0312@gmail.com']
            send_mail(subject, message, email, recipients)
            messages.success(request, 'Email successfully sent.')
        else:
            messages.warning(
                request, 'Something went wrong. Please try again.')
    form = HelpcenterForm()

    context = {
        'title': 'Contact',
        'form': form
    }
    return render(request, 'contact.html', context)


class PurchaseProductReportView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    def get(self, request, *args, **kwargs):
        last_month = datetime.today() - timedelta(days=30)
        # check for filter
        if self.request.GET and not self.request.GET.get('download'):
            # if filtered
            queryset = PurchaseProduct.objects.filter(is_active=True)
        else:
            # if not filtered
            queryset = PurchaseProduct.objects.filter(
                is_active=True, date_added__gte=last_month)

        query_filter = PurchaseProductFilter(self.request.GET, queryset)
        qs = query_filter.qs

        # report summary
        searched_for = {}
        if self.request.GET:
            date = self.request.GET.get('date_added')
            if date:
                searched_for['date'] = date

            start_date = self.request.GET.get('start_date')
            if start_date:
                searched_for['start date'] = start_date

            end_date = self.request.GET.get('end_date')
            if end_date:
                searched_for['end date'] = end_date

        if len(searched_for) <= 0:
            searched_for['start date'] = last_month

        # generate PDF
        download = request.GET.get('download')
        if download:
            template = get_template('purchase_report_pdf.html')
            pdf_context = {
                'qs': qs,
                'office': Office.objects.first(),
                'grand_total_price': sum([item.total_purchase_price for item in qs]),
                'searched_for': searched_for,
            }
            html = template.render(pdf_context)
            pdf = render_to_pdf('purchase_report_pdf.html', pdf_context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = 'Purchase-Report'
                content = f"inline; filename={filename}"
                download = request.GET.get('download')
                content = f"attachment; filename={filename}"
                response['Content-Disposition'] = content
                return response

        context = {
            'grand_total_price': sum([item.total_purchase_price for item in qs]),
            'title': 'Purchase Report',
            'PurchaseProduct': PurchaseProduct(),
            'filter': qs,
            'searched_for': searched_for,
        }
        return render(request, 'purchase_report.html', context)

    def test_func(self, *args, **kwargs):
        if self.request.user.is_staff:
            return True
        return False


class SellProductReportView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    def get(self, request, *args, **kwargs):
        last_month = datetime.today() - timedelta(days=30)
        # check for filter
        if self.request.GET and not self.request.GET.get('download'):
            # if filtered
            queryset = SellProduct.objects.filter(is_active=True)
        else:
            # if not filtered
            queryset = SellProduct.objects.filter(
                is_active=True, date_added__gte=last_month)

        query_filter = SellProductFilter(self.request.GET, queryset)
        qs = query_filter.qs

        sack_count = {
            'sack5': qs.filter(sack=5).count(),
            'sack35': qs.filter(sack=35).count(),
            'sack37': qs.filter(sack=37).count(),
            'sack50': qs.filter(sack=50).count(),
            'sack55': qs.filter(sack=55).count(),
            'sack60': qs.filter(sack=60).count()
        }

        # report summary
        searched_for = {}
        if self.request.GET:
            customer_name = self.request.GET.get('customer_name')
            if customer_name:
                searched_for['customer name'] = customer_name

            token = self.request.GET.get('token_number')
            if token:
                searched_for['token'] = token

            product_name = self.request.GET.get('product_name')
            if product_name:
                searched_for['product name'] = product_name

            date = self.request.GET.get('date_added')
            if date:
                searched_for['date'] = date

            start_date = self.request.GET.get('start_date')
            if start_date:
                searched_for['start date'] = start_date

            end_date = self.request.GET.get('end_date')
            if end_date:
                searched_for['end date'] = end_date

        if len(searched_for) <= 0:
            searched_for['start date'] = last_month

        # generate PDF
        download = request.GET.get('download')
        if download:
            template = get_template('sell_report_pdf.html')
            pdf_context = {
                'qs': qs,
                'office': Office.objects.first(),
                'total_sell': sum([item.get_total_amount for item in qs]),
                'total_paid': sum([item.paid_amount for item in qs]),
                'total_due': sum([item.get_due_amount for item in qs]),
                'searched_for': searched_for,
                # 'sack_count': sack_count
            }
            html = template.render(pdf_context)
            pdf = render_to_pdf('sell_report_pdf.html', pdf_context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = 'Report'
                content = f"inline; filename={filename}"
                download = request.GET.get('download')
                content = f"attachment; filename={filename}"
                response['Content-Disposition'] = content
                return response

        context = {
            'total_sell': sum([item.get_total_amount for item in qs]),
            'total_paid': sum([item.paid_amount for item in qs]),
            'total_due': sum([item.get_due_amount for item in qs]),
            'title': 'Sale Report',
            'sellproductFilter': SellProductFilter(),
            'filter': qs,
            'searched_for': searched_for,
            'sack_count': sack_count,
        }
        return render(request, 'sell_report.html', context)

    def test_func(self, *args, **kwargs):
        if self.request.user.is_staff:
            return True
        return False


class SellReportView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def get(self, request, *args, **kwargs):
        f = SellProductFilter(
            self.request.GET, queryset=SellProduct.objects.filter(is_active=True))
        # sells = SellProduct.objects.all(is_active=True)
        context = {
            # 'filter': f,
            'filter': f,
            'title': 'Sell Report Chart',
        }
        return render(self.request, 'sell_report_chart.html', context)

    def test_func(self, *args, **kwargs):
        if self.request.user.is_staff:
            return True
        return False


class HomeView(LoginRequiredMixin,
               ListView):
    template_name = 'index.html'
    model = Stock
    queryset = Stock.objects.filter(is_active=True)
    context_object_name = 'stocks'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Stock.objects.filter(is_active=True)
        context["sells"] = SellProduct.objects.filter(is_active=True)
        context["total_stocks"] = Stock.objects.filter(is_active=True).count()
        context["total_sells"] = SellProduct.objects.filter(
            is_active=True).count()
        context["total_purchases"] = PurchaseProduct.objects.filter(
            is_active=True).count()
        return context


class UserManagement(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, *args, **kwargs):
        users = User.objects.all()
        context = {
            'users': users,
            'title': 'User Management',
        }
        return render(self.request, 'users.html', context)

    def test_func(self, *args, **kwargs):
        if self.request.user.is_staff:
            return True
        return False


class EditUserManagent(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserPermissionForm
    template_name = 'edit-user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = 'user'
    success_message = "Changes saved successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit User'
        return context

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return True
        return False


class SupplierCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    model = Supplier
    template_name = 'supplier.html'

    def get(self, *args, **kwargs):
        queryset = Supplier.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            suppliers = paginator.page(page)
        except PageNotAnInteger:
            suppliers = paginator.page(1)
        except EmptyPage:
            suppliers = paginator.page(paginator.num_pages)

        context = {
            'suppliers': suppliers,
            'page_obj': suppliers,
            'title': 'New Supplier',
            'form': SupplierCreateForm()
        }

        return render(self.request, 'supplier.html', context)

    def post(self, *args, **kwargs):
        form = SupplierCreateForm(self.request.POST or None)

        if form.is_valid():
            form.save()

            messages.success(self.request, 'Supplier created successfully')
            return redirect('supplier')

        messages.warning(self.request, 'Invalid form')
        return redirect('supplier')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SupplierModalCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    queryset = Supplier.objects.all()
    form_class = SupplierCreateForm
    success_url = 'purchase'
    success_message = "%(name)s was created successfully"

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class PurchaseProductCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    model = PurchaseProduct
    template_name = 'purchase.html'

    def get(self, *args, **kwargs):
        queryset = PurchaseProduct.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            purchases = paginator.page(page)
        except PageNotAnInteger:
            purchases = paginator.page(1)
        except EmptyPage:
            purchases = paginator.page(paginator.num_pages)

        context = {
            'purchases': purchases,
            'page_obj': purchases,
            'title': 'New Purchase',
            'form': PurchaseCreateForm(),
            'supplier_form': SupplierCreateForm()
        }

        return render(self.request, 'purchase.html', context)

    def post(self, *args, **kwargs):
        form = PurchaseCreateForm(self.request.POST or None)

        if form.is_valid():
            new_purchase = form.save(commit=False)
            new_purchase.added_by = self.request.user
            new_purchase.save()

            messages.success(
                self.request, f'{new_purchase.product_name} created successfully')
            return redirect('purchase')

        messages.warning(self.request, 'Invalid form')
        return redirect('purchase')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class StockCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    model = Stock
    template_name = 'stock.html'

    def get(self, *args, **kwargs):
        queryset = Stock.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            stocks = paginator.page(page)
        except PageNotAnInteger:
            stocks = paginator.page(1)
        except EmptyPage:
            stocks = paginator.page(paginator.num_pages)

        context = {
            'stocks': stocks,
            'page_obj': stocks,
            'title': 'New Stock',
            'form': StockCreateForm()
        }

        return render(self.request, 'stock.html', context)

    def post(self, *args, **kwargs):
        form = StockCreateForm(self.request.POST or None)

        if form.is_valid():
            new_stock = form.save(commit=False)
            new_stock.added_by = self.request.user
            new_stock.save()

            messages.success(
                self.request, f'{new_stock.product_name} created successfully')
            return redirect('stock')

        messages.warning(self.request, 'Invalid form')
        return redirect('stock')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SellsListView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, ListView):
    model = SellProduct
    # queryset = SellProduct.objects.filter(is_staff=True)
    context_object_name = 'sells'
    template_name = 'sell.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Sales'
        return context

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SellProductCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = SellProduct
    form_class = SellProductCreateForm
    template_name = 'sell-create.html'
    success_url = 'sell-create'
    success_message = "%(product_name)s was created successfully"

    def post(self, *args, **kwargs):
        form = SellProductCreateForm(self.request.POST or None)

        if self.request.is_ajax():
            if form.is_valid():
                product_name = form.cleaned_data.get('product_name')
                product_instance = get_object_or_404(
                    Stock, product_name=product_name)
                quantity = form.cleaned_data.get('quantity')

                if quantity <= product_instance.quantity:
                    sell = form.save(commit=False)
                    sell.added_by = self.request.user
                    sell.save()

                    new_qntty = product_instance.quantity - quantity
                    product_instance.quantity = new_qntty
                    product_instance.save(update_fields=['quantity'])

                return JsonResponse({'msg': f'{product_instance.product_name} sold successfully'})
            else:
                return JsonResponse({'msg': form.errors.as_data()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Sale'
        context["hasAjax"] = True
        return context

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SellProductByID(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def get(self, *args, **kwargs):
        product_instance = get_object_or_404(Stock, pk=self.kwargs['pk'])
        form = SellProductCreateForm(instance=product_instance, initial={
            'product_name': product_instance
        })
        context = {
            'form': form,
            'title': 'New Sale',
        }
        return render(self.request, 'sell-create.html', context)

    def post(self, *args, **kwargs):
        product_instance = get_object_or_404(Stock, pk=self.kwargs['pk'])
        form = SellProductCreateForm(self.request.POST or None)

        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')

            if quantity <= product_instance.quantity:
                sell = form.save(commit=False)
                sell.added_by = self.request.user
                sell.save()

                new_qntty = product_instance.quantity - quantity
                product_instance.quantity = new_qntty
                product_instance.save(update_fields=['quantity'])
                messages.success(
                    self.request, f'{product_instance.product_name} sold successfully')
                return redirect('sell-list')
            else:
                messages.warning(self.request, 'Invalid Qunatity')
                return redirect('./')
        else:
            messages.warning(self.request, 'Invalid Form')
            return redirect('./')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


# ============ update view ===========

class SupplierUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierCreateForm
    template_name = 'supplier.html'
    success_url = 'supplier'
    success_message = "%(name)s was updated successfully"

    def get(self, *args, **kwargs):
        queryset = Supplier.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            suppliers = paginator.page(page)
        except PageNotAnInteger:
            suppliers = paginator.page(1)
        except EmptyPage:
            suppliers = paginator.page(paginator.num_pages)

        context = {
            'suppliers': suppliers,
            'page_obj': suppliers,
            'title': 'New Supplier',
            'form': SupplierCreateForm(instance=self.get_object())
        }

        return render(self.request, 'supplier.html', context)

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class PurchaseProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = PurchaseProduct
    form_class = PurchaseCreateForm
    template_name = 'purchase.html'
    success_url = 'purchase'
    success_message = "%(product_name)s was updated successfully"

    def get(self, *args, **kwargs):
        queryset = PurchaseProduct.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            purchases = paginator.page(page)
        except PageNotAnInteger:
            purchases = paginator.page(1)
        except EmptyPage:
            purchases = paginator.page(paginator.num_pages)

        context = {
            'purchases': purchases,
            'page_obj': purchases,
            'title': 'New Purchase',
            'form': PurchaseCreateForm(instance=self.get_object()),
            'supplier_form': SupplierCreateForm()
        }

        return render(self.request, 'purchase.html', context)

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class StockUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Stock
    form_class = StockCreateForm
    template_name = 'stock.html'
    success_url = 'stock'
    success_message = "%(product_name)s was updated successfully"

    def get(self, *args, **kwargs):
        queryset = Stock.objects.filter(is_active=True)
        page = self.request.GET.get('page', 1)

        paginator = Paginator(queryset, 20)

        try:
            stocks = paginator.page(page)
        except PageNotAnInteger:
            stocks = paginator.page(1)
        except EmptyPage:
            stocks = paginator.page(paginator.num_pages)

        context = {
            'stocks': stocks,
            'page_obj': stocks,
            'title': 'New Stock',
            'form': StockCreateForm(instance=self.get_object())
        }

        return render(self.request, 'stock.html', context)

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class SellProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = SellProduct
    form_class = SellProductCreateForm
    template_name = 'sell-create.html'
    success_url = 'sell-list'
    success_message = "%(product_name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Sale'
        return context

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


# ========== delete views ==============

class SupplierDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Supplier
    template_name = 'supplier.html'
    success_url = 'supplier'
    success_message = "%(name)s was deleted successfully"

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class PurchaseProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = PurchaseProduct
    template_name = 'purchase.html'
    success_url = 'purchase'
    success_message = "%(name)s was deleted successfully"

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class StockDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Stock
    template_name = 'stock.html'
    success_url = 'stock'
    success_message = "%(name)s was deleted successfully"

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class SellProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = SellProduct
    template_name = 'sell.html'
    success_url = 'sell-list'
    success_message = "%(name)s was deleted successfully"

    def get_success_url(self, **kwargs):
        return reverse(self.success_url)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

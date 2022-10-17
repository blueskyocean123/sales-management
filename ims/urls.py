from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from core.views import *

urlpatterns = [
    # admin
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secret-panel/', admin.site.urls),
    # auth
    path('accounts/', include('allauth.urls')),
    # help
    path('contact/', contact, name='contact'),
    # home & user management
    path('', HomeView.as_view(), name='home'),
    path('users/', UserManagement.as_view(), name='user'),
    path('user/<username>/', EditUserManagent.as_view(), name='user-edit'),
    # Suppliers url
    path('purchase/suppliers/', SupplierModalCreate.as_view(), name='supplier-modal'),
    path('suppliers/', SupplierCreateView.as_view(), name='supplier'),
    path('suppliers/<int:pk>/', SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/delete/<int:pk>/',
         SupplierDeleteView.as_view(), name='supplier-delete'),
    # Purchases urls
    path('purchases/', PurchaseProductCreateView.as_view(), name='purchase'),
    path('purchases/report', PurchaseProductReportView.as_view(),
         name='purchase-report'),
    path('purchase/<int:pk>/', PurchaseProductUpdateView.as_view(),
         name='purchase-update'),
    path('purchase/delete/<int:pk>/',
         PurchaseProductDeleteView.as_view(), name='purchase-delete'),
    # stocks urls
    path('stocks/', StockCreateView.as_view(), name='stock'),
    path('stocks/<int:pk>/', StockUpdateView.as_view(), name='stock-update'),
    path('stocks/delete/<int:pk>/', StockDeleteView.as_view(), name='stock-delete'),
    # sells urls
    path('sells/list/', SellsListView.as_view(), name='sell-list'),
    path('sells/', SellProductCreateView.as_view(), name='sell-create'),
    path('sells/<int:pk>/', SellProductUpdateView.as_view(), name='sell-update'),
    path('sells/product/<int:pk>/', SellProductByID.as_view(),
         name='sell-product-by-id'),
    path('sells/delete/<int:pk>/',
         SellProductDeleteView.as_view(), name='sell-delete'),
    # sells report urls
    path('sells/report/', SellProductReportView.as_view(), name='sell-report'),
    path('sells/report/<download>',
         SellProductReportView.as_view(), name='sell-report-pdf'),
    path('sells/invoice/<int:pk>', sell_invoice, name='sell-invoice'),
    # charts urls
    path('charts/', ChartView.as_view(), name='charts'),
    path('sells/chart/', SellReportView.as_view(), name='report'),
    # search endpoints
    path('sells/search', csrf_exempt(SellProductSearch.as_view()), name="sells-search"),
    path('purchases/search', csrf_exempt(PurchaseProductSearch.as_view()),
         name="purchases-search"),
    path('supplier/search', csrf_exempt(SupplierSearch.as_view()),
         name="supplier-search"),
]

admin.site.site_header = 'Sales Manager Panel'
admin.site.index_title = 'Sales Manager'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

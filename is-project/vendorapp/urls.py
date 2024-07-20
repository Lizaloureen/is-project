from django.urls import path

from vendorapp.views import FirearmsView, VendorProfileView

urlpatterns = [
  path('profile', VendorProfileView.as_view({"get": 'get_profile'}), name='vendor-profile'),
  path('profile/update', VendorProfileView.as_view({"post": 'update'}), name='vendor-profile-update'),

  path('firearms/count', FirearmsView.as_view({"get": 'fa_count'}), name='vendor-firearms-count'),
  path('firearms', FirearmsView.as_view({"get": 'list'}), name='vendor-firearms'),
  path('firearms/add', FirearmsView.as_view({"post": 'create'}), name='vendor-firearms-add'),
  path('firearms/edit/<int:id>', FirearmsView.as_view({"post": 'update'}), name='vendor-firearms-update'),
  path('firearms/issue', FirearmsView.as_view({"post": 'issue_firearm'}), name='vendor-firearms-issue'),
  path('firearms/return', FirearmsView.as_view({"post": 'return_firearm'}), name='vendor-firearms-return'),
]
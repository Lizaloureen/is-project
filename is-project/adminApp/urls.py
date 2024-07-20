from django.urls import path

from adminApp.views import ClientView, ClientsApplicationsView, FirearmsView, LicenceView, StatView, VendorsView

urlpatterns = [
    path('stats', StatView.as_view({'get':'list'}), name='stats'),
    path('stats/firearms-dist', StatView.as_view({'get':'firearms_dist'}), name='firearms-dist'),
    path('stats/app-dist', StatView.as_view({'get':'app_dist'}), name='app_dist'),
    path('clients', ClientView.as_view({'get':'list'}), name='clients'),
    path('vendors', VendorsView.as_view({'get':'list'}), name='vendors'),
    path('applications', ClientsApplicationsView.as_view({'get':'list'}), name='applications'),
    path('applications/reject', ClientsApplicationsView.as_view({'post':'reject'}), name='applications-reject'),
    path('applications/approve_interview', ClientsApplicationsView.as_view({'post':'approve_interview'}), name='applications-approve-interview'),
    path('applications/approve', ClientsApplicationsView.as_view({'post':'approve'}), name='applications-approve'),

    path('licences', LicenceView.as_view({'get': 'list'}), name='licences'),
    path('licences/confirm_payment', LicenceView.as_view({'post': 'confirm_payment'}), name='licences-confirm_payment'),
    path('licences/change_status', LicenceView.as_view({'post': 'change_status'}), name='licences-change_status'),
    
    path('firearms', FirearmsView.as_view({'get':'list'}), name='firearms'),
    path('firearms/add', FirearmsView.as_view({'post':'create'}), name='firearms-add'),
    path('firearms/change_status', FirearmsView.as_view({'post':'change_status'}), name='firearms-change_status'),
    path('firearms/approve', FirearmsView.as_view({'post':'approve'}), name='firearms-approve'),
    path('firearms/issue_firearm', FirearmsView.as_view({'post':'issue_firearm'}), name='firearms-issue_firearm'),
    path('firearms/return_firearm', FirearmsView.as_view({'post':'return_firearm'}), name='firearms-return_firearm'),
]
from django.urls import path

from clientapp.views import ClientApplicationView, ClientFirearmsView, ClientLicenceView, ClientProfileView, StatsView

urlpatterns = [
    path('dash-stats', StatsView.as_view({'get': 'stats'}), name='start'),
    path('profile', ClientProfileView.as_view({'get': 'get_profile'}), name='get_profile'),
    path('update-profile', ClientProfileView.as_view({'post': 'update'}), name='update_profile'),

    path('applications', ClientApplicationView.as_view({'get': 'get_applications'}), name='get_applications'),
    path('applications/stats', ClientApplicationView.as_view({'get': 'get_application_stats'}), name='get_application_stats'),
    path('apply', ClientApplicationView.as_view({'post': 'create'}), name='apply'),
    path('renew', ClientApplicationView.as_view({'post': 'renew'}), name='apply-renew'),

    path('firearms', ClientFirearmsView.as_view({'get': 'get_client_firearms'}), name='get_firearms'),
    path('firearms/stat', ClientFirearmsView.as_view({'get': 'firearm_stats'}), name='stats'),
    path('firearms/<int:id>', ClientFirearmsView.as_view({'get': 'details'}), name='firearm_details'),

    path('licences', ClientLicenceView.as_view({'get': 'list'}), name='licences'),
    path('licences/renew', ClientLicenceView.as_view({'post': 'renew'}), name='licences-renew'),

]
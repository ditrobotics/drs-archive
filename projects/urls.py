from django.conf.urls import url, patterns

from projects import views


urlpatterns = patterns('',
    url(r'^create/$', views.ProjectCreate.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', views.ProjectUpdate.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', views.ProjectDelete.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/cover_photo/$', views.cover_photo, name='cover-photo'),
)

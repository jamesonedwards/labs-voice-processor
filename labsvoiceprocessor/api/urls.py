from django.conf.urls.defaults import patterns, url
from django.conf import settings

urlpatterns = patterns('api.views',
    url(r'^listfiles/$', 'listfiles', name='listfiles'),
    url(r'^testupload/$', 'testupload', name='testupload'),
    url(r'^savefile/$', 'savefile', name='savefile')    
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
	path("login", views.login_view, name="login"),
	path("logout", views.logout_view, name="logout"),
	path("register", views.register, name="register"),
	path("addcart", views.addcart, name="addcart"),
	path("removecart", views.removecart, name="removecart"),
	path("displaycart", views.displaycart, name="displaycart"),
	path('coursereview/<int:idcourse>', views.coursereview, name="coursereview"),
	path('coursereview', views.coursereview, name="coursereview"),
    path('showpurchase', views.showpurchase, name="showpurchase"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

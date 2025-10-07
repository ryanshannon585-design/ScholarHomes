"""auth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AuthExample import views
from AuthExample.forms import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views 


urlpatterns = [
    path('', views.index, name="home"),
    path('admin/', admin.site.urls),
    path('registerstudent/', views.StudentSignupView, name='student_register'),
    path('registerPropLister/', views.PropListerSignupView, name="register_PropLister"),
    path('login/',views.LoginView.as_view(template_name="login.html", authentication_form=UserLoginForm)),
    path('logout/', views.logout_user, name="logout"),
    path('properties/', views.property_list, name='property_list'),
    path('apply/<int:property_id>/', views.apply_for_rent, name='apply_for_rent'),
    path('ApplicationSuccessful/', views.application_successful, name='application_successful'),
    path('RegistrationSuccessful/', views.registration_successful, name='registration_successful'),
    path('CreateListing/', views.create_listing, name='create_listing'),
    path('Listing_hub/', views.Listing_hub, name='Listing_hub'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('properties/<int:prodid>', views.property_individual, name="Property_individual"),
    path('view_profile/<int:user_id>', views.view_profile, name="view_profile"),
    path('accept_applicant/<int:application_id>/', views.accept_applicant, name='accept_applicant'),
    path('decline_applicant/<int:application_id>/', views.decline_applicant, name='decline_applicant'),
    path('follow/<int:followed_user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:followed_user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers/<int:user_id>/', views.followers_view, name='followers'),
    path('following/<int:user_id>/', views.following_view, name='following'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_application/<int:application_id>/', views.delete_application, name='delete_application'),
    path('delete_property/<int:property_id>/', views.delete_property, name='delete_property'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#view_my_profile
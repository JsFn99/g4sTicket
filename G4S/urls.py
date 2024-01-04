"""
URL configuration for G4S project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from ticketmam.views import (
    index,
    login_user,
    logout_view,
    my_tickets,
    profil,
    signup,
    activity,
    ticket_detail_view,
    terminate_ticket,
    my_contacts,
    detail_contact,
    create_report,
    report_detail,
    report_list,
    stat,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("profil/", profil, name="profil"),
    path("login/", login_user, name="login"),
    path("signup/", signup, name="signup"),
    path("logout/", logout_view, name="logout"),
    path("my_tickets/", my_tickets, name="my_tickets"),
    path("activity", activity, name="activity"),
    path("ticket/<int:pk>/", ticket_detail_view, name="ticket_detail_view"),
    path("terminate_ticket/<int:ticket_id>/", terminate_ticket, name="terminate_ticket"),
    path("my_contacts/", my_contacts, name="my_contacts"),
    path("detail_contact/<int:pk>/", detail_contact, name="detail_contact"),
    path("report/", create_report, name="report"),
    path("report_list/", report_list, name="report_list"),
    path("report_detail/<int:pk>/", report_detail, name="report_detail"),
    path("stat/", stat, name="stat"),
]

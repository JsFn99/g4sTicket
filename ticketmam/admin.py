from django.contrib import admin

from .models import Agent, SiteIntervention, Ticket, Client

admin.site.register(Agent)
admin.site.register(SiteIntervention)
admin.site.register(Ticket)
admin.site.register(Client)

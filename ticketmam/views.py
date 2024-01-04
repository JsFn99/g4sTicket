import datetime
from django.utils import timezone
import json
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models.functions import TruncMonth
from plotly.offline import plot
import plotly.graph_objs as go
from ticketmam.models import Agent, Ticket, SiteIntervention,Client,Report

# Create your views here.

User = get_user_model()


def index(request):
    if not request.user.is_authenticated:
        return redirect('login') 

    user = request.user
    user_agent = Agent.objects.get(username=user.username)

    current_tickets_count = Ticket.objects.filter(agent=user_agent, etat='En Cours').count()

    cities_count = SiteIntervention.objects.filter(ticket__agent=user_agent, ticket__etat='En Cours').annotate(
        num_tickets=Count('ticket')
    ).count()

    context = {
        'agent': user_agent,
        'current_tickets_count': current_tickets_count,
        'cities_count': cities_count,
    }
    return render(request, 'ticket/index.html', {'agent': user_agent})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        id_agent = request.POST.get("id_technicien")
        departement = request.POST.get("departement") 
        telephone = request.POST.get("telephone") 
        
        try:
            agent = Agent.objects.create_user(
                username=username,
                password=password,
                id_agent=id_agent,
                departement=departement,  
                telephone=telephone, 
            )
        except IntegrityError:
            return render(request, 'accounts/signup.html', {'error': 'ID already exists. Please enter a different ID.'})
        
        login(request, agent)
        return redirect('index')
    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    return redirect('index') 

@login_required
def profil(request):
    agent = request.user
    return render(request, 'ticket/profil.html', {'agent': agent})

@login_required
def my_tickets(request):
    agent = request.user

    if not isinstance(agent, Agent):
        raise ValueError("Current user is not an Agent instance")

    tickets = Ticket.objects.filter(agent=agent)

    context = {
        'tickets': tickets
    }
    return render(request, 'ticket/my_tickets.html', context)

@login_required
def activity(request):
    user = request.user
    user_tickets = Ticket.objects.filter(agent=user)  

    user_tickets_dates = []

    for ticket in user_tickets:
        user_tickets_dates.append({
            'title': ticket.titre,
            'start': ticket.dateAssignation.strftime('%Y-%m-%d'),  
            'url': reverse('ticket_detail_view', args=[ticket.id]),
        })

    context = {
        'user': user,
        'user_tickets_dates': json.dumps(user_tickets_dates),
    }

    return render(request, 'ticket/activite.html', context)

def ticket_detail_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    context = {'ticket': ticket}
    return render(request, 'ticket/detail.html', context)


def terminate_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    if ticket.etat != 'Termine':
        ticket.etat = 'Termine'
        
        now = timezone.localtime(timezone.now())
        # Convert dateAssignation to a datetime object with timezone information
        date_assignation_datetime = timezone.make_aware(datetime.datetime.combine(ticket.dateAssignation, datetime.time.min))
        duration = now - date_assignation_datetime
        ticket.dureeDeResolution = duration

        ticket.save()
    return redirect('ticket_detail_view', pk=ticket_id)

def my_contacts(request):
    clients = Client.objects.all()
    
    context = {
        'clients': clients,
    }
    
    return render(request, 'ticket/my_contacts.html', context)

def detail_contact(request, pk):
    client = get_object_or_404(Client, pk=pk)
    context = {'client': client}
    return render(request, 'ticket/detail_contact.html', context)

@login_required
def create_report(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        
        auteur = request.user  
        
        Report.objects.create(
            titre=titre,
            description=description,
            auteur=auteur,
            ticket=ticket
        )
        
        return redirect('report_list')
        
    tickets = Ticket.objects.filter(agent=request.user)
    context = {'tickets': tickets}
    return render(request, 'ticket/report.html', context)

def report_list(request):
    reports = Report.objects.filter(auteur=request.user)
    context = {'reports': reports}
    return render(request, 'ticket/report_list.html', context)

def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    context = {'report': report}
    return render(request, 'ticket/report_detail.html', context)


def stat(request):
    if request.user.is_authenticated:
        user = request.user

        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = current_month_start.replace(month=current_month_start.month % 12 + 1, day=1) - timezone.timedelta(days=1)
        
        assigned_tickets_counts = Ticket.objects.filter(agent=user, dateAssignation__gte=current_month_start, dateAssignation__lte=current_month_end) \
            .annotate(month=TruncMonth('dateAssignation')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        resolved_tickets_counts = Ticket.objects.filter(agent=user, etat='Termine', derniereMiseAJour__gte=current_month_start, derniereMiseAJour__lte=current_month_end) \
            .annotate(month=TruncMonth('derniereMiseAJour')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        assigned_graph = go.Figure(go.Bar(x=[item['month'] for item in assigned_tickets_counts],
                                          y=[item['count'] for item in assigned_tickets_counts],
                                          name='Assigned Tickets'))
        assigned_graph.update_layout(title_text='Vos tickets assignes ce mois')
        
        solved_graph = go.Figure(go.Bar(x=[item['month'] for item in resolved_tickets_counts],
                                        y=[item['count'] for item in resolved_tickets_counts],
                                        name='Solved Tickets'))
        solved_graph.update_layout(title_text='Vos tickets resolues ce mois')
        
        assigned_tickets_graph = assigned_graph.to_html(full_html=False)
        solved_tickets_graph = solved_graph.to_html(full_html=False)
        
        return render(request, 'ticket/stat.html', {'user': user, 'assigned_tickets_graph': assigned_tickets_graph, 'solved_tickets_graph': solved_tickets_graph})
    else:
        return redirect('login')
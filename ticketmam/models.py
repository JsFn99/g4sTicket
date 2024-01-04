import cv2
import qrcode
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

'''
Agent(AbstractUser):
    id_agent
    telephone
    departement
    nbrTickets
    nbrTicketsResolus
'''

class Agent(AbstractUser):
    id_agent = models.CharField(max_length=100, unique=True, verbose_name=_("ID"))
    telephone = models.CharField(max_length=15, verbose_name=_("Telephone"))
    departement = models.CharField(max_length=100, verbose_name=_("Departement"))
    nbrTickets = models.IntegerField(verbose_name=_("Nombre de tickets"),default=0)
    nbrTicketsResolus = models.IntegerField(verbose_name=_("Nombre de tickets resolus"),default=0)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="agents_groups",
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_query_name="agent",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="agents_user_permissions",
        help_text=_("Specific permissions for this user."),
        related_query_name="agent",
    )

    
'''
SiteIntervention:
    nom 
    adresse 
    ville 
    qrcode 
'''

class SiteIntervention(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=100, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    qrcode = models.ImageField(upload_to='qrcodes/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.nom
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qrcode.url)  
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_code_path = f'qrcodes/{self.nom}_qrcode.png'
        img.save(qr_code_path)

        return qr_code_path

    def validate_qr_code(self, qr_code_path):
        img = cv2.imread(qr_code_path)
        qr_code_reader = cv2.QRCodeDetector()
        retval, decoded_info, points, straight_qrcode = qr_code_reader.detectAndDecodeMulti(img)
        if retval:
            return decoded_info
        else:
            return None

  
    


'''
Tickect:
- Client 
- Site
- Demandeur
- Etat (Nouveau/Assignée/En Attente/Refuse/Resolu)
- Origine
- Titre
- Description
- Service
- Sous catégorie de service
- Ticket à surveiller (Oui/Non)
- Raison de surveillance
- Type de Requête
- Impact
- Urgence
- Priorité (Basse/Moyenne/Haute/Urgente)
- Equipe
- Agent 
- Approbateur 
- Date de début
- Dernière mise à jour
- Date d'assignation
- Echéance TTR
- Requête parente
- Changement parent
- Duree de resolution
'''


class Ticket(models.Model):
    client = models.CharField(max_length=100, verbose_name=_("Client"), blank=True)
    site_id = models.ForeignKey(SiteIntervention, on_delete=models.SET_NULL, null=True, verbose_name=_("Site"), blank=True)
    demandeur = models.CharField(max_length=100, verbose_name=_("Demandeur"), blank=True)
    etat = models.CharField(max_length=100, verbose_name=_("Etat"), blank=True)
    origine = models.CharField(max_length=100, verbose_name=_("Origine"), blank=True)
    titre = models.CharField(max_length=100, verbose_name=_("Titre"), blank=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    service = models.CharField(max_length=100, verbose_name=_("Service"), blank=True)
    sousCategorieService = models.CharField(max_length=100, verbose_name=_("Sous categorie de service"), blank=True)
    ticketASurveiller = models.CharField(max_length=100, verbose_name=_("Ticket a surveiller"), blank=True)
    raisonDeSurveillance = models.CharField(max_length=100, verbose_name=_("Raison de surveillance"), blank=True)
    typeDeRequete = models.CharField(max_length=100, verbose_name=_("Type de requete"), blank=True)
    impact = models.CharField(max_length=100, verbose_name=_("Impact"), blank=True)
    urgence = models.CharField(max_length=100, verbose_name=_("Urgence"), blank=True)
    priorite = models.CharField(max_length=100, verbose_name=_("Priorite"), blank=True)
    equipe = models.CharField(max_length=100, verbose_name=_("Equipe"), blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, verbose_name=_("Agent"), blank=True)
    approbateur = models.CharField(max_length=100, verbose_name=_("Approbateur"), blank=True)
    dateDebut = models.DateField(verbose_name=_("Date de debut"), blank=True)
    derniereMiseAJour = models.DateTimeField(auto_now=True, verbose_name=_("Derniere mise a jour"))
    dateAssignation = models.DateField(verbose_name=_("Date d'assignation"), blank=True)
    echeanceTTR = models.DateField(verbose_name=_("Echeance TTR"), blank=True)
    requeteParente = models.CharField(max_length=100, verbose_name=_("Requete parente"), blank=True)
    changementParent = models.CharField(max_length=100, verbose_name=_("Changement parent"), blank=True)
    dureeDeResolution = models.CharField(max_length=100, verbose_name=_("Duree de resolution"), blank=True)

    def __str__(self):
        return self.titre
     

'''
Client:
    nom
    adresse
    ville
    pays
    telephone
    email
'''   

class Client(models.Model):
    nom = models.CharField(max_length=100, verbose_name=_("Nom"), blank=True)
    adresse = models.CharField(max_length=100, verbose_name=_("Adresse"), blank=True)
    ville = models.CharField(max_length=100, verbose_name=_("Ville"), blank=True)
    pays = models.CharField(max_length=100, verbose_name=_("Pays"), blank=True)
    telephone = models.CharField(max_length=100, verbose_name=_("Telephone"), blank=True)
    email = models.CharField(max_length=100, verbose_name=_("Email"), blank=True)
    
    def __str__(self):
        return self.nom

'''
Report:
    titre
    description
    cree_le
    auteur
'''

class Report(models.Model):
    titre = models.CharField(max_length=100, verbose_name=_("Titre"))
    description = models.TextField( verbose_name=_("Description"),)
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name=_("Cree le"))
    auteur = models.ForeignKey(Agent, on_delete=models.CASCADE, verbose_name=_("Auteur"),)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name=_("Ticket"))

    def __str__(self):
        return self.titre
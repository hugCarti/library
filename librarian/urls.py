from django.urls import path
from .views import (index, list_member, create_member, update_member, list_media, create_media,
                    create_loan, list_active_loans, return_loan)

app_name = "librarian"
urlpatterns = [
    path('', index, name='index'),
    path('liste-membres/', list_member, name='list_member'),
    path('creer-membre/', create_member, name='create_member'),
    path('modifier-membre/<int:member_id>/', update_member, name='update_member'),
    path('liste-medias/', list_media, name='list_media'),
    path('creer-media/', create_media, name='create_media'),
    path('creer-emprunt/', create_loan, name='create_loan'),
    path('liste-emprunts/', list_active_loans, name='list_active_loans'),
    path('rendre-emprunt/<int:loan_id>/', return_loan, name='return_loan'),
]
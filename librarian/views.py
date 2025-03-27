from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Member, Media, Loan, Book, DVD, CD, BoardGame


def index(request):
    return render(request, 'librarian/index.html')


def list_member(request):
    members = Member.objects.all().prefetch_related('loan_set')
    for member in members:
        member.active_loans_count = member.loan_set.filter(date_return__isnull=True).count()
    return render(request, 'librarian/members_list.html', {'members': members})


def create_member(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Member.objects.create(name=name)
        return redirect('librarian:list_member')
    return render(request, 'librarian/create_member.html')


def update_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.blocked = 'blocked' in request.POST
        member.save()
        return redirect('librarian:list_member')
    return render(request, 'librarian/update_member.html', {'member': member})


def list_media(request):
    media_types = {
        'book': (Book.objects.all(), "Livre"),
        'dvd': (DVD.objects.all(), "DVD"),
        'cd': (CD.objects.all(), "CD"),
        'boardgame': (BoardGame.objects.all(), "Jeu de société")
    }

    allmedias = []
    for items, media_type in media_types.values():
        for item in items:
            item.type = media_type
            allmedias.append(item)

    return render(request, 'librarian/medias_list.html', {'allmedias': allmedias})


def create_media(request):
    if request.method == 'POST':
        media_type = request.POST.get('media_type')
        name = request.POST.get('name')

        if media_type == 'book':
            author = request.POST.get('author')
            Book.objects.create(name=name, author=author)
        elif media_type == 'dvd':
            producer = request.POST.get('producer')
            DVD.objects.create(name=name, producer=producer)
        elif media_type == 'cd':
            artist = request.POST.get('artist')
            CD.objects.create(name=name, artist=artist)
        elif media_type == 'boardgame':
            name = request.POST.get('name')
            creator = request.POST.get('creator')
            BoardGame.objects.create(name=name, creator=creator)

        return redirect('librarian:list_media')
    return render(request, 'librarian/create_media.html')


def create_loan(request):
    if request.method == 'POST':
        member_id = request.POST.get('member')
        media_id = request.POST.get('media')

        member = get_object_or_404(Member, id=member_id)
        media = get_object_or_404(Media, id=media_id)

        # Vérifications des contraintes
        if member.blocked:
            messages.error(request, "Ce membre est bloqué et ne peut pas emprunter.")
            return redirect('librarian:create_loan')

        if Loan.objects.filter(member=member, date_return__isnull=True).count() >= 3:
            messages.error(request, "Ce membre a déjà 3 emprunts en cours.")
            return redirect('librarian:create_loan')

        if not media.available:
            messages.error(request, "Ce média n'est pas disponible.")
            return redirect('librarian:create_loan')

        Loan.objects.create(
            media=media,
            member=member,
            date_loan=timezone.now().date()
        )
        media.available = False
        media.save()

        return redirect('librarian:index')

    members = Member.objects.filter(blocked=False)
    medias = Media.objects.filter(available=True)
    return render(request, 'librarian/create_loan.html', {
        'members': members,
        'medias': medias
    })


def return_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if loan.date_return is None:
        loan.date_return = timezone.now().date()
        loan_duration = (loan.date_return - loan.date_loan).days

        if loan_duration > 7:
            loan.member.blocked = True
            loan.member.save()
            messages.warning(request, "Membre bloqué pour retard de retour")

        loan.media.available = True
        loan.media.save()
        loan.save()

    return redirect('librarian:index')
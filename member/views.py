from django.shortcuts import render
from librarian.models import Book, DVD, CD, BoardGame


def list_media(request):
    media_types = {
        'book': (Book.objects.all(), "Livre"),
        'dvd': (DVD.objects.all(), "DVD"),
        'cd': (CD.objects.all(), "CD"),
        'boardgame': (BoardGame.objects.all(), "Jeu de société")
    }

    medias = []
    for items, media_type in media_types.values():
        for item in items:
            item.type = media_type
            medias.append(item)

    return render(request, 'member/member-medias_list.html', {'medias': medias})

from django.contrib import admin
from .models import Member, Media, Book, DVD, CD, BoardGame, Loan


class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'blocked', 'loan_count')
    list_filter = ('blocked',)
    search_fields = ('name',)

    def loan_count(self, obj):
        return obj.loan_set.count()

    loan_count.short_description = 'Emprunts en cours'


class MediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'media_type', 'available')
    list_filter = ('available',)
    search_fields = ('name',)

    def media_type(self, obj):
        if hasattr(obj, 'book'):
            return "Livre"
        elif hasattr(obj, 'dvd'):
            return "DVD"
        elif hasattr(obj, 'cd'):
            return "CD"
        return "Média"

    media_type.short_description = 'Type'


class LoanAdmin(admin.ModelAdmin):
    list_display = ('member', 'media_display', 'date_loan', 'date_return', 'is_overdue')
    list_filter = ('date_loan', 'date_return')
    search_fields = ('member__name', 'media__name')

    def media_display(self, obj):
        return obj.media.name

    media_display.short_description = 'Média'

    def is_overdue(self, obj):
        return obj.is_overdue()

    is_overdue.boolean = True
    is_overdue.short_description = 'En retard'


# Enregistrement des modèles
admin.site.register(Member, MemberAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Book, MediaAdmin)
admin.site.register(DVD, MediaAdmin)
admin.site.register(CD, MediaAdmin)
admin.site.register(BoardGame)
admin.site.register(Loan, LoanAdmin)
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Member(models.Model):
    name = models.CharField(max_length=100)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def can_borrow(self):
        if self.blocked:
            return False

        # Vérifier les emprunts en retard
        overdue_loans = Loan.objects.filter(
            member=self,
            date_return__isnull=True,
            date_loan__lt=timezone.now().date() - timedelta(days=7)
        )
        if overdue_loans.exists():
            self.blocked = True
            self.save()
            return False

        # Vérifier le nombre d'emprunts
        current_loans = Loan.objects.filter(member=self, date_return__isnull=True).count()
        return current_loans < 3

class Media(models.Model):
    name = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Book(Media):
    author = models.CharField(max_length=100)

class DVD(Media):
    producer = models.CharField(max_length=100)

class CD(Media):
    artist = models.CharField(max_length=100)

class BoardGame(models.Model):
    name = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Loan(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date_loan = models.DateField(auto_now_add=True)
    date_return = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.name} - {self.media.name}"

    def is_overdue(self):
        if self.date_return is None:
            return (timezone.now().date() - self.date_loan) > timedelta(days=7)
        return (self.date_return - self.date_loan) > timedelta(days=7)
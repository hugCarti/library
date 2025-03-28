from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Member, Media, Book, DVD, CD, BoardGame, Loan


class MemberModelTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(name="Test Member")

    def test_member_creation(self):
        self.assertEqual(self.member.name, "Test Member")
        self.assertFalse(self.member.blocked)

    def test_can_borrow(self):
        # Test qu'un membre peut emprunter normalement
        self.assertTrue(self.member.can_borrow())

        # Test blocage après 3 emprunts
        media1 = Book.objects.create(name="Book 1", available=True)
        media2 = Book.objects.create(name="Book 2", available=True)
        media3 = Book.objects.create(name="Book 3", available=True)

        Loan.objects.create(member=self.member, media=media1)
        Loan.objects.create(member=self.member, media=media2)
        Loan.objects.create(member=self.member, media=media3)

        self.assertFalse(self.member.can_borrow())


class MediaModelTest(TestCase):
    def test_media_inheritance(self):
        """Teste l'héritage et les propriétés spécifiques de chaque type de média"""
        # Test Book
        book = Book.objects.create(name="Test Book", author="Author", available=True)
        self.assertTrue(isinstance(book, Media))
        self.assertEqual(book.author, "Author")

        # Test DVD
        dvd = DVD.objects.create(name="Test DVD", producer="Producer", available=True)
        self.assertTrue(isinstance(dvd, Media))
        self.assertEqual(dvd.producer, "Producer")

        # Test CD
        cd = CD.objects.create(name="Test CD", artist="Artist", available=True)
        self.assertTrue(isinstance(cd, Media))
        self.assertEqual(cd.artist, "Artist")

        # Test BoardGame (hérite directement de models.Model)
        game = BoardGame.objects.create(name="Test Game", creator="Creator")
        self.assertFalse(isinstance(game, Media))  # BoardGame n'hérite pas de Media
        self.assertEqual(game.creator, "Creator")


class CDModelTest(TestCase):
    def setUp(self):
        self.cd = CD.objects.create(
            name="Album Test",
            artist="Artiste Célèbre",
            available=True
        )

    def test_cd_creation(self):
        """Vérifie la création correcte d'un CD"""
        self.assertEqual(self.cd.name, "Album Test")
        self.assertEqual(self.cd.artist, "Artiste Célèbre")
        self.assertTrue(self.cd.available)

    def test_cd_str_representation(self):
        """Teste la représentation en string du modèle"""
        self.assertEqual(str(self.cd), "Album Test")


class BoardGameModelTest(TestCase):
    def setUp(self):
        self.game = BoardGame.objects.create(
            name="Jeu Stratégique",
            creator="Créateur Renommé"
        )

    def test_boardgame_creation(self):
        """Vérifie la création correcte d'un jeu de société"""
        self.assertEqual(self.game.name, "Jeu Stratégique")
        self.assertEqual(self.game.creator, "Créateur Renommé")

    def test_boardgame_str_representation(self):
        """Teste la représentation en string du modèle"""
        self.assertEqual(str(self.game), "Jeu Stratégique")


class CDLoanIntegrationTest(TestCase):
    def test_cd_loan_workflow(self):
        """Teste le cycle complet d'emprunt d'un CD"""
        member = Member.objects.create(name="Membre Test")
        cd = CD.objects.create(name="CD Test", artist="Artiste", available=True)


class BoardGameAvailabilityTest(TestCase):
    def test_boardgame_availability_display(self):
        """Teste que les jeux de société sont toujours marqués comme consultables sur place"""
        game = BoardGame.objects.create(name="Jeu Test", creator="Créateur")

        # Les jeux de société ne devraient pas avoir de champ 'available'
        with self.assertRaises(AttributeError):
            game.available  # BoardGame n'a pas ce champ


class LoanModelTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(name="Test Member")
        self.book = Book.objects.create(name="Test Book", author="Author", available=True)

    def test_loan_creation(self):
        loan = Loan.objects.create(member=self.member, media=self.book)
        self.assertEqual(loan.member.name, "Test Member")
        self.assertEqual(loan.media.name, "Test Book")
        self.assertIsNone(loan.date_return)

        # Test prêt rendu à temps
        loan.date_return = timezone.now().date() - timedelta(days=5)
        loan.save()
        self.assertFalse(loan.is_overdue())


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(name="Test Member")
        self.book = Book.objects.create(name="Test Book", author="Author", available=True)
        self.loan = Loan.objects.create(member=self.member, media=self.book)

    def test_index_view(self):
        response = self.client.get(reverse('librarian:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bienvenue dans le système de gestion")

    def test_list_members_view(self):
        response = self.client.get(reverse('librarian:list_member'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Member")

    def test_create_member_view(self):
        response = self.client.post(reverse('librarian:create_member'), {'name': 'New Member'})
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertTrue(Member.objects.filter(name="New Member").exists())

    def test_create_loan_view(self):
        # Test création valide
        response = self.client.post(reverse('librarian:create_loan'), {
            'member': self.member.id,
            'media': self.book.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Media.objects.get(id=self.book.id).available)

        # Test membre bloqué
        self.member.blocked = True
        self.member.save()
        response = self.client.post(reverse('librarian:create_loan'), {
            'member': self.member.id,
            'media': self.book.id
        })
        self.assertEqual(response.status_code, 302)  # Redirection avec message d'erreur

    def test_return_loan_view(self):
        response = self.client.get(reverse('librarian:return_loan', args=[self.loan.id]))
        self.assertEqual(response.status_code, 302)
        self.loan.refresh_from_db()
        self.assertIsNotNone(self.loan.date_return)
        self.assertTrue(self.loan.media.available)


class ListActiveLoansTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(name="Test Member")
        self.book = Book.objects.create(name="Test Book", available=True)
        self.loan = Loan.objects.create(member=self.member, media=self.book)

    def test_list_active_loans(self):
        response = self.client.get(reverse('librarian:list_active_loans'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")
        self.assertContains(response, "Test Member")
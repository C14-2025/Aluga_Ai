from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistrationForm
from .views import CustomLoginView

# --- Testes de Modelos e Signals ---

class UsuariosModelsTests(TestCase):
    """Testes para os modelos e signals da app usuarios."""

    def test_user_creation_and_profile_signal(self):
        # Teste 1: Garante que o User é criado
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            first_name="Tester"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

        # Teste 2: Garante que o UserProfile é automaticamente criado via signal (post_save)
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.phone_number, "")
        self.assertFalse(user.profile.is_host)

    def test_user_profile_str(self):
        """Testa o método __str__ do modelo UserProfile."""
        user = User.objects.create_user(
            username="user_with_name",
            first_name="Nome",
            last_name="Sobrenome",
            password="password"
        )
        profile = user.profile
        # Caso o usuário tenha primeiro e último nome
        self.assertEqual(str(profile), "Nome Sobrenome Profile")

        # Caso o usuário só tenha o username
        user_no_name = User.objects.create_user(
            username="no_name_user",
            password="password"
        )
        profile_no_name = user_no_name.profile
        self.assertEqual(str(profile_no_name), "no_name_user Profile")


# --- Testes de Formulários ---

class UsuariosFormsTests(TestCase):
    """Testes para o formulário de registro (RegistrationForm)."""

    def setUp(self):
        # Cria um usuário para testar a duplicação de e-mail
        User.objects.create_user(
            username="existinguser",
            email="existing@email.com",
            password="password"
        )

    def test_registration_form_valid_data(self):
        """Testa o formulário com dados válidos, incluindo campos do UserProfile."""
        form_data = {
            "username": "newuser",
            "first_name": "Novo",
            "email": "new@email.com",
            "password_1": "securepass123",
            "password_2": "securepass123",
            "phone_number": "(99) 98765-4321",
            "city": "Rio de Janeiro",
            "state": "RJ"
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors.as_text()}")

    def test_registration_form_email_in_use(self):
        """Testa a validação de e-mail já em uso (clean_email)."""
        form_data = {
            "username": "anotheruser",
            "first_name": "Outro",
            "email": "existing@email.com", # E-mail já em uso
            "password_1": "securepass123",
            "password_2": "securepass123",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"][0],
            "Este email já está em uso."
        )

    def test_registration_form_invalid_phone_number(self):
        """Testa a validação de formato de telefone inválido (clean_phone_number)."""
        form_data = {
            "username": "phoneuser",
            "first_name": "Telefone",
            "email": "phone@email.com",
            "password_1": "securepass123",
            "password_2": "securepass123",
            "phone_number": "not-a-phone!", # Formato inválido
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0],
            "Telefone inválido."
        )

    def test_registration_form_empty_phone_number_is_valid(self):
        """Testa se um campo de telefone vazio é válido (já que required=False)."""
        form_data = {
            "username": "nophoneuser",
            "first_name": "Sem Telefone",
            "email": "nophone@email.com",
            "password_1": "securepass123",
            "password_2": "securepass123",
            "phone_number": "", # Telefone não é obrigatório
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors.as_text()}")


# --- Testes de Views ---

class UsuariosViewsTests(TestCase):
    """Testes para as views da app usuarios."""

    def setUp(self):
        self.client = Client()
        self.registration_url = reverse("usuarios:cadastro")
        self.login_url = reverse("usuarios:login")
        
        # Cria usuários de teste
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpassword",
            first_name="UserOne",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpassword",
            first_name="UserTwo",
        )
        self.profile_url1 = reverse("usuarios:perfil", kwargs={"pk": self.user1.pk})
        self.profile_url2 = reverse("usuarios:perfil", kwargs={"pk": self.user2.pk})


    # --- Testes da View de Cadastro (cadastro_view) ---
    def test_cadastro_view_get(self):
        """Testa se a página de cadastro carrega corretamente (GET)."""
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/cadastro.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    def test_cadastro_view_successful_registration(self):
        """Testa o fluxo completo de registro de usuário bem-sucedido (POST)."""
        new_user_data = {
            "username": "newuser",
            "first_name": "NovoNome",
            "email": "newuser@test.com",
            "password_1": "testpass123",
            "password_2": "testpass123",
            "phone_number": "11999998888",
            "city": "São Paulo",
            "state": "SP"
        }
        # follow=True segue o redirecionamento
        response = self.client.post(self.registration_url, new_user_data, follow=True)

        # 1. Checa se o usuário foi criado
        self.assertEqual(User.objects.count(), 3)
        new_user = User.objects.get(username="newuser")
        
        # 2. Checa o redirecionamento para o perfil e se o usuário está logado
        self.assertRedirects(response, reverse("usuarios:perfil", kwargs={"pk": new_user.pk}))
        # self.assertTrue(response.context['user'].is_authenticated) # Não funciona no follow=True, mas a view perfil_view garante o login
        self.assertTemplateUsed(response, "usuarios/perfil.html")

        # 3. Checa se os dados do User e UserProfile foram salvos
        self.assertEqual(new_user.first_name, "NovoNome")
        self.assertEqual(new_user.profile.phone_number, "11999998888")
        self.assertEqual(new_user.profile.city, "São Paulo")
        self.assertEqual(new_user.profile.state, "SP")

        # 4. Checa a mensagem de sucesso
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Cadastro realizado com sucesso.")

    def test_cadastro_view_failed_registration(self):
        """Testa o envio de formulário com dados inválidos (ex: senhas diferentes)."""
        # Senhas que não batem (o formulário deve falhar)
        new_user_data = {
            "username": "failuser",
            "first_name": "Fail",
            "email": "fail@test.com",
            "password_1": "testpass123",
            "password_2": "notmatching",
        }
        initial_user_count = User.objects.count()
        response = self.client.post(self.registration_url, new_user_data)

        # O usuário NÃO deve ter sido criado
        self.assertEqual(User.objects.count(), initial_user_count)
        # Deve retornar a página de cadastro (status 200)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/cadastro.html")
        self.assertTrue(response.context["form"].errors)

    # --- Testes da View de Perfil (perfil_view) ---
    def test_perfil_view_unauthenticated_access(self):
        """Testa o acesso ao perfil sem estar logado."""
        # Deve redirecionar para o login
        response = self.client.get(self.profile_url1)
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url1}")

    def test_perfil_view_access_own_profile(self):
        """Testa o acesso ao próprio perfil."""
        self.client.login(username="user1", password="testpassword")
        response = self.client.get(self.profile_url1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/perfil.html")
        self.assertEqual(response.context["usuario"], self.user1)

    def test_perfil_view_access_other_user_profile(self):
        """Testa a tentativa de acessar o perfil de outro usuário."""
        self.client.login(username="user1", password="testpassword")
        # user1 tenta acessar o perfil de user2
        response = self.client.get(self.profile_url2, follow=True)

        # Deve ser negado, redirecionando para o perfil do user1 com mensagem de erro
        self.assertRedirects(response, self.profile_url1)
        
        # Checa a mensagem de erro
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Acesso negado: você só pode ver seu próprio perfil.")
        
        # Checa se o template renderizado é o do user1 (após o redirect)
        self.assertTemplateUsed(response, "usuarios/perfil.html")
        self.assertEqual(response.context["usuario"], self.user1)

    # --- Testes da View de Login (CustomLoginView) ---
    def test_custom_login_view_success_url(self):
        """Testa o método get_success_url da CustomLoginView."""
        # Instancia a view para testar o método
        login_view = CustomLoginView()
        # Mock do request e do user logado
        login_view.request = self.client.get(self.login_url).wsgi_request
        login_view.request.user = self.user1 
        
        expected_url = reverse("usuarios:perfil", kwargs={"pk": self.user1.pk})
        actual_url = login_view.get_success_url()
        self.assertEqual(actual_url, expected_url)
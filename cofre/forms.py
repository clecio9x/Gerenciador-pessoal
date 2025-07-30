from django import forms
from django.contrib.auth.models import User
from .models import Note

# --- Formulários de Autenticação ---

class LoginForm(forms.Form):
    """
    Formulário para a tela de login com usuário e senha.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Usuário ou E-mail', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha', 'class': 'form-control'})
    )


class RegisterForm(forms.ModelForm):
    """
    Formulário para registrar novos usuários.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha', 'class': 'form-control'}),
        label="Senha"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirme a Senha', 'class': 'form-control'}),
        label="Confirme a Senha"
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nome de Usuário', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail', 'class': 'form-control'}),
        }

    def clean_username(self):
        """Verifica se o nome de usuário já existe."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso. Por favor, escolha outro.")
        return username

    def clean_email(self):
        """Verifica se o e-mail já existe."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado. Por favor, use outro.")
        return email

    def clean(self):
        """Verifica se as senhas são iguais."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        """Cria o usuário com a senha corretamente hasheada."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class OTPTokenForm(forms.Form):
    """
    Formulário para inserir o código OTP de 6 dígitos.
    """
    token = forms.CharField(
        label="",
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': '______', 'class': 'form-control', 'autocomplete': 'off'})
    )


# --- Formulário de Notas ---

class NoteForm(forms.ModelForm):
    """
    Formulário para criar e editar notas.
    """
    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título da Nota'}),
            'content': forms.Textarea(attrs={'placeholder': 'Escreva sua nota aqui...'}),
        }

# --- Formulários para Reset de Senha ---
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu email'
        })
    )

class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua nova senha'
        })
    )
    password2 = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua nova senha'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('As senhas não coincidem.')
            
            # Validação de força da senha
            if len(password1) < 8:
                raise forms.ValidationError('A senha deve ter pelo menos 8 caracteres.')
            
            if not any(c.isupper() for c in password1):
                raise forms.ValidationError('A senha deve conter pelo menos uma letra maiúscula.')
            
            if not any(c.islower() for c in password1):
                raise forms.ValidationError('A senha deve conter pelo menos uma letra minúscula.')
            
            if not any(c.isdigit() for c in password1):
                raise forms.ValidationError('A senha deve conter pelo menos um número.')
        
        return cleaned_data
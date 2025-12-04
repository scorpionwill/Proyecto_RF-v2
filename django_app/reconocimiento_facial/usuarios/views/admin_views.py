"""Vistas para administración del sistema (gestión de usuarios Encargados)."""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
import re
from ..decorators import admin_required


def validate_password_strength(password):
    """Valida que la contraseña tenga mínimo 12 caracteres, 1 número y 1 caracter especial."""
    if len(password) < 12:
        raise ValidationError('La contraseña debe tener al menos 12 caracteres.')
    if not re.search(r'\d', password):
        raise ValidationError('La contraseña debe contener al menos 1 número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        raise ValidationError('La contraseña debe contener al menos 1 caracter especial (!@#$%^&*...).')


class EncargadoCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios Encargado."""
    first_name = forms.CharField(max_length=150, required=True, label='Nombre')
    last_name = forms.CharField(max_length=150, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar help_text para contraseña
        self.fields['password1'].help_text = (
            '<ul>'
            '<li>La contraseña debe tener al menos 12 caracteres.</li>'
            '<li>Debe contener al menos 1 número.</li>'
            '<li>Debe contener al menos 1 carácter especial (!@#$%^&*...).</li>'
            '<li>No puede ser similar a tu información personal.</li>'
            '</ul>'
        )
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1


@admin_required
def listar_encargados(request):
    """Lista todos los usuarios Encargado del sistema."""
    # Obtener solo usuarios que son Encargado (no staff) y Admins (staff)
    usuarios_sistema = User.objects.all().order_by('-is_staff', 'username')
    
    return render(request, 'admin/listar_encargados.html', {
        'usuarios_sistema': usuarios_sistema
    })


@admin_required
def crear_encargado(request):
    """Crear nuevo usuario Encargado."""
    if request.method == 'POST':
        form = EncargadoCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False  # Encargado, no Admin
            user.is_superuser = False
            user.save()
            
            messages.success(request, f'Usuario Encargado "{user.username}" creado exitosamente.')
            return redirect('listar_encargados')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EncargadoCreationForm()
    
    return render(request, 'admin/crear_encargado.html', {
        'form': form
    })


@admin_required
def eliminar_encargado(request, user_id):
    """Eliminar usuario Encargado (solo si no es Admin)."""
    try:
        user = User.objects.get(id=user_id)
        
        # No permitir eliminar a Admins
        if user.is_staff:
            messages.error(request, 'No se puede eliminar a un Administrador.')
            return redirect('listar_encargados')
        
        # No permitir que el admin se elimine a sí mismo
        if user.id == request.user.id:
            messages.error(request, 'No puedes eliminarte a ti mismo.')
            return redirect('listar_encargados')
        
        username = user.username
        user.delete()
        messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
    
    return redirect('listar_encargados')

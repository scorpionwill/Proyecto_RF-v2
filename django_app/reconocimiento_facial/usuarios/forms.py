from django import forms
from .models import Usuario, Evento


class UsuarioForm(forms.ModelForm):
    """Formulario para crear y editar usuarios."""
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'rut', 'carrera']


class EventoForm(forms.ModelForm):
    """Formulario para crear y editar eventos."""
    
    class Meta:
        model = Evento
        fields = ['nom_evento', 'fecha', 'relator', 'descripcion', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.Select(choices=[(True, 'Activo'), (False, 'Inactivo')])
        }
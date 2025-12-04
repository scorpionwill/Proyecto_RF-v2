"""Servicio de lógica de negocio para eventos."""

from datetime import date
from django.shortcuts import get_object_or_404
from ..models import Evento


class EventoService:
    """Servicio para operaciones de eventos."""
    
    @staticmethod
    def obtener_evento_activo_hoy():
        """
        Obtiene el evento activo de hoy si existe.
        
        Returns:
            Tupla (evento, mensaje) donde evento puede ser None
        """
        hoy = date.today()
        evento = Evento.objects.filter(fecha=hoy).order_by('-id').first()
        
        if evento:
            mensaje = f"El evento '{evento.nom_evento}' está en curso."
        else:
            mensaje = "No hay ningún evento activo en este momento."
            
        return evento, mensaje
    
    @staticmethod
    def validar_evento_para_reconocimiento(evento_id=None):
        """
        Valida que un evento esté disponible y activo (hoy) para reconocimiento.
        
        Args:
            evento_id: ID del evento (opcional)
            
        Returns:
            Evento si es válido, None si no
            
        Raises:
            ValueError: Si el evento no existe o no está activo
        """
        if evento_id:
            try:
                evento = Evento.objects.get(id=evento_id)
            except Evento.DoesNotExist:
                raise ValueError("Evento no encontrado")
            
            if not evento.esta_activo():
                raise ValueError(f"El evento '{evento.nom_evento}' no está activo (debe ser hoy)")
        else:
            hoy = date.today()
            evento = Evento.objects.filter(fecha=hoy).order_by('-id').first()
            if not evento:
                raise ValueError("No hay eventos activos disponibles")
        
        return evento

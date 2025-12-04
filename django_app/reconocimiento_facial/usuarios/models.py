from django.db import models


class Usuario(models.Model):
    """Modelo para usuarios del sistema de reconocimiento facial."""
    
    JORNADA_CHOICES = [
        ('D', 'Diurna'),
        ('N', 'Nocturna'),
    ]
    
    nombre = models.CharField(max_length=255, verbose_name="Nombre completo")
    rut = models.CharField(max_length=20, unique=True, verbose_name="RUT")
    carrera = models.CharField(max_length=100, verbose_name="Carrera")
    jornada = models.CharField(max_length=1, choices=JORNADA_CHOICES, default='D', verbose_name="Jornada")
    imagen = models.BinaryField(blank=True, null=True, verbose_name="Foto del alumno")
    
    # Campos biométricos (LuckFox)
    vector_facial = models.JSONField(null=True, blank=True, help_text="Vector de características faciales (512 floats)")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.rut})"
    
    def get_jornada_display_text(self):
        """Retorna el texto completo de la jornada"""
        return dict(self.JORNADA_CHOICES).get(self.jornada, 'Desconocida')


class Evento(models.Model):
    """Modelo para eventos donde se registra asistencia."""
    
    nom_evento = models.CharField(max_length=100)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    relator = models.CharField(max_length=60, blank=True, null=True)
    estado = models.BooleanField()

    def __str__(self):
        return self.nom_evento
    
    def get_estado(self):
        """
        Retorna el estado del evento basado en su fecha.
        
        Returns:
            str: 'proximo', 'activo', o 'finalizado'
        """
        from datetime import date
        hoy = date.today()
        
        if self.fecha > hoy:
            return 'proximo'
        elif self.fecha == hoy:
            return 'activo'
        else:
            return 'finalizado'
    
    def esta_activo(self):
        """Retorna True si el evento es hoy."""
        return self.get_estado() == 'activo'


class Asistencia(models.Model):
    """Modelo para registrar asistencia de usuarios a eventos."""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    evento_asist = models.ForeignKey(Evento, on_delete=models.CASCADE)
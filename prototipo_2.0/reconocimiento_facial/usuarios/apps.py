from django.apps import AppConfig

# Este archivo contiene la configuración de la aplicación 'usuarios'.
# Django utiliza esta clase para conocer información sobre la aplicación, como su nombre.
class UsuariosConfig(AppConfig):
    # Define el tipo de campo de clave primaria que se creará automáticamente
    # en los modelos de esta aplicación si no se especifica uno.
    # 'BigAutoField' es un entero de 64 bits.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # El nombre de la aplicación. Django usa esto para identificar la aplicación.
    name = 'usuarios'
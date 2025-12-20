"""
-----------------------------------------------------------------------------
Archivo: zoneinfo.py
Descripcion: Modulo de compatibilidad para zonas horarias. Proporciona
             backport de zoneinfo para versiones de Python anteriores
             a 3.9 que no incluyen el modulo nativo.
Fecha de creacion: 10 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""

import sys
import backports.zoneinfo

sys.modules['zoneinfo'] = backports.zoneinfo

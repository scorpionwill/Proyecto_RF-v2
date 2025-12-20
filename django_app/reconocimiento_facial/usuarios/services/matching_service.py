"""
-----------------------------------------------------------------------------
Archivo: matching_service.py
Descripcion: Servicio de matching biometrico para comparacion de vectores
             faciales. Implementa calculo de similitud coseno, distancia
             euclidiana, busqueda de coincidencias en la base de datos,
             y verificacion 1:1 de usuarios registrados.
Fecha de creacion: 10 de Octubre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import numpy as np

from ..config import (
    SIMILARITY_THRESHOLD_DEFAULT,
    SIMILARITY_THRESHOLD_VERIFICATION
)
from ..utils.logger import logger
from .firebase_service import firebase_service


@dataclass
class MatchResult:
    """Resultado de una operación de matching facial."""
    match: bool
    usuario: Optional[Dict[str, Any]]
    similitud: float
    distancia: float
    candidatos: List[Dict[str, Any]]
    total_comparaciones: int


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calcula la similitud coseno entre dos vectores.
    
    Args:
        vector_a: Primer vector
        vector_b: Segundo vector
    
    Returns:
        Similitud entre 0 y 1 (1 = idénticos, 0 = completamente diferentes)
    """
    try:
        vec_a = np.array(vector_a, dtype=np.float32)
        vec_b = np.array(vector_b, dtype=np.float32)
        
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot_product / (norm_a * norm_b)
        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        logger.error(f"Error calculando similitud coseno: {e}")
        return 0.0


def euclidean_distance(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calcula la distancia euclidiana entre dos vectores.
    Menor distancia = más similares.
    
    Args:
        vector_a: Primer vector
        vector_b: Segundo vector
    
    Returns:
        Distancia euclidiana
    """
    try:
        vec_a = np.array(vector_a, dtype=np.float32)
        vec_b = np.array(vector_b, dtype=np.float32)
        return float(np.linalg.norm(vec_a - vec_b))
        
    except Exception as e:
        logger.error(f"Error calculando distancia euclidiana: {e}")
        return float('inf')


def encontrar_match(
    vector_consulta: List[float],
    umbral_similitud: float = SIMILARITY_THRESHOLD_DEFAULT,
    jornada_filtro: Optional[str] = None,
    usuarios_cache: Optional[List[Dict]] = None
) -> MatchResult:
    """
    Encuentra el mejor match para un vector de consulta entre todos los usuarios registrados.
    
    Args:
        vector_consulta: Vector facial de 512 floats (InspireFace)
        umbral_similitud: Umbral mínimo de similitud (por defecto desde config)
        jornada_filtro: Opcional - Filtrar por jornada 'D' o 'V'
        usuarios_cache: Opcional - Lista de usuarios precargada para evitar consultas a Firebase
    
    Returns:
        MatchResult con estado del match, datos del usuario y métricas de similitud
    """
    logger.matching(f"Iniciando búsqueda de match (umbral: {umbral_similitud * 100}%)")
    
    # Obtener usuarios activos desde Firebase
    if usuarios_cache is not None:
        usuarios = usuarios_cache
    else:
        usuarios = firebase_service.listar_usuarios()
    
    usuarios_activos = [u for u in usuarios if u.get('activo', True)]
    
    # Filtrar por jornada si se especificó
    if jornada_filtro:
        usuarios_activos = [u for u in usuarios_activos if u.get('jornada') == jornada_filtro]
    
    logger.matching(f"Comparando con {len(usuarios_activos)} usuarios activos")
    
    if not usuarios_activos:
        return MatchResult(
            match=False,
            usuario=None,
            similitud=0.0,
            distancia=float('inf'),
            candidatos=[],
            total_comparaciones=0
        )
    
    resultados = []
    
    for usuario in usuarios_activos:
        # Usar vector_promedio si existe, sino vector_facial (compatibilidad)
        vector_usuario = usuario.get('vector_promedio') or usuario.get('vector_facial')
        
        if not vector_usuario:
            logger.warning(f"Usuario {usuario.get('nombre')} no tiene vector facial")
            continue
        
        # Calcular similitud coseno y distancia euclidiana
        similitud = cosine_similarity(vector_consulta, vector_usuario)
        distancia = euclidean_distance(vector_consulta, vector_usuario)
        
        resultados.append({
            'usuario': usuario,
            'similitud': similitud,
            'distancia': distancia
        })
        
        logger.matching(
            f"  - {usuario.get('nombre'):30s} | Similitud: {similitud:.3f} | Distancia: {distancia:.2f}"
        )
    
    # Ordenar por similitud descendente (mayor similitud primero)
    resultados.sort(key=lambda x: x['similitud'], reverse=True)
    
    mejor_match = resultados[0] if resultados else None
    
    if mejor_match:
        logger.matching(
            f"Mejor match: {mejor_match['usuario']['nombre']} "
            f"con {mejor_match['similitud'] * 100:.1f}% similitud"
        )
    
    # Verificar si se supera el umbral
    if mejor_match and mejor_match['similitud'] >= umbral_similitud:
        logger.success(f"MATCH EXITOSO (>{umbral_similitud * 100}%)")
        return MatchResult(
            match=True,
            usuario=mejor_match['usuario'],
            similitud=mejor_match['similitud'],
            distancia=mejor_match['distancia'],
            candidatos=resultados[:5],
            total_comparaciones=len(resultados)
        )
    else:
        max_similitud = mejor_match['similitud'] if mejor_match else 0.0
        logger.warning(
            f"NO MATCH (mejor similitud: {max_similitud * 100:.1f}%, "
            f"umbral: {umbral_similitud * 100}%)"
        )
        return MatchResult(
            match=False,
            usuario=None,
            similitud=max_similitud,
            distancia=mejor_match['distancia'] if mejor_match else float('inf'),
            candidatos=resultados[:5],
            total_comparaciones=len(resultados)
        )


def verificar_usuario(
    vector_consulta: List[float],
    rut_esperado: str,
    umbral: float = SIMILARITY_THRESHOLD_VERIFICATION
) -> Dict[str, Any]:
    """
    Verifica si un vector corresponde a un usuario específico (por RUT).
    Útil para modo de verificación 1:1.
    
    Args:
        vector_consulta: Vector facial capturado
        rut_esperado: RUT del usuario a verificar
        umbral: Umbral mínimo de similitud
    
    Returns:
        Dict con estado de verificación y similitud
    """
    usuario = firebase_service.obtener_usuario_por_rut(rut_esperado)
    
    if not usuario:
        return {
            'verificado': False,
            'similitud': 0.0,
            'error': 'Usuario no encontrado'
        }
    
    vector_usuario = usuario.get('vector_promedio') or usuario.get('vector_facial')
    
    if not vector_usuario:
        return {
            'verificado': False,
            'similitud': 0.0,
            'error': 'Usuario sin vector facial'
        }
    
    similitud = cosine_similarity(vector_consulta, vector_usuario)
    
    return {
        'verificado': similitud >= umbral,
        'similitud': similitud,
        'nombre': usuario.get('nombre')
    }

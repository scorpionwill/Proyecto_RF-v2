"""
Service for biometric matching of facial vectors.
Handles face comparison, similarity calculation, and user matching.
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
    """Result of a face matching operation."""
    match: bool
    usuario: Optional[Dict[str, Any]]
    similitud: float
    distancia: float
    candidatos: List[Dict[str, Any]]
    total_comparaciones: int


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        Similarity between 0 and 1 (1 = identical, 0 = completely different)
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
    Calculate Euclidean distance between two vectors.
    Lower distance = more similar.
    
    Args:
        vector_a: First vector
        vector_b: Second vector
    
    Returns:
        Euclidean distance
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
    Find the best match for a query vector among all registered users.
    
    Args:
        vector_consulta: Facial vector of 512 floats (InspireFace)
        umbral_similitud: Minimum similarity threshold (default from config)
        jornada_filtro: Optional - Filter by shift 'D' or 'V'
        usuarios_cache: Optional - Pre-loaded user list to avoid Firebase queries
    
    Returns:
        MatchResult with match status, user data, and similarity metrics
    """
    logger.matching(f"Iniciando búsqueda de match (umbral: {umbral_similitud * 100}%)")
    
    # Get active users from Firebase
    if usuarios_cache is not None:
        usuarios = usuarios_cache
    else:
        usuarios = firebase_service.listar_usuarios()
    
    usuarios_activos = [u for u in usuarios if u.get('activo', True)]
    
    # Filter by shift if specified
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
        # Use vector_promedio if exists, else vector_facial (compatibility)
        vector_usuario = usuario.get('vector_promedio') or usuario.get('vector_facial')
        
        if not vector_usuario:
            logger.warning(f"Usuario {usuario.get('nombre')} no tiene vector facial")
            continue
        
        # Calculate cosine similarity and Euclidean distance
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
    
    # Sort by similarity descending (highest similarity first)
    resultados.sort(key=lambda x: x['similitud'], reverse=True)
    
    mejor_match = resultados[0] if resultados else None
    
    if mejor_match:
        logger.matching(
            f"Mejor match: {mejor_match['usuario']['nombre']} "
            f"con {mejor_match['similitud'] * 100:.1f}% similitud"
        )
    
    # Check if threshold is exceeded
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
    Verify if a vector corresponds to a specific user (by RUT).
    Useful for 1:1 verification mode.
    
    Args:
        vector_consulta: Captured facial vector
        rut_esperado: RUT of user to verify
        umbral: Minimum similarity threshold
    
    Returns:
        Dict with verification status and similarity
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

import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class ScoringSystem:
    def __init__(self):
        self.disc_profiles = {
            'Dominante': {
                'description': 'Orientado a resultados, directo y decidido. Excelente para roles de liderazgo.',
                'characteristics': ['Liderazgo', 'Toma de decisiones', 'Orientación a resultados', 'Competitivo'],
                'strengths': ['Liderazgo natural', 'Toma decisiones rápidas', 'Orientado a objetivos'],
                'areas_to_improve': ['Paciencia', 'Escucha activa', 'Trabajo en equipo']
            },
            'Influyente': {
                'description': 'Sociable, comunicativo y persuasivo. Ideal para roles de ventas y relaciones.',
                'characteristics': ['Comunicación', 'Persuasión', 'Sociabilidad', 'Optimismo'],
                'strengths': ['Excelente comunicador', 'Carismático', 'Motivador'],
                'areas_to_improve': ['Atención al detalle', 'Seguimiento de tareas', 'Organización']
            },
            'Estable': {
                'description': 'Confiable, paciente y colaborativo. Perfecto para roles de apoyo y equipo.',
                'characteristics': ['Confiabilidad', 'Paciencia', 'Colaboración', 'Lealtad'],
                'strengths': ['Muy confiable', 'Trabajo en equipo', 'Estabilidad emocional'],
                'areas_to_improve': ['Iniciativa', 'Adaptabilidad', 'Toma de riesgos']
            },
            'Analítico': {
                'description': 'Detallista, preciso y sistemático. Excelente para roles técnicos y de análisis.',
                'characteristics': ['Precisión', 'Análisis', 'Calidad', 'Sistematización'],
                'strengths': ['Atención al detalle', 'Análisis profundo', 'Alta calidad'],
                'areas_to_improve': ['Velocidad de decisión', 'Flexibilidad', 'Comunicación interpersonal']
            }
        }
        
        self.hogan_profiles = {
            'Líder': {
                'description': 'Natural tendencia al liderazgo y toma de control en situaciones grupales.',
                'characteristics': ['Liderazgo', 'Control', 'Ambición', 'Iniciativa'],
                'strengths': ['Liderazgo natural', 'Toma de iniciativa', 'Motivación alta'],
                'areas_to_improve': ['Delegación', 'Paciencia', 'Escucha de feedback']
            },
            'Resiliente': {
                'description': 'Capacidad de mantener estabilidad emocional bajo presión y críticas.',
                'characteristics': ['Estabilidad', 'Resistencia', 'Calma', 'Autocontrol'],
                'strengths': ['Manejo del estrés', 'Estabilidad emocional', 'Perseverancia'],
                'areas_to_improve': ['Expresión emocional', 'Búsqueda de feedback', 'Flexibilidad']
            },
            'Estructurado': {
                'description': 'Prefiere orden, planificación y métodos sistemáticos de trabajo.',
                'characteristics': ['Organización', 'Planificación', 'Método', 'Disciplina'],
                'strengths': ['Muy organizado', 'Planificación efectiva', 'Disciplina'],
                'areas_to_improve': ['Adaptabilidad', 'Creatividad', 'Improvisación']
            },
            'Equilibrado': {
                'description': 'Balance entre trabajo y vida personal, con límites claros.',
                'characteristics': ['Balance', 'Límites', 'Bienestar', 'Sostenibilidad'],
                'strengths': ['Balance vida-trabajo', 'Límites saludables', 'Sostenibilidad'],
                'areas_to_improve': ['Dedicación extra', 'Disponibilidad', 'Flexibilidad horaria']
            }
        }

    def calculate_disc_profile(self, answers: List[Dict]) -> Dict:
        """Calcula el perfil DISC basado en las respuestas"""
        try:
            # Inicializar puntuaciones
            scores = {
                'D': 0,  # Dominante
                'I': 0,  # Influyente
                'S': 0,  # Estable
                'C': 0   # Analítico
            }
            
            # Calcular puntuaciones basadas en las respuestas
            for answer in answers:
                question_num = answer['question']
                selected_value = answer['value']
                
                # Mapear respuestas a tipos DISC
                if question_num == 0:  # ¿Prefieres trabajar en grupo o solo?
                    if selected_value == 'grupo':
                        scores['I'] += 2
                        scores['S'] += 1
                    elif selected_value == 'solo':
                        scores['D'] += 1
                        scores['C'] += 2
                    elif selected_value == 'ambos':
                        scores['S'] += 2
                        scores['I'] += 1
                
                elif question_num == 1:  # ¿Tomas decisiones rápidamente o prefieres analizar?
                    if selected_value == 'rapido':
                        scores['D'] += 2
                        scores['I'] += 1
                    elif selected_value == 'analizar':
                        scores['C'] += 2
                        scores['S'] += 1
                    elif selected_value == 'depende':
                        scores['S'] += 2
                        scores['C'] += 1
                
                elif question_num == 2:  # ¿Qué te motiva más: logros personales o ayudar al equipo?
                    if selected_value == 'logros':
                        scores['D'] += 2
                        scores['C'] += 1
                    elif selected_value == 'equipo':
                        scores['I'] += 2
                        scores['S'] += 2
                    elif selected_value == 'ambos':
                        scores['I'] += 1
                        scores['S'] += 1
                
                elif question_num == 3:  # ¿Te incomodan los conflictos?
                    if selected_value == 'si':
                        scores['S'] += 2
                        scores['C'] += 1
                    elif selected_value == 'no':
                        scores['D'] += 2
                        scores['I'] += 1
                    elif selected_value == 'depende':
                        scores['C'] += 2
                        scores['S'] += 1
            
            # Determinar perfil dominante
            max_score = max(scores.values())
            profile_type = None
            
            for key, value in scores.items():
                if value == max_score:
                    if key == 'D':
                        profile_type = 'Dominante'
                    elif key == 'I':
                        profile_type = 'Influyente'
                    elif key == 'S':
                        profile_type = 'Estable'
                    elif key == 'C':
                        profile_type = 'Analítico'
                    break
            
            # Si no se puede determinar, usar Analítico por defecto
            if profile_type is None:
                profile_type = 'Analítico'
            
            profile_data = self.disc_profiles[profile_type]
            
            return {
                'type': profile_type,
                'description': profile_data['description'],
                'characteristics': profile_data['characteristics'],
                'strengths': profile_data['strengths'],
                'areas_to_improve': profile_data['areas_to_improve'],
                'scores': scores,
                'confidence': max_score / sum(scores.values()) if sum(scores.values()) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculando perfil DISC: {e}")
            return self._get_default_disc_profile()

    def calculate_hogan_profile(self, answers: List[Dict]) -> Dict:
        """Calcula el perfil HOGAN basado en las respuestas"""
        try:
            # Inicializar puntuaciones
            scores = {
                'leadership': 0,
                'resilience': 0,
                'structure': 0,
                'balance': 0
            }
            
            # Calcular puntuaciones basadas en las respuestas
            for answer in answers:
                question_num = answer['question']
                selected_value = answer['value']
                
                # Mapear respuestas a tipos HOGAN
                if question_num == 0:  # ¿Tiendes a asumir liderazgo en grupos?
                    if selected_value == 'si':
                        scores['leadership'] += 2
                    elif selected_value == 'no':
                        scores['balance'] += 1
                        scores['structure'] += 1
                    elif selected_value == 'aveces':
                        scores['leadership'] += 1
                        scores['resilience'] += 1
                
                elif question_num == 1:  # ¿Eres emocionalmente reactivo ante críticas?
                    if selected_value == 'si':
                        scores['leadership'] += 1
                    elif selected_value == 'no':
                        scores['resilience'] += 2
                    elif selected_value == 'depende':
                        scores['resilience'] += 1
                        scores['structure'] += 1
                
                elif question_num == 2:  # ¿Prefieres estructura o improvisación en el trabajo?
                    if selected_value == 'estructura':
                        scores['structure'] += 2
                        scores['resilience'] += 1
                    elif selected_value == 'improvisacion':
                        scores['leadership'] += 1
                        scores['balance'] += 1
                    elif selected_value == 'ambos':
                        scores['balance'] += 2
                
                elif question_num == 3:  # ¿Te cuesta desconectarte del trabajo?
                    if selected_value == 'si':
                        scores['leadership'] += 1
                        scores['structure'] += 1
                    elif selected_value == 'no':
                        scores['balance'] += 2
                    elif selected_value == 'aveces':
                        scores['balance'] += 1
                        scores['resilience'] += 1
            
            # Determinar perfil dominante
            max_score = max(scores.values())
            profile_type = None
            
            for key, value in scores.items():
                if value == max_score:
                    if key == 'leadership':
                        profile_type = 'Líder'
                    elif key == 'resilience':
                        profile_type = 'Resiliente'
                    elif key == 'structure':
                        profile_type = 'Estructurado'
                    elif key == 'balance':
                        profile_type = 'Equilibrado'
                    break
            
            # Si no se puede determinar, usar Equilibrado por defecto
            if profile_type is None:
                profile_type = 'Equilibrado'
            
            profile_data = self.hogan_profiles[profile_type]
            
            return {
                'type': profile_type,
                'description': profile_data['description'],
                'characteristics': profile_data['characteristics'],
                'strengths': profile_data['strengths'],
                'areas_to_improve': profile_data['areas_to_improve'],
                'scores': scores,
                'confidence': max_score / sum(scores.values()) if sum(scores.values()) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculando perfil HOGAN: {e}")
            return self._get_default_hogan_profile()

    def _get_default_disc_profile(self) -> Dict:
        """Perfil DISC por defecto en caso de error"""
        return {
            'type': 'Analítico',
            'description': self.disc_profiles['Analítico']['description'],
            'characteristics': self.disc_profiles['Analítico']['characteristics'],
            'strengths': self.disc_profiles['Analítico']['strengths'],
            'areas_to_improve': self.disc_profiles['Analítico']['areas_to_improve'],
            'scores': {'D': 1, 'I': 1, 'S': 1, 'C': 2},
            'confidence': 0.4
        }

    def _get_default_hogan_profile(self) -> Dict:
        """Perfil HOGAN por defecto en caso de error"""
        return {
            'type': 'Equilibrado',
            'description': self.hogan_profiles['Equilibrado']['description'],
            'characteristics': self.hogan_profiles['Equilibrado']['characteristics'],
            'strengths': self.hogan_profiles['Equilibrado']['strengths'],
            'areas_to_improve': self.hogan_profiles['Equilibrado']['areas_to_improve'],
            'scores': {'leadership': 1, 'resilience': 1, 'structure': 1, 'balance': 2},
            'confidence': 0.4
        }

    def get_profile_recommendations(self, profile_type: str, test_type: str = 'disc') -> Dict:
        """Obtiene recomendaciones específicas para un perfil"""
        try:
            if test_type == 'disc':
                profiles = self.disc_profiles
            else:
                profiles = self.hogan_profiles
            
            if profile_type not in profiles:
                profile_type = 'Analítico' if test_type == 'disc' else 'Equilibrado'
            
            profile_data = profiles[profile_type]
            
            return {
                'interview_tips': self._get_interview_tips(profile_type, test_type),
                'career_suggestions': self._get_career_suggestions(profile_type, test_type),
                'development_areas': profile_data['areas_to_improve'],
                'strengths': profile_data['strengths']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}")
            return {}

    def _get_interview_tips(self, profile_type: str, test_type: str) -> List[str]:
        """Obtiene consejos específicos de entrevista por perfil"""
        tips = {
            'disc': {
                'Dominante': [
                    "Muestra ejemplos concretos de liderazgo y toma de decisiones",
                    "Enfatiza tus logros y resultados cuantificables",
                    "Demuestra cómo tu estilo directo beneficia a los equipos"
                ],
                'Influyente': [
                    "Cuenta historias que demuestren tu capacidad de persuasión",
                    "Muestra cómo motivas y energizas a los equipos",
                    "Destaca tu habilidad para construir relaciones"
                ],
                'Estable': [
                    "Enfatiza tu confiabilidad y consistencia",
                    "Muestra ejemplos de trabajo en equipo exitoso",
                    "Destaca tu capacidad de mantener calma bajo presión"
                ],
                'Analítico': [
                    "Presenta datos y análisis que respalden tus decisiones",
                    "Muestra tu atención al detalle con ejemplos específicos",
                    "Enfatiza tu capacidad de resolver problemas complejos"
                ]
            },
            'hogan': {
                'Líder': [
                    "Presenta ejemplos de cuando tomaste la iniciativa",
                    "Muestra cómo tu liderazgo impactó positivamente en los resultados",
                    "Demuestra tu capacidad para inspirar y dirigir equipos"
                ],
                'Resiliente': [
                    "Cuenta sobre situaciones difíciles que manejaste exitosamente",
                    "Muestra tu capacidad de mantener rendimiento bajo presión",
                    "Demuestra cómo tu estabilidad beneficia al equipo"
                ],
                'Estructurado': [
                    "Presenta ejemplos de proyectos bien organizados que lideraste",
                    "Muestra cómo tu planificación previno problemas",
                    "Enfatiza tu capacidad de crear procesos eficientes"
                ],
                'Equilibrado': [
                    "Muestra cómo balanceas múltiples responsabilidades",
                    "Demuestra tu sostenibilidad y prevención del burnout",
                    "Enfatiza tu capacidad de mantener límites saludables"
                ]
            }
        }
        
        return tips.get(test_type, {}).get(profile_type, [])

    def _get_career_suggestions(self, profile_type: str, test_type: str) -> List[str]:
        """Obtiene sugerencias de carrera por perfil"""
        suggestions = {
            'disc': {
                'Dominante': [
                    "Roles de liderazgo y gerencia",
                    "Consultoría estratégica",
                    "Emprendimiento y startups",
                    "Ventas de alto nivel"
                ],
                'Influyente': [
                    "Ventas y desarrollo de negocios",
                    "Marketing y comunicaciones",
                    "Relaciones públicas",
                    "Capacitación y desarrollo"
                ],
                'Estable': [
                    "Recursos humanos",
                    "Servicio al cliente",
                    "Administración y operaciones",
                    "Trabajo social y salud"
                ],
                'Analítico': [
                    "Análisis de datos y investigación",
                    "Ingeniería y tecnología",
                    "Finanzas y contabilidad",
                    "Control de calidad"
                ]
            },
            'hogan': {
                'Líder': [
                    "Roles ejecutivos y de alta gerencia",
                    "Gestión de proyectos complejos",
                    "Consultoría de liderazgo",
                    "Desarrollo organizacional"
                ],
                'Resiliente': [
                    "Gestión de crisis",
                    "Roles de alta presión",
                    "Negociación y mediación",
                    "Operaciones críticas"
                ],
                'Estructurado': [
                    "Gestión de procesos",
                    "Planificación estratégica",
                    "Auditoría y cumplimiento",
                    "Gestión de calidad"
                ],
                'Equilibrado': [
                    "Roles de coordinación",
                    "Gestión de equipos diversos",
                    "Desarrollo sostenible",
                    "Bienestar organizacional"
                ]
            }
        }
        
        return suggestions.get(test_type, {}).get(profile_type, [])

    def validate_answers(self, answers: List[Dict], test_type: str) -> bool:
        """Valida que las respuestas sean completas y válidas"""
        try:
            if not answers or len(answers) != 4:
                return False
            
            for answer in answers:
                if 'question' not in answer or 'value' not in answer:
                    return False
                
                if not isinstance(answer['question'], int) or answer['question'] < 0 or answer['question'] > 3:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando respuestas: {e}")
            return False

    def get_profile_comparison(self, profile1: Dict, profile2: Dict) -> Dict:
        """Compara dos perfiles y encuentra similitudes/diferencias"""
        try:
            similarities = []
            differences = []
            
            # Comparar características
            chars1 = set(profile1.get('characteristics', []))
            chars2 = set(profile2.get('characteristics', []))
            
            similarities.extend(list(chars1.intersection(chars2)))
            differences.extend(list(chars1.symmetric_difference(chars2)))
            
            return {
                'similarities': similarities,
                'differences': differences,
                'compatibility_score': len(similarities) / (len(similarities) + len(differences)) if (len(similarities) + len(differences)) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error comparando perfiles: {e}")
            return {'similarities': [], 'differences': [], 'compatibility_score': 0}
import google.generativeai as genai
import logging
import json
import asyncio
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class GeminiIntegration:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.setup_gemini()
        
    def setup_gemini(self):
        """Configura la API de Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Integración con Gemini configurada correctamente")
        except Exception as e:
            logger.error(f"Error configurando Gemini: {e}")
            raise

    async def generate_feedback(self, profile: Dict, interview_answers: List[Dict]) -> str:
        """Genera retroalimentación personalizada usando IA"""
        try:
            # Construir prompt para IA
            prompt = self._build_feedback_prompt(profile, interview_answers)
            
            # Generar respuesta
            response = await self._generate_response(prompt)
            
            # Procesar y limpiar respuesta
            feedback = self._process_feedback(response)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generando feedback: {e}")
            return self._generate_fallback_feedback(profile)

    def _build_feedback_prompt(self, profile: Dict, interview_answers: List[Dict]) -> str:
        """Construye el prompt para generar retroalimentación"""
        
        # Información del perfil
        profile_info = f"""
        PERFIL DEL CANDIDATO:
        - Tipo: {profile.get('type', 'No definido')}
        - Descripción: {profile.get('description', 'No disponible')}
        - Puntuaciones: {json.dumps(profile.get('scores', {}), indent=2)}
        """
        
        # Respuestas de la entrevista
        answers_info = "RESPUESTAS DE LA ENTREVISTA:\n"
        for i, qa in enumerate(interview_answers, 1):
            answers_info += f"""
            Pregunta {i}: {qa['question']}
            Respuesta: {qa['answer']}
            ---
            """
        
        # Prompt completo
        prompt = f"""
        Actúa como un experto en recursos humanos y coach de entrevistas laborales.
        
        {profile_info}
        
        {answers_info}
        
        INSTRUCCIONES:
        1. Analiza las respuestas del candidato considerando su perfil psicológico
        2. Identifica fortalezas específicas demostradas en las respuestas
        3. Señala áreas de mejora concretas y accionables
        4. Proporciona consejos prácticos para futuras entrevistas
        5. Mantén un tono motivacional y constructivo
        6. Limita tu respuesta a 300 palabras máximo
        
        FORMATO DE RESPUESTA:
        **🎯 FORTALEZAS IDENTIFICADAS:**
        - [Lista de fortalezas específicas]
        
        **📈 ÁREAS DE MEJORA:**
        - [Lista de mejoras concretas]
        
        **💡 CONSEJOS PRÁCTICOS:**
        - [Recomendaciones específicas]
        
        **🚀 MENSAJE MOTIVACIONAL:**
        [Mensaje final de ánimo personalizado]
        
        Genera una retroalimentación específica, profesional y motivadora.
        """
        
        return prompt

    async def _generate_response(self, prompt: str) -> str:
        """Genera respuesta usando Gemini"""
        try:
            # Ejecutar en un hilo separado para evitar bloqueo
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            raise

    def _process_feedback(self, raw_feedback: str) -> str:
        """Procesa y limpia la retroalimentación generada"""
        try:
            # Limpiar y formatear la respuesta
            feedback = raw_feedback.strip()
            
            # Verificar que la respuesta no esté vacía
            if not feedback:
                raise ValueError("Respuesta vacía de la IA")
            
            # Limitar longitud si es necesario
            if len(feedback) > 1500:
                feedback = feedback[:1500] + "..."
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error procesando feedback: {e}")
            return self._generate_fallback_feedback({})

    def _generate_fallback_feedback(self, profile: Dict) -> str:
        """Genera retroalimentación de respaldo si falla la IA"""
        profile_type = profile.get('type', 'Analítico')
        
        fallback_messages = {
            'Dominante': """
            **🎯 FORTALEZAS IDENTIFICADAS:**
            - Muestras liderazgo natural y capacidad de toma de decisiones
            - Tienes orientación a resultados y objetivos claros
            
            **📈 ÁREAS DE MEJORA:**
            - Desarrolla más la escucha activa en tus respuestas
            - Incluye más ejemplos de trabajo en equipo
            
            **💡 CONSEJOS PRÁCTICOS:**
            - Practica respuestas que muestren empatía y colaboración
            - Prepara ejemplos específicos con métricas de éxito
            
            **🚀 MENSAJE MOTIVACIONAL:**
            Tu perfil de liderazgo es una gran fortaleza. Sigue desarrollando tu capacidad de comunicación y tendrás entrevistas exitosas.
            """,
            
            'Influyente': """
            **🎯 FORTALEZAS IDENTIFICADAS:**
            - Excelente capacidad comunicativa y carisma natural
            - Facilidad para conectar con otros y generar confianza
            
            **📈 ÁREAS DE MEJORA:**
            - Agrega más detalles técnicos y datos concretos
            - Estructura mejor tus respuestas con ejemplos específicos
            
            **💡 CONSEJOS PRÁCTICOS:**
            - Prepara anécdotas con resultados medibles
            - Practica el método STAR para respuestas estructuradas
            
            **🚀 MENSAJE MOTIVACIONAL:**
            Tu habilidad para comunicarte es excepcional. Combinada con preparación técnica, serás imparable en cualquier entrevista.
            """,
            
            'Estable': """
            **🎯 FORTALEZAS IDENTIFICADAS:**
            - Demuestras confiabilidad y consistencia
            - Capacidad de trabajo en equipo y colaboración
            
            **📈 ÁREAS DE MEJORA:**
            - Muestra más iniciativa y proactividad en tus ejemplos
            - Desarrolla respuestas que destaquen tu capacidad de liderazgo
            
            **💡 CONSEJOS PRÁCTICOS:**
            - Prepara historias donde hayas tomado la iniciativa
            - Practica proyectar más confianza en tu lenguaje corporal
            
            **🚀 MENSAJE MOTIVACIONAL:**
            Tu estabilidad y confiabilidad son cualidades muy valoradas. Proyecta más seguridad y destacarás en cualquier proceso.
            """,
            
            'Analítico': """
            **🎯 FORTALEZAS IDENTIFICADAS:**
            - Capacidad de análisis detallado y pensamiento crítico
            - Atención a los detalles y enfoque metodológico
            
            **📈 ÁREAS DE MEJORA:**
            - Sé más conciso en tus respuestas
            - Muestra más tu lado humano y habilidades interpersonales
            
            **💡 CONSEJOS PRÁCTICOS:**
            - Practica resumir ideas complejas de forma simple
            - Prepara ejemplos que muestren tu capacidad de adaptación
            
            **🚀 MENSAJE MOTIVACIONAL:**
            Tu capacidad analítica es tu superpoder. Combínala con storytelling efectivo y serás el candidato ideal.
            """
        }
        
        return fallback_messages.get(profile_type, fallback_messages['Analítico'])

    async def generate_interview_question(self, profile: Dict, previous_answers: List[Dict] = None) -> str:
        """Genera preguntas de entrevista personalizadas basadas en el perfil"""
        try:
            prompt = f"""
            Genera una pregunta de entrevista laboral personalizada para un candidato con perfil {profile.get('type', 'Analítico')}.
            
            Descripción del perfil: {profile.get('description', '')}
            
            Criterios:
            - La pregunta debe ser específica para este tipo de perfil
            - Debe permitir al candidato demostrar sus fortalezas
            - Debe ser profesional y realista
            - Máximo 2 líneas
            
            Responde solo con la pregunta, sin explicaciones adicionales.
            """
            
            response = await self._generate_response(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generando pregunta personalizada: {e}")
            return self._get_fallback_question(profile)

    def _get_fallback_question(self, profile: Dict) -> str:
        """Pregunta de respaldo si falla la generación con IA"""
        profile_type = profile.get('type', 'Analítico')
        
        fallback_questions = {
            'Dominante': "¿Cómo manejas situaciones donde necesitas tomar decisiones rápidas con información limitada?",
            'Influyente': "Describe una situación donde tuviste que persuadir a un equipo para adoptar tu idea.",
            'Estable': "¿Cómo te adaptas a cambios inesperados en proyectos importantes?",
            'Analítico': "Explica un problema complejo que resolviste y el proceso que seguiste."
        }
        
        return fallback_questions.get(profile_type, fallback_questions['Analítico'])

    async def evaluate_answer_quality(self, question: str, answer: str) -> Dict:
        """Evalúa la calidad de una respuesta específica"""
        try:
            prompt = f"""
            Evalúa la siguiente respuesta de entrevista:
            
            PREGUNTA: {question}
            RESPUESTA: {answer}
            
            Califica del 1 al 10 en estas categorías:
            - Claridad: ¿Qué tan clara es la respuesta?
            - Relevancia: ¿Qué tan relevante es para la pregunta?
            - Especificidad: ¿Incluye ejemplos concretos?
            - Profesionalismo: ¿Qué tan profesional suena?
            
            Responde en formato JSON:
            {
                "claridad": número,
                "relevancia": número,
                "especificidad": número,
                "profesionalismo": número,
                "puntuacion_total": número,
                "comentario_breve": "texto"
            }
            """
            
            response = await self._generate_response(prompt)
            
            # Intentar parsear JSON
            try:
                evaluation = json.loads(response)
                return evaluation
            except json.JSONDecodeError:
                # Si falla el parsing, crear evaluación básica
                return {
                    "claridad": 7,
                    "relevancia": 7,
                    "especificidad": 6,
                    "profesionalismo": 7,
                    "puntuacion_total": 6.75,
                    "comentario_breve": "Respuesta adecuada con espacio para mejorar"
                }
                
        except Exception as e:
            logger.error(f"Error evaluando respuesta: {e}")
            return {
                "claridad": 6,
                "relevancia": 6,
                "especificidad": 5,
                "profesionalismo": 6,
                "puntuacion_total": 5.75,
                "comentario_breve": "Evaluación no disponible"
            }

    def get_personalized_tips(self, profile: Dict) -> List[str]:
        """Obtiene consejos personalizados basados en el perfil"""
        profile_type = profile.get('type', 'Analítico')
        
        tips = {
            'Dominante': [
                "Muestra cómo tu liderazgo beneficia al equipo",
                "Incluye ejemplos de toma de decisiones difíciles",
                "Demuestra tu capacidad de delegar efectivamente",
                "Habla sobre cómo manejas la presión y los plazos"
            ],
            'Influyente': [
                "Comparte historias que demuestren tu capacidad de persuasión",
                "Habla sobre cómo motivas a otros hacia objetivos comunes",
                "Incluye ejemplos de networking y construcción de relaciones",
                "Muestra tu adaptabilidad en diferentes audiencias"
            ],
            'Estable': [
                "Destaca tu confiabilidad con ejemplos específicos",
                "Muestra cómo contribuyes a la armonía del equipo",
                "Habla sobre tu capacidad de mantener calidad bajo presión",
                "Incluye ejemplos de apoyo a colegas en momentos difíciles"
            ],
            'Analítico': [
                "Presenta datos y métricas que respalden tus logros",
                "Muestra tu proceso de toma de decisiones basado en datos",
                "Habla sobre cómo tu atención al detalle previno problemas",
                "Incluye ejemplos de análisis que mejoraron procesos"
            ]
        }
        
        return tips.get(profile_type, tips['Analítico'])

    async def health_check(self) -> bool:
        """Verifica que la integración con IA funcione correctamente"""
        try:
            test_prompt = "Responde con 'OK' si recibes este mensaje."
            response = await self._generate_response(test_prompt)
            return 'OK' in response.upper()
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False
import logging
import json
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from database import DatabaseManager
from ai_integration import GeminiIntegration
from scoring_system import ScoringSystem


load_dotenv()
# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados del bot
START, TEST_SELECT, DISC1, DISC2, DISC3, DISC4, HOGAN1, HOGAN2, HOGAN3, HOGAN4, ENTREVISTA, RESTART, CIERRE  = range(13)

class TlabajaBot:
    def __init__(self, token: str, gemini_api_key: str):
        self.token = token
        self.db = DatabaseManager()
        self.ai = GeminiIntegration(gemini_api_key)
        self.scoring = ScoringSystem()
        self.questions = self.load_questions()
        
    def load_questions(self):
        """Carga las preguntas desde archivos JSON"""
        try:
            with open('questions/disc_questions.json', 'r', encoding='utf-8') as f:
                disc_questions = json.load(f)
            with open('questions/hogan_questions.json', 'r', encoding='utf-8') as f:
                hogan_questions = json.load(f)
            with open('questions/interview_questions.json', 'r', encoding='utf-8') as f:
                interview_questions = json.load(f)
            
            return {
                'disc': disc_questions,
                'hogan': hogan_questions,
                'interview': interview_questions
            }
        except FileNotFoundError:
            logger.error("Archivos de preguntas no encontrados")
            return {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Función de inicio del bot"""
        user = update.effective_user
        
        # Inicializar datos del usuario
        context.user_data.clear()
        context.user_data['user_id'] = user.id
        context.user_data['username'] = user.username or user.first_name
        context.user_data['start_time'] = datetime.now()
        
        # Registrar usuario en base de datos
        self.db.insert_user(user.id, user.username or user.first_name)
        
        welcome_message = (
            f"¡Hola {user.first_name}! 👋\n\n"
            "Soy **Tlabaja**, tu entrenador personal para entrevistas de trabajo.\n\n"
            "🎯 **¿Qué haré por ti?**\n"
            "• Realizaré un test de perfilamiento para conocerte mejor\n"
            "• Simularé una entrevista de trabajo real\n"
            "• Te daré retroalimentación personalizada con IA\n\n"
            "💡 **¿Listo para comenzar?**"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 ¡Empezar ahora!", callback_data='start_test')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
        return START
    
    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Función de inicio del bot"""
        user = update.effective_user
        
        # Inicializar datos del usuario
        context.user_data.clear()
        context.user_data['user_id'] = user.id
        context.user_data['username'] = user.username or user.first_name
        context.user_data['start_time'] = datetime.now()
        
        # Registrar usuario en base de datos
        self.db.insert_user(user.id, user.username or user.first_name)
        
        welcome_message = (
            f"¡Hola de nuevo {user.first_name}! 👋\n\n"
            "**¿Listo para intentarlo otra vez? pulsa /start**"
        )
        query = update.callback_query
        await query.answer()
        
        """keyboard = [
            [InlineKeyboardButton("¡Empezar ahora!", callback_data='restart')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)"""
        
        await update.callback_query.edit_message_text(welcome_message, parse_mode='Markdown')
        return ConversationHandler.END

    async def test_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Selección del tipo de test"""
        query = update.callback_query
        await query.answer()
        
        message = (
            "🧠 **Selecciona tu test de perfilamiento:**\n\n"
            "🔵 **Test DISC**: Evalúa tu estilo de comportamiento y comunicación\n"
            "🔴 **Test HOGAN**: Analiza tu personalidad y motivaciones laborales\n\n"
            "Ambos tests son breves (4 preguntas) y me ayudarán a personalizar tu entrevista."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔵 Test DISC", callback_data='disc')],
            [InlineKeyboardButton("🔴 Test HOGAN", callback_data='hogan')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return TEST_SELECT

    async def start_disc_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Inicia el test DISC"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['test_type'] = 'disc'
        context.user_data['disc_answers'] = []
        
        question = self.questions['disc']['questions'][0]
        context.user_data['current_question'] = 0
        
        message = f"**Test DISC - Pregunta 1/4**\n\n{question['question']}"
        
        keyboard = [[InlineKeyboardButton(option, callback_data=f"disc_answer_{i}")] 
        for i, option in enumerate(question['options'])]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return DISC1

    async def handle_disc_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Maneja las respuestas del test DISC"""
        query = update.callback_query
        await query.answer()
        
        # Extraer respuesta
        answer_index = int(query.data.split('_')[-1])
        current_q = context.user_data['current_question']
        
        # Guardar respuesta
        context.user_data['disc_answers'].append({
            'question': current_q,
            'answer': answer_index,
            'value': self.questions['disc']['questions'][current_q]['values'][answer_index]
        })
        
        # Verificar si hay más preguntas
        if current_q < 3:  # 0, 1, 2, 3 = 4 preguntas
            context.user_data['current_question'] += 1
            next_q = context.user_data['current_question']
            question = self.questions['disc']['questions'][next_q]
            
            message = f"**Test DISC - Pregunta {next_q + 1}/4**\n\n{question['question']}"
            
            keyboard = [[InlineKeyboardButton(option, callback_data=f"disc_answer_{i}")] 
            for i, option in enumerate(question['options'])]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return DISC1  # Mantener en el mismo estado
        else:
            # Test completado, calcular perfil
            profile = self.scoring.calculate_disc_profile(context.user_data['disc_answers'])
            context.user_data['profile'] = profile
            
            # Guardar resultados en BD
            self.db.save_test_results(
                context.user_data['user_id'],
                'disc',
                context.user_data['disc_answers'],
                profile
            )
            
            await query.edit_message_text(
                f"✅ **Test DISC completado!**\n\n"
                f"Tu perfil: **{profile['type']}**\n"
                f"{profile['description']}\n\n"
                f"🎯 Ahora comenzaremos la simulación de entrevista...",
                parse_mode='Markdown'
            )
            
            # Esperar 2 segundos antes de continuar
            await asyncio.sleep(2)
            return await self.start_interview(update, context)

    async def start_hogan_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Inicia el test HOGAN"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['test_type'] = 'hogan'
        context.user_data['hogan_answers'] = []
        
        question = self.questions['hogan']['questions'][0]
        context.user_data['current_question'] = 0
        
        message = f"**Test HOGAN - Pregunta 1/4**\n\n{question['question']}"
        
        keyboard = [[InlineKeyboardButton(option, callback_data=f"hogan_answer_{i}")] 
        for i, option in enumerate(question['options'])]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return HOGAN1

    async def handle_hogan_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Maneja las respuestas del test HOGAN"""
        query = update.callback_query
        await query.answer()
        
        # Extraer respuesta
        answer_index = int(query.data.split('_')[-1])
        current_q = context.user_data['current_question']
        
        # Guardar respuesta
        context.user_data['hogan_answers'].append({
            'question': current_q,
            'answer': answer_index,
            'value': self.questions['hogan']['questions'][current_q]['values'][answer_index]
        })
        
        # Verificar si hay más preguntas
        if current_q < 3:  # 0, 1, 2, 3 = 4 preguntas
            context.user_data['current_question'] += 1
            next_q = context.user_data['current_question']
            question = self.questions['hogan']['questions'][next_q]
            
            message = f"**Test HOGAN - Pregunta {next_q + 1}/4**\n\n{question['question']}"
            
            keyboard = [[InlineKeyboardButton(option, callback_data=f"hogan_answer_{i}")] 
            for i, option in enumerate(question['options'])]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return HOGAN1  # Mantener en el mismo estado
        else:
            # Test completado, calcular perfil
            profile = self.scoring.calculate_hogan_profile(context.user_data['hogan_answers'])
            context.user_data['profile'] = profile
            
            # Guardar resultados en BD
            self.db.save_test_results(
                context.user_data['user_id'],
                'hogan',
                context.user_data['hogan_answers'],
                profile
            )
            
            await query.edit_message_text(
                f"✅ **Test HOGAN completado!**\n\n"
                f"Tu perfil: **{profile['type']}**\n"
                f"{profile['description']}\n\n"
                f"🎯 Ahora comenzaremos la simulación de entrevista...",
                parse_mode='Markdown'
            )
            
            # Esperar 2 segundos antes de continuar
            await asyncio.sleep(2)
            return await self.start_interview(update, context)

    async def start_interview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Inicia la simulación de entrevista"""
        context.user_data['interview_answers'] = []
        context.user_data['interview_question'] = 0
        
        # Seleccionar primera pregunta
        questions = self.questions['interview']['questions']
        first_question = questions[0]
        
        message = (
            "🎭 **¡Simulación de Entrevista!**\n\n"
            "Ahora simularé ser tu entrevistador. Responde como lo harías en una entrevista real.\n\n"
            f"**Pregunta 1:** {first_question}\n\n"
            "💡 *Tip: Sé específico y da ejemplos concretos*"
        )
        
        await update.callback_query.edit_message_text(message, parse_mode='Markdown')
        return ENTREVISTA

    async def handle_interview_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Maneja las respuestas de la entrevista"""
        user_answer = update.message.text
        current_q = context.user_data['interview_question']
        
        # Guardar respuesta
        context.user_data['interview_answers'].append({
            'question': self.questions['interview']['questions'][current_q],
            'answer': user_answer,
            'timestamp': datetime.now()
        })
        
        # Verificar si hay más preguntas (máximo 3)
        if current_q < 2:  # 0, 1, 2 = 3 preguntas
            context.user_data['interview_question'] += 1
            next_q = context.user_data['interview_question']
            next_question = self.questions['interview']['questions'][next_q]
            
            message = f"**Pregunta {next_q + 1}:** {next_question}\n\n💡 *Continúa respondiendo naturalmente*"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return ENTREVISTA
        else:
            # Entrevista completada, generar feedback
            await update.message.reply_text(
                "✅ **¡Entrevista completada!**\n\n"
                "🤖 Estoy analizando tus respuestas con IA para darte retroalimentación personalizada...\n\n"
                "⏳ *Esto tomará unos segundos*",
                parse_mode='Markdown'
            )
            
            return await self.generate_feedback(update, context)

    async def generate_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Genera retroalimentación final usando IA"""
        try:
            # Preparar datos para IA
            profile = context.user_data['profile']
            interview_answers = context.user_data['interview_answers']
            
            # Generar feedback con IA
            feedback = await self.ai.generate_feedback(profile, interview_answers)
            
            # Guardar en base de datos
            self.db.save_feedback(
                context.user_data['user_id'],
                feedback,
                datetime.now()
            )
            
            # Mostrar resultados finales
            final_message = (
            f"**¡Felicitaciones {context.user_data['username']}!**\n\n"
            f"**Tu perfil:** {profile['type']}\n\n"
            f"**Retroalimentación personalizada:**\n"
            f"{feedback}\n\n"
            f"**Próximos pasos:**\n"
            f"• Practica las áreas de mejora identificadas\n"
            f"• Repite el proceso cuando quieras con /start\n\n"
            f"¡Mucha suerte en tus entrevistas!"
            )
            
            keyboard = [
                [InlineKeyboardButton("📊 Ver mi historial", callback_data='history')],
                [InlineKeyboardButton("Volver", callback_data='restart')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                final_message, 
                reply_markup=reply_markup, 
                parse_mode='Markdown'
            )
            
            return CIERRE
            
        except Exception as e:
            logger.error(f"Error generando feedback: {e}")
            await update.message.reply_text(
                "❌ Hubo un error generando tu retroalimentación. Por favor, intenta nuevamente con /start",
                parse_mode='Markdown'
            )
            return ConversationHandler.END

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Maneja los callbacks generales"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'start_test':
            return await self.test_select(update, context)
        elif query.data == 'disc':
            return await self.start_disc_test(update, context)
        elif query.data == 'hogan':
            return await self.start_hogan_test(update, context)
        elif query.data == 'restart':
            return await self.restart(update, context)
        elif query.data == 'history':
            return await self.show_history(update, context)
        elif query.data.startswith('disc_answer_'):
            return await self.handle_disc_answer(update, context)
        elif query.data.startswith('hogan_answer_'):
            return await self.handle_hogan_answer(update, context)
        
        return ConversationHandler.END

    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Muestra el historial del usuario"""
        user_id = context.user_data['user_id']
        history = self.db.get_user_history(user_id)
        
        if not history:
            message = "📊 No tienes historial de tests previos."
        else:
            message = "📊 **Tu historial de tests:**\n\n"
            for record in history[-3:]:  # Últimos 3 registros
                message += f"• {record['test_type'].upper()} - {record['date']}\n"
                message += f"  Perfil: {record['profile']}\n\n"
        
        keyboard = [[InlineKeyboardButton("Volver", callback_data='restart')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )
        return CIERRE

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancela la conversación"""
        await update.message.reply_text(
            "❌ Conversación cancelada. Usa /start para comenzar de nuevo."
        )
        return ConversationHandler.END

    def run(self):
        """Ejecuta el bot"""
        application = Application.builder().token(self.token).build()
        
        # Crear handler de conversación
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                START: [CallbackQueryHandler(self.handle_callback)],
                TEST_SELECT: [CallbackQueryHandler(self.handle_callback)],
                DISC1: [CallbackQueryHandler(self.handle_callback)],
                HOGAN1: [CallbackQueryHandler(self.handle_callback)],
                ENTREVISTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_interview_answer)],
                RESTART:[CallbackQueryHandler(self.handle_callback)],
                CIERRE: [CallbackQueryHandler(self.handle_callback)]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
        
        application.add_handler(conv_handler)
        
        # Ejecutar bot
        logger.info("Bot iniciado...")
        application.run_polling()

if __name__ == '__main__':
    # Configuración
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY_')
    
    # Crear y ejecutar bot
    bot = TlabajaBot(BOT_TOKEN, GEMINI_API_KEY)
    bot.run()
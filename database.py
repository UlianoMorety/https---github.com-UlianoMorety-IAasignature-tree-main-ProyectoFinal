import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "tlabaja_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de usuarios
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de resultados de tests
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        test_type TEXT NOT NULL,
                        answers TEXT NOT NULL,
                        profile_type TEXT,
                        profile_description TEXT,
                        score TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabla de respuestas de entrevistas
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interview_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabla de retroalimentación
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        feedback_text TEXT NOT NULL,
                        ai_generated BOOLEAN DEFAULT TRUE,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabla de sesiones
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        session_id TEXT UNIQUE,
                        test_type TEXT,
                        status TEXT DEFAULT 'active',
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Base de datos inicializada correctamente")
                
        except sqlite3.Error as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise

    def insert_user(self, user_id: int, username: str) -> bool:
        """Inserta o actualiza un usuario en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si el usuario existe
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Actualizar última actividad
                    cursor.execute('''
                        UPDATE users 
                        SET last_activity = CURRENT_TIMESTAMP, username = ?
                        WHERE user_id = ?
                    ''', (username, user_id))
                else:
                    # Insertar nuevo usuario
                    cursor.execute('''
                        INSERT INTO users (user_id, username)
                        VALUES (?, ?)
                    ''', (user_id, username))
                
                conn.commit()
                logger.info(f"Usuario {user_id} ({username}) procesado correctamente")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error insertando usuario: {e}")
            return False

    def save_test_results(self, user_id: int, test_type: str, answers: List[Dict], profile: Dict) -> bool:
        """Guarda los resultados de un test"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convertir respuestas a JSON
                answers_json = json.dumps(answers, ensure_ascii=False)
                score_json = json.dumps(profile.get('scores', {}), ensure_ascii=False)
                
                cursor.execute('''
                    INSERT INTO test_results 
                    (user_id, test_type, answers, profile_type, profile_description, score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    test_type,
                    answers_json,
                    profile.get('type', ''),
                    profile.get('description', ''),
                    score_json
                ))
                
                conn.commit()
                logger.info(f"Resultados del test {test_type} guardados para usuario {user_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error guardando resultados del test: {e}")
            return False

    def save_interview_answer(self, user_id: int, question: str, answer: str, session_id: str) -> bool:
        """Guarda una respuesta de entrevista"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO interview_answers 
                    (user_id, question, answer, session_id)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, question, answer, session_id))
                
                conn.commit()
                logger.info(f"Respuesta de entrevista guardada para usuario {user_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error guardando respuesta de entrevista: {e}")
            return False

    def save_feedback(self, user_id: int, feedback_text: str, created_at: datetime, session_id: str = None) -> bool:
        """Guarda retroalimentación generada por IA"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO feedback 
                    (user_id, feedback_text, session_id, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, feedback_text, session_id, created_at))
                
                conn.commit()
                logger.info(f"Retroalimentación guardada para usuario {user_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error guardando retroalimentación: {e}")
            return False

    def get_user_history(self, user_id: int) -> List[Dict]:
        """Obtiene el historial de tests de un usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT test_type, profile_type, profile_description, created_at
                    FROM test_results
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                results = cursor.fetchall()
                
                history = []
                for row in results:
                    history.append({
                        'test_type': row[0],
                        'profile': row[1],
                        'description': row[2],
                        'date': row[3]
                    })
                
                return history
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []

    def get_last_profile(self, user_id: int) -> Optional[Dict]:
        """Obtiene el último perfil calculado para un usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT test_type, profile_type, profile_description, score
                    FROM test_results
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (user_id,))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        'test_type': result[0],
                        'type': result[1],
                        'description': result[2],
                        'scores': json.loads(result[3]) if result[3] else {}
                    }
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo último perfil: {e}")
            return None

    def get_user_statistics(self, user_id: int) -> Dict:
        """Obtiene estadísticas de un usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar tests completados
                cursor.execute('''
                    SELECT COUNT(*) FROM test_results WHERE user_id = ?
                ''', (user_id,))
                total_tests = cursor.fetchone()[0]
                
                # Contar respuestas de entrevistas
                cursor.execute('''
                    SELECT COUNT(*) FROM interview_answers WHERE user_id = ?
                ''', (user_id,))
                total_answers = cursor.fetchone()[0]
                
                # Última actividad
                cursor.execute('''
                    SELECT last_activity FROM users WHERE user_id = ?
                ''', (user_id,))
                last_activity = cursor.fetchone()[0]
                
                return {
                    'total_tests': total_tests,
                    'total_answers': total_answers,
                    'last_activity': last_activity
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def create_session(self, user_id: int, test_type: str) -> str:
        """Crea una nueva sesión de usuario"""
        try:
            session_id = f"{user_id}_{int(datetime.now().timestamp())}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO sessions (user_id, session_id, test_type)
                    VALUES (?, ?, ?)
                ''', (user_id, session_id, test_type))
                
                conn.commit()
                logger.info(f"Sesión {session_id} creada para usuario {user_id}")
                return session_id
                
        except sqlite3.Error as e:
            logger.error(f"Error creando sesión: {e}")
            return f"{user_id}_{int(datetime.now().timestamp())}"  # Fallback

    def complete_session(self, session_id: str) -> bool:
        """Marca una sesión como completada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE sessions 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (session_id,))
                
                conn.commit()
                logger.info(f"Sesión {session_id} marcada como completada")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error completando sesión: {e}")
            return False

    def get_database_stats(self) -> Dict:
        """Obtiene estadísticas generales de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de usuarios
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Total de tests
                cursor.execute("SELECT COUNT(*) FROM test_results")
                total_tests = cursor.fetchone()[0]
                
                # Tests por tipo
                cursor.execute('''
                    SELECT test_type, COUNT(*) 
                    FROM test_results 
                    GROUP BY test_type
                ''')
                tests_by_type = dict(cursor.fetchall())
                
                # Usuarios activos (últimos 7 días)
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity >= datetime('now', '-7 days')
                ''')
                active_users = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users,
                    'total_tests': total_tests,
                    'tests_by_type': tests_by_type,
                    'active_users_7d': active_users
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo estadísticas de BD: {e}")
            return {}

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Limpia sesiones antiguas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM sessions 
                    WHERE started_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Limpiadas {deleted_count} sesiones antiguas")
                return deleted_count
                
        except sqlite3.Error as e:
            logger.error(f"Error limpiando sesiones: {e}")
            return 0

    def backup_database(self, backup_path: str = None) -> bool:
        """Crea una copia de seguridad de la base de datos"""
        try:
            if backup_path is None:
                backup_path = f"backup_tlabaja_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            logger.info(f"Backup creado en: {backup_path}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error creando backup: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        logger.info("Conexión a base de datos cerrada")
        # SQLite no requiere cierre explícito con context managers
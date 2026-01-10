"""
Base de datos PostgreSQL/SQLite para App Soporte
Usa PostgreSQL en Railway, SQLite en desarrollo local
"""
import os
from datetime import datetime, date

# Detectar si estamos en Railway (tiene DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL en Railway
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = True
    print("📦 Usando PostgreSQL")
else:
    # SQLite local
    import sqlite3
    USE_POSTGRES = False
    DB_PATH = 'soporte.db'
    print("📦 Usando SQLite local")

def get_connection():
    """Obtiene conexión a la base de datos"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(sql, params=None, fetch=True):
    """Ejecuta una consulta y retorna resultados"""
    conn = get_connection()
    
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Convertir ? a %s para PostgreSQL
        sql = sql.replace('?', '%s')
    else:
        cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if fetch:
            rows = cursor.fetchall()
            if USE_POSTGRES:
                return [dict(row) for row in rows]
            else:
                return [dict(row) for row in rows]
        else:
            conn.commit()
            if USE_POSTGRES:
                # Para INSERT con RETURNING
                if 'RETURNING' in sql.upper():
                    row = cursor.fetchone()
                    return row['id'] if row else None
                return cursor.rowcount
            else:
                return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def init_db():
    """Inicializa las tablas de la base de datos"""
    conn = get_connection()
    
    if USE_POSTGRES:
        cursor = conn.cursor()
        
        # Tabla de Soportistas (crear primero por las FK)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soportistas (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                correo TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                correo TEXT,
                telefono TEXT,
                soportista_id INTEGER REFERENCES soportistas(id),
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de Visitas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitas (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id),
                soportista_id INTEGER NOT NULL REFERENCES soportistas(id),
                persona_atendida TEXT,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                duracion_minutos INTEGER NOT NULL,
                trabajo_realizado TEXT NOT NULL,
                tiene_pendiente INTEGER DEFAULT 0,
                descripcion_pendiente TEXT,
                pendiente_resuelto INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de Configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        
        # SQLite - Tabla de Soportistas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soportistas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT,
                telefono TEXT,
                soportista_id INTEGER,
                activo INTEGER DEFAULT 1,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (soportista_id) REFERENCES soportistas(id)
            )
        ''')
        
        # Agregar columna soportista_id si no existe (para BD existentes)
        try:
            cursor.execute('ALTER TABLE clientes ADD COLUMN soportista_id INTEGER')
        except:
            pass
        
        # Tabla de Visitas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                soportista_id INTEGER NOT NULL,
                persona_atendida TEXT,
                fecha TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                duracion_minutos INTEGER NOT NULL,
                trabajo_realizado TEXT NOT NULL,
                tiene_pendiente INTEGER DEFAULT 0,
                descripcion_pendiente TEXT,
                pendiente_resuelto INTEGER DEFAULT 0,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (soportista_id) REFERENCES soportistas(id)
            )
        ''')
        
        # Tabla de Configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

# ============== CLIENTES ==============

def obtener_clientes(solo_activos=True, soportista_id=None):
    """Obtiene lista de clientes, opcionalmente filtrados por soportista"""
    sql = '''
        SELECT c.*, s.nombre as soportista_nombre 
        FROM clientes c
        LEFT JOIN soportistas s ON c.soportista_id = s.id
        WHERE 1=1
    '''
    params = []
    
    if solo_activos:
        sql += ' AND c.activo = 1'
    if soportista_id:
        sql += ' AND c.soportista_id = ?'
        params.append(soportista_id)
    
    sql += ' ORDER BY c.nombre'
    
    return execute_query(sql, params if params else None)

def obtener_cliente(id):
    """Obtiene un cliente por ID"""
    rows = execute_query('SELECT * FROM clientes WHERE id = ?', (id,))
    return rows[0] if rows else None

def guardar_cliente(nombre, correo, telefono, soportista_id=None, id=None):
    """Guarda o actualiza un cliente"""
    if id:
        execute_query('''
            UPDATE clientes SET nombre=?, correo=?, telefono=?, soportista_id=? WHERE id=?
        ''', (nombre, correo, telefono, soportista_id, id), fetch=False)
        return id
    else:
        if USE_POSTGRES:
            return execute_query('''
                INSERT INTO clientes (nombre, correo, telefono, soportista_id) 
                VALUES (?, ?, ?, ?) RETURNING id
            ''', (nombre, correo, telefono, soportista_id), fetch=False)
        else:
            return execute_query('''
                INSERT INTO clientes (nombre, correo, telefono, soportista_id) VALUES (?, ?, ?, ?)
            ''', (nombre, correo, telefono, soportista_id), fetch=False)

def eliminar_cliente(id):
    """Desactiva un cliente (borrado lógico)"""
    execute_query('UPDATE clientes SET activo = 0 WHERE id = ?', (id,), fetch=False)

# ============== SOPORTISTAS ==============

def obtener_soportistas(solo_activos=True):
    """Obtiene lista de soportistas"""
    if solo_activos:
        return execute_query('SELECT * FROM soportistas WHERE activo = 1 ORDER BY nombre')
    else:
        return execute_query('SELECT * FROM soportistas ORDER BY nombre')

def obtener_soportista(id):
    """Obtiene un soportista por ID"""
    rows = execute_query('SELECT * FROM soportistas WHERE id = ?', (id,))
    return rows[0] if rows else None

def guardar_soportista(nombre, correo, id=None):
    """Guarda o actualiza un soportista"""
    if id:
        execute_query('''
            UPDATE soportistas SET nombre=?, correo=? WHERE id=?
        ''', (nombre, correo, id), fetch=False)
        return id
    else:
        if USE_POSTGRES:
            return execute_query('''
                INSERT INTO soportistas (nombre, correo) VALUES (?, ?) RETURNING id
            ''', (nombre, correo), fetch=False)
        else:
            return execute_query('''
                INSERT INTO soportistas (nombre, correo) VALUES (?, ?)
            ''', (nombre, correo), fetch=False)

def eliminar_soportista(id):
    """Desactiva un soportista (borrado lógico)"""
    execute_query('UPDATE soportistas SET activo = 0 WHERE id = ?', (id,), fetch=False)

# ============== VISITAS ==============

def guardar_visita(cliente_id, soportista_id, persona_atendida, fecha, hora_inicio, 
                   duracion_minutos, trabajo_realizado, tiene_pendiente=False, 
                   descripcion_pendiente=None, id=None):
    """Guarda o actualiza una visita"""
    tiene_pend = 1 if tiene_pendiente else 0
    
    if id:
        execute_query('''
            UPDATE visitas SET cliente_id=?, soportista_id=?, persona_atendida=?,
            fecha=?, hora_inicio=?, duracion_minutos=?, trabajo_realizado=?,
            tiene_pendiente=?, descripcion_pendiente=? WHERE id=?
        ''', (cliente_id, soportista_id, persona_atendida, fecha, hora_inicio,
              duracion_minutos, trabajo_realizado, tiene_pend,
              descripcion_pendiente, id), fetch=False)
        return id
    else:
        if USE_POSTGRES:
            return execute_query('''
                INSERT INTO visitas (cliente_id, soportista_id, persona_atendida, fecha,
                hora_inicio, duracion_minutos, trabajo_realizado, tiene_pendiente, descripcion_pendiente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id
            ''', (cliente_id, soportista_id, persona_atendida, fecha, hora_inicio,
                  duracion_minutos, trabajo_realizado, tiene_pend,
                  descripcion_pendiente), fetch=False)
        else:
            return execute_query('''
                INSERT INTO visitas (cliente_id, soportista_id, persona_atendida, fecha,
                hora_inicio, duracion_minutos, trabajo_realizado, tiene_pendiente, descripcion_pendiente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cliente_id, soportista_id, persona_atendida, fecha, hora_inicio,
                  duracion_minutos, trabajo_realizado, tiene_pend,
                  descripcion_pendiente), fetch=False)

def obtener_visita(id):
    """Obtiene una visita por ID con datos de cliente y soportista"""
    rows = execute_query('''
        SELECT v.*, c.nombre as cliente_nombre, c.correo as cliente_correo,
               s.nombre as soportista_nombre
        FROM visitas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN soportistas s ON v.soportista_id = s.id
        WHERE v.id = ?
    ''', (id,))
    return rows[0] if rows else None

def obtener_visitas_cliente(cliente_id, fecha_desde=None, fecha_hasta=None):
    """Obtiene visitas de un cliente en un rango de fechas"""
    sql = '''
        SELECT v.*, c.nombre as cliente_nombre, c.correo as cliente_correo,
               s.nombre as soportista_nombre
        FROM visitas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN soportistas s ON v.soportista_id = s.id
        WHERE v.cliente_id = ?
    '''
    params = [cliente_id]
    
    if fecha_desde:
        sql += ' AND v.fecha >= ?'
        params.append(fecha_desde)
    if fecha_hasta:
        sql += ' AND v.fecha <= ?'
        params.append(fecha_hasta)
    
    sql += ' ORDER BY v.fecha DESC, v.hora_inicio DESC'
    
    return execute_query(sql, params)

def obtener_pendientes(solo_no_resueltos=True):
    """Obtiene visitas con pendientes"""
    sql = '''
        SELECT v.*, c.nombre as cliente_nombre, c.correo as cliente_correo,
               s.nombre as soportista_nombre
        FROM visitas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN soportistas s ON v.soportista_id = s.id
        WHERE v.tiene_pendiente = 1
    '''
    if solo_no_resueltos:
        sql += ' AND v.pendiente_resuelto = 0'
    sql += ' ORDER BY v.fecha DESC'
    
    return execute_query(sql)

def resolver_pendiente(visita_id):
    """Marca un pendiente como resuelto"""
    execute_query('UPDATE visitas SET pendiente_resuelto = 1 WHERE id = ?', (visita_id,), fetch=False)

def calcular_tiempo_total(visitas):
    """Calcula el tiempo total en minutos de una lista de visitas"""
    return sum(v['duracion_minutos'] for v in visitas)

def formatear_duracion(minutos):
    """Formatea minutos a horas:minutos"""
    horas = minutos // 60
    mins = minutos % 60
    if horas > 0:
        return f"{horas}h {mins}m"
    return f"{mins}m"

# ============== ESTADÍSTICAS ==============

def obtener_estadisticas_clientes(soportista_id=None, fecha_desde=None, fecha_hasta=None):
    """Obtiene resumen de boletas por cliente: cantidad y tiempo total"""
    sql = '''
        SELECT c.id, c.nombre as cliente_nombre, 
               COUNT(v.id) as cantidad_boletas,
               COALESCE(SUM(v.duracion_minutos), 0) as tiempo_total
        FROM clientes c
        LEFT JOIN visitas v ON c.id = v.cliente_id
    '''
    params = []
    where_clauses = ['c.activo = 1']
    
    # Filtros de fecha solo aplican a las visitas
    if fecha_desde:
        where_clauses.append('(v.fecha >= ? OR v.id IS NULL)')
        params.append(fecha_desde)
    if fecha_hasta:
        where_clauses.append('(v.fecha <= ? OR v.id IS NULL)')
        params.append(fecha_hasta)
    if soportista_id:
        where_clauses.append('c.soportista_id = ?')
        params.append(soportista_id)
    
    if where_clauses:
        sql += ' WHERE ' + ' AND '.join(where_clauses)
    
    sql += ' GROUP BY c.id, c.nombre ORDER BY c.nombre'
    
    return execute_query(sql, params if params else None)

def obtener_clientes_sin_boletas(soportista_id=None, fecha_desde=None, fecha_hasta=None):
    """Obtiene clientes que NO tuvieron boletas en el período"""
    # Primero obtenemos los IDs de clientes que SÍ tienen boletas en el período
    sql_con_boletas = '''
        SELECT DISTINCT cliente_id FROM visitas WHERE 1=1
    '''
    params_boletas = []
    
    if fecha_desde:
        sql_con_boletas += ' AND fecha >= ?'
        params_boletas.append(fecha_desde)
    if fecha_hasta:
        sql_con_boletas += ' AND fecha <= ?'
        params_boletas.append(fecha_hasta)
    
    # Ahora buscamos clientes que NO están en esa lista
    sql = f'''
        SELECT c.id, c.nombre as cliente_nombre, s.nombre as soportista_nombre
        FROM clientes c
        LEFT JOIN soportistas s ON c.soportista_id = s.id
        WHERE c.activo = 1 
        AND c.id NOT IN ({sql_con_boletas})
    '''
    params = params_boletas.copy()
    
    if soportista_id:
        sql += ' AND c.soportista_id = ?'
        params.append(soportista_id)
    
    sql += ' ORDER BY c.nombre'
    
    return execute_query(sql, params if params else None)

# ============== CONFIGURACIÓN ==============

def obtener_config(clave, default=None):
    """Obtiene un valor de configuración"""
    rows = execute_query('SELECT valor FROM configuracion WHERE clave = ?', (clave,))
    return rows[0]['valor'] if rows else default

def guardar_config(clave, valor):
    """Guarda un valor de configuración"""
    if USE_POSTGRES:
        execute_query('''
            INSERT INTO configuracion (clave, valor) VALUES (?, ?)
            ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor
        ''', (clave, valor), fetch=False)
    else:
        execute_query('''
            INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)
        ''', (clave, valor), fetch=False)

# Inicializar BD al importar
init_db()

"""
Base de datos SQLite para App Soporte
"""
import sqlite3
import os
from datetime import datetime, date

# Ruta de la base de datos
DB_PATH = os.environ.get('DB_PATH', 'soporte.db')

def get_connection():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    return conn

def init_db():
    """Inicializa las tablas de la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
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
        pass  # La columna ya existe
    
    # Tabla de Soportistas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soportistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    conn = get_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def obtener_cliente(id):
    """Obtiene un cliente por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def guardar_cliente(nombre, correo, telefono, soportista_id=None, id=None):
    """Guarda o actualiza un cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    if id:
        cursor.execute('''
            UPDATE clientes SET nombre=?, correo=?, telefono=?, soportista_id=? WHERE id=?
        ''', (nombre, correo, telefono, soportista_id, id))
    else:
        cursor.execute('''
            INSERT INTO clientes (nombre, correo, telefono, soportista_id) VALUES (?, ?, ?, ?)
        ''', (nombre, correo, telefono, soportista_id))
        id = cursor.lastrowid
    conn.commit()
    conn.close()
    return id

def eliminar_cliente(id):
    """Desactiva un cliente (borrado lógico)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE clientes SET activo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# ============== SOPORTISTAS ==============

def obtener_soportistas(solo_activos=True):
    """Obtiene lista de soportistas"""
    conn = get_connection()
    cursor = conn.cursor()
    if solo_activos:
        cursor.execute('SELECT * FROM soportistas WHERE activo = 1 ORDER BY nombre')
    else:
        cursor.execute('SELECT * FROM soportistas ORDER BY nombre')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def obtener_soportista(id):
    """Obtiene un soportista por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM soportistas WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def guardar_soportista(nombre, correo, id=None):
    """Guarda o actualiza un soportista"""
    conn = get_connection()
    cursor = conn.cursor()
    if id:
        cursor.execute('''
            UPDATE soportistas SET nombre=?, correo=? WHERE id=?
        ''', (nombre, correo, id))
    else:
        cursor.execute('''
            INSERT INTO soportistas (nombre, correo) VALUES (?, ?)
        ''', (nombre, correo))
        id = cursor.lastrowid
    conn.commit()
    conn.close()
    return id

def eliminar_soportista(id):
    """Desactiva un soportista (borrado lógico)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE soportistas SET activo = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# ============== VISITAS ==============

def guardar_visita(cliente_id, soportista_id, persona_atendida, fecha, hora_inicio, 
                   duracion_minutos, trabajo_realizado, tiene_pendiente=False, 
                   descripcion_pendiente=None, id=None):
    """Guarda o actualiza una visita"""
    conn = get_connection()
    cursor = conn.cursor()
    if id:
        cursor.execute('''
            UPDATE visitas SET cliente_id=?, soportista_id=?, persona_atendida=?,
            fecha=?, hora_inicio=?, duracion_minutos=?, trabajo_realizado=?,
            tiene_pendiente=?, descripcion_pendiente=? WHERE id=?
        ''', (cliente_id, soportista_id, persona_atendida, fecha, hora_inicio,
              duracion_minutos, trabajo_realizado, 1 if tiene_pendiente else 0,
              descripcion_pendiente, id))
    else:
        cursor.execute('''
            INSERT INTO visitas (cliente_id, soportista_id, persona_atendida, fecha,
            hora_inicio, duracion_minutos, trabajo_realizado, tiene_pendiente, descripcion_pendiente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_id, soportista_id, persona_atendida, fecha, hora_inicio,
              duracion_minutos, trabajo_realizado, 1 if tiene_pendiente else 0,
              descripcion_pendiente))
        id = cursor.lastrowid
    conn.commit()
    conn.close()
    return id

def obtener_visita(id):
    """Obtiene una visita por ID con datos de cliente y soportista"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, c.nombre as cliente_nombre, c.correo as cliente_correo,
               s.nombre as soportista_nombre
        FROM visitas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN soportistas s ON v.soportista_id = s.id
        WHERE v.id = ?
    ''', (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def obtener_visitas_cliente(cliente_id, fecha_desde=None, fecha_hasta=None):
    """Obtiene visitas de un cliente en un rango de fechas"""
    conn = get_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def obtener_pendientes(solo_no_resueltos=True):
    """Obtiene visitas con pendientes"""
    conn = get_connection()
    cursor = conn.cursor()
    
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
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def resolver_pendiente(visita_id):
    """Marca un pendiente como resuelto"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE visitas SET pendiente_resuelto = 1 WHERE id = ?', (visita_id,))
    conn.commit()
    conn.close()

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

# ============== CONFIGURACIÓN ==============

def obtener_config(clave, default=None):
    """Obtiene un valor de configuración"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT valor FROM configuracion WHERE clave = ?', (clave,))
    row = cursor.fetchone()
    conn.close()
    return row['valor'] if row else default

def guardar_config(clave, valor):
    """Guarda un valor de configuración"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)
    ''', (clave, valor))
    conn.commit()
    conn.close()

# Inicializar BD al importar
init_db()


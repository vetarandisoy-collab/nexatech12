# -*- coding: utf-8 -*-
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'nexatech_secret_2024'

# Función de conexión configurada con tu base de datos en Supabase
def get_db():
    conn = psycopg2.connect(
        host='aws-0-ca-central-1.pooler.supabase.com',  # Host del Pooler
        database='postgres',                             # Base de datos
        user='postgres.omuxvlmbmpjxbbymfocz',            # Usuario con el ID del proyecto
        password='londres2456',                          # Tu contraseña
        port='5432',                                     # Puerto en modo Session
        sslmode='require'                                # Requerido por Supabase
    )
    cur = conn.cursor()
    cur.execute("SET search_path TO nexatech_db;")
    return conn, cur


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/productos')
def productos():
    conn = None
    cur = None
    productos = []
    try:
        conn, cur = get_db()
        cur.execute("""
            SELECT p.nombre, p.sku, p.precio_venta,
                   c.nombre AS categoria,
                   COALESCE(SUM(i.stock_actual), 0) AS stock_total
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = TRUE
            GROUP BY p.id_producto, p.nombre, p.sku, p.precio_venta, c.nombre
            ORDER BY c.nombre, p.nombre;
        """)
        rows = cur.fetchall()
        for row in rows:
            productos.append({
                'nombre': row[0],
                'sku': row[1],
                'precio_venta': row[2],
                'categoria': row[3] if row[3] else 'Sin categoría',
                'stock_total': row[4]
            })
    except Exception as exc:
        app.logger.error('Error al cargar productos: %s', exc)
        flash('Hubo un error al cargar los productos. Intenta nuevamente más tarde.', 'danger')
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    return render_template('productos.html', productos=productos)


@app.route('/inventario')
def inventario():
    conn = None
    cur = None
    almacenes = []
    alertas = []
    try:
        conn, cur = get_db()
        cur.execute('SELECT * FROM almacenes ORDER BY id_almacen;')
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        for row in rows:
            almacenes.append(dict(zip(columns, row)))

        cur.execute('SELECT * FROM vw_alerta_stock_minimo;')
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        for row in rows:
            alertas.append(dict(zip(columns, row)))
    except Exception as exc:
        app.logger.error('Error al cargar inventario: %s', exc)
        flash('Hubo un error al cargar el inventario. Intenta nuevamente más tarde.', 'danger')
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    return render_template('inventario.html', almacenes=almacenes, alertas=alertas)


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        flash(f'¡Mensaje enviado con éxito! Gracias por {nombre or "tu consulta"}.', 'success')
        return redirect(url_for('contacto'))
    return render_template('contacto.html')


@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


@app.route('/servicios')
def servicios():
    return render_template('servicios.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == '__main__':
    try:
        conn, cur = get_db()
        cur.close()
        conn.close()
        print('✅ Conectado a PostgreSQL en Supabase - nexatech_db')
    except Exception as exc:
        print('❌ No se pudo conectar a PostgreSQL:', exc)
    app.run(debug=True)
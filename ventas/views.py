from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from django.contrib import messages
from django.http import HttpResponse
from .services.regresion_lineal import RegresionLinealService
from .services.modelos_predictivos import ModelosPredictivosService
import mysql.connector
import json
import os

def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.perfilusuario.rol != 'ADMIN':
            return HttpResponse("No tienes permiso")
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dashboard(request):
    rol = request.user.perfilusuario.rol

    return render(request, 'dashboard.html', {
        'rol': rol
    })

@login_required
@solo_admin
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')

        if not username or not email or not password or not rol:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('crear_usuario')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect('crear_usuario')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('crear_usuario')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.perfilusuario.rol = rol
        user.perfilusuario.save()

        messages.success(request, "Usuario creado correctamente.")
        return redirect('crear_usuario')

    return render(request, 'c_usuario.html')


# 🧪 TEST DB
@login_required
def test_db(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()

    return HttpResponse(f"Conectado a: {db}")


def prueba_ml(request):

    servicio = RegresionLinealService()
    resultado = servicio.entrenar_modelo()
    servicio_modelos = ModelosPredictivosService()
    modelos = servicio_modelos.obtener_modelos()

    prediccion = resultado["prediccion"]
    meses = resultado["meses"]
    ventas_mensuales = resultado["ventas_mensuales"]
    mes_prediccion = resultado["mes_prediccion"]
    mae = resultado["mae"]
    mape = resultado["mape"]
    print("MAE:", mae)
    print("MAPE:", mape)

    print("ENTRÉ A PRUEBA ML")

    servicio = RegresionLinealService()
    resultado = servicio.entrenar_modelo()

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
)

    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM producto")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM venta")
    total_ventas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT categoria, SUM(cantidad) AS total
        FROM venta
        GROUP BY categoria
        ORDER BY total DESC
        LIMIT 1
    """)

    categoria_top = cursor.fetchone()

    cursor.execute("""
    SELECT producto, SUM(cantidad) AS total
    FROM venta
    GROUP BY producto
    ORDER BY total DESC
    LIMIT 1
    """)

    producto_top = cursor.fetchone()
    promedio_mensual = round(producto_top[1] / 12)
    stock_sugerido = promedio_mensual + 10

    cursor.execute("""
    SELECT 
        MONTH(fecha) AS mes,
        SUM(cantidad) AS total_vendido
        FROM venta
        WHERE producto = %s
        AND YEAR(fecha) = 2025
        GROUP BY MONTH(fecha)
        ORDER BY MONTH(fecha)
    """, (producto_top[0],))

    ventas_producto_mes = cursor.fetchall()

    total_producto_top = sum(fila[1] for fila in ventas_producto_mes)
    conexion.close()

    return render(request, "prediccion.html", {
        "prediccion": prediccion,
        "modelos": modelos,
        "total_productos": total_productos,
        "total_ventas": total_ventas,
        "categoria_top": categoria_top,
        "meses": json.dumps(meses),
        "ventas_mensuales": json.dumps(ventas_mensuales),
        "mes_prediccion": mes_prediccion,
        "mae": mae,
        "mape": mape,
        "stock_sugerido": stock_sugerido,
        "producto_top": producto_top,
        "promedio_mensual": promedio_mensual,
        "ventas_producto_mes": ventas_producto_mes,
        "total_producto_top": total_producto_top,
    })
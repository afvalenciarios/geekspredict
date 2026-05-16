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

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="andresvalencia",
        database="geekspredict_db"
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

    conexion.close()

    return render(request, "prediccion.html", {
        "prediccion": prediccion,
        "modelos": modelos,
        "total_productos": total_productos,
        "total_ventas": total_ventas,
        "categoria_top": categoria_top,
        "meses": json.dumps(meses),
        "ventas_mensuales": json.dumps(ventas_mensuales),
        "mes_prediccion": mes_prediccion
    })
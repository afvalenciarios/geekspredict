from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from django.contrib import messages


# 🔒 SOLO ADMIN
def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.perfilusuario.rol != 'ADMIN':
            return HttpResponse("No tienes permiso")
        return view_func(request, *args, **kwargs)
    return wrapper


# 📊 DASHBOARD
@login_required
def dashboard(request):
    rol = request.user.perfilusuario.rol

    return render(request, 'dashboard.html', {
        'rol': rol
    })


# 👤 CREAR USUARIO
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
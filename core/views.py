import requests
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.
def index(request):
    usuario = request.session.get('usuario')
    return render(request, 'core/index.html', {'usuario': usuario})

def about(request):
    return render(request, 'core/about.html')

def cart(request):
    return render(request, 'core/cart.html')

def checkout(request):
    return render(request, 'core/checkout.html')

def contact(request):
    return render(request, 'core/contact.html')

def shop_single(request):
    return render(request, 'core/shop-single.html')

def shop(request):
    return render(request, 'core/shop.html')

def thankyou(request):
    return render(request, 'core/thankyou.html')

def base(request):
    usuario = request.session.get('usuario')
    return render(request, 'core/base.html', {'usuario': usuario})

#def login(request):
    form = AuthenticationForm()
    return render(request, 'core/registration/login.html', {'form':form})

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        try:
            # 1. Consulta todos los usuarios desde la API de json-server
            response = requests.get('http://localhost:3001/usuarios')
            if response.status_code == 200:
                usuarios = response.json()

                # 2. Buscar el usuario que coincida con correo y contraseña
                usuario = next(
                    (u for u in usuarios if u['correo_user'] == correo and u['contrasena_user'] == contrasena),
                    None
                )

                if usuario:
                    # 3. Guardar usuario en sesión
                    request.session['usuario'] = usuario
                    messages.success(request, f"Bienvenido {usuario['nombre']}")
                    return redirect('index')  # Cambia a la URL real de tu página principal
                else:
                    messages.error(request, "Correo o contraseña incorrectos")
            else:
                messages.error(request, "Error al conectar con la API")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor de la API")

    return render(request, 'core/registration/login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('index')
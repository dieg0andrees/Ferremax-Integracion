import requests
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .decorators import *

# Create your views here.
def index(request):
    usuario = request.session.get('usuario')
    return render(request, 'core/index.html', {'usuario': usuario})

def about(request):
    return render(request, 'core/about.html')

#def cart(request):
    return render(request, 'core/cart.html')

def checkout(request):
    return render(request, 'core/checkout.html')

def contact(request):
    return render(request, 'core/contact.html')

def shop_single(request):
    return render(request, 'core/shop-single.html')

#def shop(request):
    return render(request, 'core/shop.html')

def thankyou(request):
    return render(request, 'core/thankyou.html')

#def register(request):
    return render(request,'core/registration/register.html')

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
            response = requests.get('http://localhost:8001/usuarios')
            if response.status_code == 200:
                usuarios = response.json()

                # 2. Buscar el usuario que coincida con correo y contraseña
                usuario = next(
                    (u for u in usuarios if u['correo_usuario'] == correo and u['contrasena_usuario'] == contrasena),
                    None
                )

                if usuario:
                    # 3. Guardar usuario en sesión
                    request.session['usuario'] = usuario
                    messages.success(request, f"Bienvenido {usuario['nombre']}")
                    return redirect('index')
                else:
                    messages.error(request, "Correo o contraseña incorrectos")
            else:
                messages.error(request, "Error al conectar con la API")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor de la API")

    return render(request, 'core/registration/login.html')

def register(request):
    if request.method == 'POST':
        data = {
            "rut_user": request.POST.get("rut_user"),
            "nombre_user": request.POST.get("nombre"),
            "p_apellido": request.POST.get("p_apellido"),
            "s_apellido": request.POST.get("s_apellido"),
            "correo_user": request.POST.get("correo_user"),
            "contrasena_user": request.POST.get("contrasena_user"),
            "id_genero": int(request.POST.get("id_genero")),
            "id_rol": int(request.POST.get("id_rol"))
        }
        
        try:
            response = requests.post("http://localhost:8001/usuarios", json=data)
            if response.status_code == 200:
                messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
                return redirect("login")
            else:
                messages.error(request, "Error al registrar. Verifica los datos."+str(data))
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor.")
    
    return render(request, "core/registration/register.html")

def logout_view(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('index')

@solo_admin
def home_admin(request):
    response = requests.get('http://localhost:8001/usuarios')
    colaboradores = response.json()
    empleados = [u for u in colaboradores if u.get("rol") != "Cliente"]

    paginator = Paginator(colaboradores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista' : empleados,
        'page_obj' : page_obj
    }

    return render(request, "core/admin/home.html", aux)

@solo_admin
def add_empleado(request):
    if request.method == 'POST':
        data = {
            "rut_user": request.POST.get("rut_user"),
            "nombre_user": request.POST.get("nombre"),
            "p_apellido": request.POST.get("p_apellido"),
            "s_apellido": request.POST.get("s_apellido"),
            "correo_user": request.POST.get("correo_user"),
            "contrasena_user": request.POST.get("contrasena_user"),
            "id_genero": int(request.POST.get("id_genero")),
            "id_rol": int(request.POST.get("id_rol"))
        }

        try:
            response = requests.post("http://localhost:8001/usuarios", json=data)
            if response.status_code == 200 or response.status_code == 201:
                messages.success(request, "Empleado agregado correctamente.")
                return redirect("home_admin")
            else:
                messages.error(request, "Error al registrar el empleado.")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor de la API.")

    return render(request, "core/admin/add_empleado.html")

@solo_admin
def update_empleado(request, rut):
    try:
        get_response = requests.get(f"http://localhost:8001/usuarios/{rut}")
        if get_response.status_code != 200:
            messages.error(request, "Empleado no encontrado.")
            return redirect("home_admin")
        empleado = get_response.json()
    except requests.exceptions.RequestException:
        messages.error(request, "Error al conectar con el servidor.")
        return redirect("home_admin")

    if request.method == 'POST':
        data = {
            "nombre_user": request.POST.get("nombre"),
            "p_apellido": request.POST.get("p_apellido"),
            "s_apellido": request.POST.get("s_apellido"),
            "correo_user": request.POST.get("correo_user"),
            "contrasena_user": request.POST.get("contrasena_user"),
            "id_genero": int(request.POST.get("id_genero")),
            "id_rol": int(request.POST.get("id_rol"))
        }

        try:
            response = requests.put(f"http://localhost:8001/usuarios/{rut}", json=data)
            if response.status_code == 200:
                messages.success(request, "Empleado actualizado correctamente.")
                return redirect("home_admin")
            else:
                messages.error(request, "Error al actualizar el empleado.")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor.")

    return render(request, "core/admin/update_empleado.html", {"empleado": empleado})

@solo_admin
def delete_empleado(request, rut):
    try:
        response = requests.delete(f"http://localhost:8001/usuarios/{rut}")
        if response.status_code == 200:
            messages.success(request, "Empleado eliminado correctamente.")
        elif response.status_code == 404:
            messages.error(request, "Empleado no encontrado.")
        else:
            messages.error(request, f"Error al eliminar el empleado. Código: {response.status_code}")
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con el servidor de la API.")

    return redirect("home_admin")

def productos_view(request):
    try:
        response = requests.get("http://localhost:3000/productos")
        if response.status_code == 200:
            productos = response.json()
        else:
            productos = []
            messages.error(request, "No se pudieron obtener los productos.")
    except requests.exceptions.RequestException:
        productos = []
        messages.error(request, "Error de conexión con la API de productos.")
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    aux = {
        'productos' : productos,
        'page_obj' : page_obj
    }
    return render(request, "core/shop.html", aux)

def agregar_al_carrito(request):
    if request.method == 'POST':
        id_producto = request.POST.get('id_producto')
        if not id_producto:
            messages.error(request, "No se recibió ID de producto.")
            return redirect('shop')

        id_producto = str(id_producto)
        carrito = request.session.get('carrito', {})
        carrito[id_producto] = carrito.get(id_producto, 0) + 1
        request.session['carrito'] = carrito
        request.session.modified = True  # Forzar actualización en sesión

        print("Producto agregado:", id_producto)
        print("Carrito actual:", carrito)

        messages.success(request, "Producto agregado al carrito.")
    return redirect('shop')

def cart(request):
    carrito = request.session.get("carrito", {})
    productos_en_carrito = []
    total_general = 0

    try:
        response = requests.get("http://localhost:3000/productos")
        if response.status_code == 200:
            todos_los_productos = response.json()
            # Indexar por id_producto (¡ojo que viene como string!)
            productos_por_id = {p["id_producto"]: p for p in todos_los_productos}

            for id_str, cantidad in carrito.items():
                producto = productos_por_id.get(int(id_str))
                if producto:
                    precio = int(producto["precio_producto"])  # 👈 asegúrate que sea int
                    subtotal = precio * cantidad
                    total_general += subtotal
                    productos_en_carrito.append({
                        "id": id_str,
                        "nombre": producto["nombre_producto"],
                        "imagen": producto["imagenes"],
                        "precio": precio,
                        "cantidad": cantidad,
                        "subtotal": subtotal,
                    })
            # ✅ Guardar productos del carrito y total en la sesión
            request.session["carrito_productos"] = productos_en_carrito
            request.session["carrito_total"] = total_general
    except Exception as e:
        print("ERROR en carrito:", e)
        messages.error(request, "Error al cargar productos desde la API.")

    context = {
        "carrito_productos": productos_en_carrito,
        "total": total_general,
    }
    return render(request, "core/cart.html", context)

def actualizar_carrito(request):
    if request.method == 'POST':
        id_producto = request.POST.get("id_producto")
        accion = request.POST.get("accion")
        carrito = request.session.get("carrito", {})

        if id_producto in carrito:
            if accion == "sumar":
                carrito[id_producto] += 1
            elif accion == "restar":
                carrito[id_producto] -= 1
                # Si la cantidad llega a 0, eliminar el producto del carrito
                if carrito[id_producto] <= 0:
                    carrito.pop(id_producto)
            elif accion == "eliminar":
                carrito.pop(id_producto)

        request.session["carrito"] = carrito

    return redirect("cart")


#VISTAS VENDEDOR
@solo_vendedor
def home_vendedor(request):
    return render(request, "core/vendedor/home_vendedor.html")

#VISTAS Bodeguero
@solo_bodeguero
def home_bodeguero(request):
    return render(request, "core/bodeguero/home_bodeguero.html")

#VISTAS Contador
@solo_contador
def home_contador(request):
    return render(request, "core/contador/home_contador.html")


#PROCESAR PAGO
def pago(request):
    try:
        # Llamada a la API del dólar
        response = requests.get('https://mindicador.cl/api/dolar')
        if response.status_code == 200:
            datos_dolar = response.json()
            valor_dolar = datos_dolar['serie'][0]['valor']  # Extraer valor actual del dólar
        else:
            valor_dolar = 0  # En caso de error, dejarlo en 0 para evitar división por cero
            messages.warning(request, "No se pudo obtener el valor del dólar.")
    except Exception as e:
        print("Error al conectar con la API mi indicador:", e)
        valor_dolar = 0

    # Obtener datos desde la sesión
    productos_en_carrito = request.session.get("carrito_productos", [])
    total_general = request.session.get("carrito_total", 0)

    total_dolar = 0
    if valor_dolar > 0:
        total_dolar = round(total_general / valor_dolar, 2)

    context = {
        "carrito_productos": productos_en_carrito,
        "total": total_general,
        "total_dolar": total_dolar,
    }
    return render(request, "core/checkout.html", context)
import os
import requests
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .decorators import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


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
    response = requests.get('http://localhost:8001/producto_pedido')
    producto_pedido = response.json()
    producto_pedidos = [u for u in producto_pedido if u.get("descripcion") != "Por pagar"]

    paginator = Paginator(producto_pedido, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista' : producto_pedidos,
        'page_obj' : page_obj
    }
    return render(request, "core/vendedor/home_vendedor.html",aux)

def update_pedido(request, id_pedido):
    try:
        get_response = requests.get(f"http://localhost:8001/producto_pedido/{id_pedido}")
        if get_response.status_code != 200:
            messages.error(request, "Pedido no encontrado.")
            return redirect("home_vendedor")

        pedido = get_response.json()

        # Extraer producto (el primero de la lista)
        producto = pedido["productos"][0] if pedido.get("productos") else {}

        # Mezclar los datos para el template
        datos_pedido = {
            "id_pedido": pedido["id_pedido"],
            "nombre_producto": producto.get("nombre_producto", ""),
            "marca_descripcion": producto.get("marca_descripcion", ""),
            "precio_producto": producto.get("precio_producto", ""),
            "tipo_producto": producto.get("tipo_producto", ""),
            "cantidad_producto": producto.get("cantidad_producto", ""),
            "nombre_user": pedido.get("nombre_user", ""),
            "apellido": pedido.get("apellido", ""),
            "estado_pedido": pedido.get("estado_pedido", ""),
        }

    except requests.exceptions.RequestException:
        messages.error(request, "Error al conectar con el servidor.")
        return redirect("home_vendedor")

    if request.method == 'POST':
        data = {}
        id_estado_pedido = request.POST.get("id_estado_pedido")
        if id_estado_pedido:
            data["id_estado_pedido"] = int(id_estado_pedido)

        data["nombre_producto"] = request.POST.get("nombre_producto")
        data["marca_descripcion"] = request.POST.get("marca_descripcion")
        data["precio_producto"] = request.POST.get("precio_producto")
        data["tipo_producto"] = request.POST.get("tipo_producto")
        data["cantidad_producto"] = request.POST.get("cantidad_producto")
        data["nombre_user"] = request.POST.get("nombre_user")
        data["apellido"] = request.POST.get("apellido")

        try:
            response = requests.patch(
                f"http://localhost:8001/producto_pedido/{id_pedido}",
                json=data
            )
            if response.status_code == 200:
                messages.success(request, "Pedido actualizado correctamente.")
                requests.patch(f"http://localhost:8001/pedidos/{id_pedido}", json={"id_estado_pedido": id_estado_pedido})
                return redirect("home_vendedor")
            else:
                messages.error(request, f"Error al actualizar: {response.json().get('detail', 'Error desconocido')}")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor.")

    return render(request, "core/vendedor/update_pedido.html", {"pedido": datos_pedido})

#VISTAS Bodeguero
@solo_bodeguero
def home_bodeguero(request):
    return render(request, "core/bodeguero/home_bodeguero.html")

#VISTAS Contador
@solo_contador
def home_contador(request):
    response = requests.get('http://localhost:8001/pago')
    pago = response.json()
    pagos = [u for u in pago if u.get("medio_pago") != "Paypal"]

    paginator = Paginator(pago, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista' : pagos,
        'page_obj' : page_obj
    }
    return render(request, "core/contador/home_contador.html", aux)

def update_pago(request, id_pago):
    try:
        # Obtener el pago actual desde la API
        get_response = requests.get(f"http://localhost:8001/pago/{id_pago}")
        if get_response.status_code != 200:
            messages.error(request, "Pago no encontrado.")
            return redirect("home_contador")

        pago = get_response.json()
    except requests.exceptions.RequestException:
        messages.error(request, "Error al conectar con el servidor.")
        return redirect("home_contador")

    if request.method == 'POST':
        # Construir el diccionario de datos solo con campos presentes
        data = {}

        monto_pagar = request.POST.get("monto_pagar")
        if monto_pagar:
            data["monto_pagar"] = int(monto_pagar)

        id_estado_pago = request.POST.get("id_estado_pago")
        if id_estado_pago:
            data["id_estado_pago"] = int(id_estado_pago)

        # Siempre enviar campos que no provienen del formulario pero son requeridos por lógica
        data["url_comprobante"] = pago.get("url_comprobante")
        data["id_pedido"] = pago.get("id_pedido")
        data["id_medio_pago"] = 2  # Puedes hacer esto dinámico si es necesario

        try:
            response = requests.patch(
                f"http://localhost:8001/pago/{id_pago}",
                json=data
            )
            if response.status_code == 200:
                messages.success(request, "Pago actualizado correctamente.")
                id_pedido = pago["id_pedido"]
                requests.patch(f"http://localhost:8001/pedidos/{id_pedido}", json={"id_estado_pedido": 2})
                return redirect("home_contador")
            else:
                messages.error(request, f"Error al actualizar el pago: {response.json().get('detail', 'Error desconocido')}")
        except requests.exceptions.RequestException:
            messages.error(request, "No se pudo conectar con el servidor.")

    return render(request, "core/contador/update_pago.html", {"pago": pago})


#PROCESAR PAGO

def pago(request):
    if request.method == "GET":
        # Aquí cargas el checkout como antes
        try:
            response = requests.get('https://mindicador.cl/api/dolar')
            if response.status_code == 200:
                datos_dolar = response.json()
                valor_dolar = datos_dolar['serie'][0]['valor']
            else:
                valor_dolar = 0
                messages.warning(request, "No se pudo obtener el valor del dólar.")
        except Exception as e:
            print("Error al conectar con la API mi indicador:", e)
            valor_dolar = 0

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

    elif request.method == "POST":
        try:
            usuario = request.session.get('usuario')
            data = json.loads(request.body)

            # Obtener datos del carrito y usuario
            productos_en_carrito = request.session.get("carrito_productos", [])
            total_general = request.session.get("carrito_total", 0)
            if not usuario or "rut" not in usuario:
                return JsonResponse({"status": "error", "message": "Usuario no válido en sesión"}, status=400)

            rut_user = usuario["rut"]

            # Crear JSON para enviar a la API externa
            pedidoData = {
                "fecha_pedido": timezone.now().date().isoformat(),
                "cantidad_pedido": sum(item['cantidad'] for item in productos_en_carrito),
                "subtotal_pedido": total_general,
                "rut_user": rut_user,
                "url_imagen_comprobante":"",
                "id_estado_pedido": 2,  # Pagado
                "id_productos": [
                    {
                        "id_producto": item['id'],
                        "cantidad_producto": item['cantidad']
                    } for item in productos_en_carrito
                ],
                "pago": {
                    "fecha_pago": timezone.now().date().isoformat(),
                    "monto_pagar": total_general,
                    "id_medio_pago": 1,  # PayPal
                    "id_estado_pago": 1  # aprobado
                }
            }

            # URL de tu API externa para crear pedido
            url_api_pedido = "http://localhost:8001/pedidos/"  # Cambia aquí a la URL real


            response = requests.post(url_api_pedido, json=pedidoData)

            if response.status_code == 201 or response.status_code == 200:
                # Pedido creado OK
                # Limpiar carrito en sesión
                request.session["carrito_productos"] = []
                request.session["carrito_total"] = 0
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error en API externa: {response.status_code} {response.text}"
                })

        except Exception as e:
            print("Error al procesar pago:", e)
            return JsonResponse({"status": "error", "message": str(e)})

    else:
        return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)
    
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

def pago_transferencia(request):
    if request.method == 'POST':
        try:
            usuario = request.session.get('usuario')

            # Obtener datos del carrito y usuario
            productos_en_carrito = request.session.get("carrito_productos", [])
            total_general = request.session.get("carrito_total", 0)
            if not usuario or "rut" not in usuario:
                return JsonResponse({"status": "error", "message": "Usuario no válido en sesión"}, status=400)

            rut_user = usuario["rut"]

            # Procesar imagen del comprobante
            imagen = request.FILES.get("comprobante")
            url_comprobante = None
            if imagen:
                nombre_archivo = f"{rut_user}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
                ruta_relativa = os.path.join("imagenes_comprobante", nombre_archivo)
                default_storage.save(ruta_relativa, ContentFile(imagen.read()))
                url_comprobante = ruta_relativa  # Esto es lo que se envía a la API

            data = {
                "fecha_pedido": timezone.now().date().isoformat(),
                "cantidad_pedido": sum(item['cantidad'] for item in productos_en_carrito),
                "subtotal_pedido": total_general,
                "rut_user": rut_user,
                "id_estado_pedido": 1,  # Por pagar
                "id_productos": [
                    {
                        "id_producto": item['id'],
                        "cantidad_producto": item['cantidad']
                    } for item in productos_en_carrito
                ],
                "pago": {
                    "fecha_pago": timezone.now().date().isoformat(),
                    "monto_pagar": total_general,
                    "url_comprobante": url_comprobante,
                    "id_medio_pago": 2,  # Transferencia
                    "id_estado_pago": 1  # Por aprobar
                }
            }

            # URL de tu API externa para crear pedido
            url_api_pedido = "http://localhost:8001/pedidos/"
            response = requests.post(url_api_pedido, json=data)

            if response.status_code in [200, 201]:
                request.session["carrito_productos"] = []
                request.session["carrito_total"] = 0
                return redirect("thankyou")
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error en API externa: {response.status_code} {response.text}"
                })

        except Exception as e:
            print("Error al procesar pago por transferencia:", e)
            return JsonResponse({"status": "error", "message": str(e)})

    return render(request, "core/checkout.html")


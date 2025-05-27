from django.shortcuts import redirect
from django.contrib import messages

def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not usuario or str(usuario.get("rol")) != "Admin":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("index")
        return view_func(request, *args, **kwargs)
    return wrapper

def solo_vendedor(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not usuario or str(usuario.get("rol")) != "Vendedor":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("index")
        return view_func(request, *args, **kwargs)
    return wrapper

def solo_bodeguero(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not usuario or str(usuario.get("rol")) != "Bodeguero":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("index")
        return view_func(request, *args, **kwargs)
    return wrapper

def solo_contador(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get("usuario")
        if not usuario or str(usuario.get("rol")) != "Contador":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("index")
        return view_func(request, *args, **kwargs)
    return wrapper
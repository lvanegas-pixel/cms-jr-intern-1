# Genesal Jr. — repo base

Tu punto de partida para el reto de la semana. Lee `02_ENUNCIADO_SANDBOX.md`
(te lo pasa tu mentor) para saber **qué** construir. Esto explica **cómo arrancar**.

## 1. Entorno (día 1)

```bash
# 1. Crea y activa el entorno virtual
python -m venv venv
source venv/bin/activate        # macOS/Linux
# .\venv\Scripts\activate       # Windows

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Copia el archivo de entorno (el .env real NUNCA se commitea)
cp .env.example .env

# 4. Crea el proyecto Django (si aún no existe)
django-admin startproject config .

# 5. Primeras migraciones + superusuario (para el admin)
python manage.py migrate
python manage.py createsuperuser

# 6. Arranca
python manage.py runserver
```

Abre http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/ — si ves ambas, +10 pts 🎉

## 2. Checklist antes de tu primer commit

- [ ] `git status` NO muestra `.env` ni `venv/` (el `.gitignore` ya los protege).
- [ ] Trabajas en una **rama**, no en `main` (créala desde GitLab, no desde PyCharm).
- [ ] El código está en **inglés**.

## 3. Correr los tests

```bash
pytest
```

## 4. Convención de ramas

```
feature/<numero-issue>-descripcion-corta
# ej: feature/3-project-serializer-validation
```

## 5. Estructura que acabarás teniendo (orientativa)

```
config/              # settings, urls raíz
catalogue/           # tu app principal
├── models.py        # Project, Asset
├── serializers.py   # validación de negocio (Regla 1)
├── permissions.py   # scoping + anti-trampa (Reglas 2 y 3)
├── views.py         # ViewSets DELGADOS
├── urls.py          # router
└── tests/           # pytest
```

> Fíjate: `permissions.py` y `serializers.py` son archivos **separados**. Así está
> montado el Aurora real. Mantén cada cosa en su sitio.


### RETO 2 - Evolucionar el CMS Jr.: separar Backend y Frontend

## FASE 1 — Definir bien la API

# 1.1. Autenticación — ¿quién entra?

- Añadir la app de tokens en settings.py
Abre tu archivo config/settings.py y busca la lista INSTALLED_APPS
- Tenemos que tener en INSTALLED_APPS: `rest_framework.authtoken` ---> esta app tiene sus propios modelos internos : 
  un modelo llamado `Token` para guardar qué token le pertenece a qué usuario)

(Cuando tú pones 'rest_framework.authtoken' en INSTALLED_APPS, le estás diciendo a Django: "Oye, esta app existe y 
va a formar parte de mi proyecto".)

- Configurar DRF globalmente en settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # Usaremos tokens
        'rest_framework.authentication.SessionAuthentication', # Dejamos la sesión para el admin de Django
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Por defecto, nadie entra si no está autenticado
    ],
}


- Aplicar las migraciones
Como se ha añadido una app nueva que guarda los tokens en la base de datos, ejecuta en tu terminal:
    python manage.py migrate

//Al ejecutar python manage.py migrate, Django revisa todas las apps de esa lista (las tuyas y las de librerías 
externas) y dice: "Vaya, veo que la app de tokens necesita una tabla llamada authtoken_token en la base de datos
para guardar los códigos de acceso. Voy a crearla".

- Crear la "puerta" de login para los tokens (config/urls.py):
Abre tu archivo config/urls.py para que los usuarios puedan enviar su usuario/contraseña y recibir su token:

from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token  # <-- Importamos la vista de tokens

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),
    path('api-token-auth/', obtain_auth_token),  # <-- Ruta para hacer login y obtener el token
]

# 1.2. Activar la Paginación
Eso es para obtener un mejor servicio al entregar datos que se piden. 
Si tenemos una BD muy grande (ej. 5.00 proyectos) y un cliente hace GET `/api/projects/`, el servidor intentará mandar todos
los proyectos y eso tardará y el cliente se congelará.
    La paginación corta esos datos en paginas y te devuelve metadatos útiles, como cuántos hay en total, enlace pagina 
    siguiente... y eso hará que el sistema funcione de forma más eficiente.

Añadimos esto en config/settings.py
    # 2. Paginación global de la API
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Máximo 10 elementos por página

# Paso 1.3: Añadir Filtros y Búsqueda

Un comercial no quiere ver una lista infinita de proyectos de toda la empresa; quiere filtrar por su usuario (owner)
o buscar un proyecto por su nombre exacto. Para no tener que programar esto a mano en Python, usamos librerías especializadas.

- Instala la librería de filtros en tu terminal (con el entorno virtual activo):
    `pip install django-filter`
- Añade la app a tu settings.py:
En INSTALLED_APPS, añade 'django_filters':
    `django_filters`
- Configura los ViewSets (catalog/views.py):
Entra en tu archivo de vistas y dile a tus ViewSets qué campos se pueden filtrar y buscar:
1. Hemos importado DjangoFilterBackend y filters de REST Framework. 
`from rest_framework import viewsets, filters`

2. Hemos añadido filter_backends, filterset_fields y search_fields en ambas clases (ProjectViewSet y AssetViewSet).

## FASE 2 — Probar toda la API con Postman

# Paso 2.1: Crear la Colección en Postman y la variable global
Una colección en Postman es simplemente una carpeta donde guardas todas las peticiones de tu proyecto ordenadas.

- Abre la aplicación Postman en tu ordenador.
- En la barra lateral izquierda, haz clic en el botón New (o en el icono +) y selecciona Collection.
- Ponle de nombre: CMS Jr.
- Vamos a crear una variable de entorno para no tener que escribir [http://127.0.0.1:8000](http://127.0.0.1:8000) en cada petición:
  - Clica sobre tu colección CMS Jr. en la barra lateral. 
  - Ve a la pestaña Variables (en la parte superior derecha de la ventana central). 
  - En la columna VARIABLE, escribe: base_url 
  - En la columna INITIAL VALUE y CURRENT VALUE, escribe: [http://127.0.0.1:8000](http://127.0.0.1:8000)
  - Pincha en Save (Guardar). 
  - ¿Para qué sirve esto? A partir de ahora, en cualquier petición podrás escribir {{base_url}}/api/projects/ 
    y Postman cambiará automáticamente {{base_url}} por tu servidor local.

# Paso 2.2.: Generar y configurar tu Token de Autenticación
Como la API exige estar autenticado (`IsAuthenticated`), necesitamos pasar el token del usuario en las peticiones
mediante cabeceras HTTP.

- 
**Generar un token por terminal:**
Tenemos que crear un usuario en el Postman.
Ejecuta el siguiente comando en el entorno virtual para crear un token asociado a un usuario (por ejemplo, a un comercial o administrador):
    `python manage.py drf_create_token <nombre_usuario>`

1. Abre tu terminal (con el entorno virtual activo y el servidor de Django corriendo en otra pestaña).
2. Ejecuta este comando para crear un token a un usuario que ya tengas creado (por ejemplo, tu superusuario o un comercial):
   - Hemos tenido que crear un usuario comercial `comercial1`
     `python manage.py drf_create_token tu_usuario`
3. La terminal te devolverá una cadena larga de letras y números (ejemplo: 99b4d5...). Cópiala. 
     `(c133cccc7e3e1578ec3ed0cedc88dc17381fa59f)`
4. En Postman, vete a tu colección CMS Jr., haz clic en la pestaña Authorization.
5. En el desplegable Type, selecciona Bearer Token (o Token si te aparece).
6. En el campo Token, pega la cadena larga que copiaste de la terminal y guarda (Save). Esto hará que todas las 
   peticiones dentro de esta colección se autentiquen solas.

# Paso 2.3: Crear las peticiones del Camino Feliz (CRUD)
Vamos a crear dentro de tu colección las peticiones básicas para projects y assets.

- A. Para Projects:

1. Clica en los tres puntitos (...) al lado de tu colección CMS Jr. y selecciona Add request. Llámala List Projects.
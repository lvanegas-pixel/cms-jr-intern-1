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
- Ponle de nombre: `CMS Jr.`
- Vamos a crear una variable de entorno para no tener que escribir `http://127.0.0.1:8000` en cada petición:
  - Clica sobre tu colección `CMS Jr.` en la barra lateral.
  - Ve a la pestaña **Variables** (en la parte superior derecha de la ventana central).
  - En la columna VARIABLE, escribe: `base_url`
  - En la columna INITIAL VALUE y CURRENT VALUE, escribe: `http://127.0.0.1:8000`
  - Pincha en **Save** (Guardar).
  - *¿Para qué sirve esto?* A partir de ahora, en cualquier petición podrás escribir `{{base_url}}/api/projects/` y 
      Postman cambiará automáticamente `{{base_url}}` por tu servidor local.

# Paso 2.2: Generar y configurar tu Token de Autenticación (Guía Paso a Paso)

Como la API exige estar autenticado (`IsAuthenticated`), necesitamos pasar el token del usuario en las peticiones 
mediante cabeceras HTTP. Sigue estos pasos exactos para configurarlo:

1. **Generar un token por terminal:**
   - Abre tu terminal con el entorno virtual activo (`venv`) y el servidor de Django corriendo.
   - Ejecuta el siguiente comando para asociar y generar un token a un usuario (por ejemplo, el superusuario `admin`):

     python manage.py drf_create_token admin

   - La terminal te devolverá una cadena larga de letras y números (ejemplo: `543b9e1319d058f75d66346628aaa0600dd7a7a0`). Cópiala.

2. **Crear la petición en Postman:**
   - Crea una nueva petición (`New Request`) en tu colección, pon el método en **`GET`** y la URL: `{{base_url}}/api/projects/`.

3. **Configurar la pestaña "Authorization" en "No Auth" (¡Importante!):**
   - **¿Por qué elegimos "No Auth"?** Por defecto, si seleccionas opciones automáticas como *Basic Auth* o *Bearer Token*, 
       Postman añade cabeceras automáticas o prefijos incorrectos (como la palabra `Bearer`). El sistema de autenticación 
       nativo de Django (`TokenAuthentication`) es estricto y **exige obligatoriamente el prefijo `Token`**. 
   - Al configurar la pestaña en **`No Auth`**, evitamos que Postman modifique o inyecte credenciales erróneas, dándonos 
   el control total para mandar la cabecera de forma manual y exacta.

4. **Añadir la cabecera (Header) de forma manual:**
   - Ve a la pestaña **Headers** de tu petición (al lado de *Params* y *Authorization*).
   - Añade una nueva fila con estos datos exactos:
     - **KEY:** `Authorization`
     - **VALUE:** `Token 543b9e1319d058f75d66346628aaa0600dd7a7a0` *(Escribe la palabra **Token**, un espacio obligatorio, 
         y pega tu clave larga generada en la terminal)*.
   - Haz clic en **Send**. El servidor validará la credencial al instante y te devolverá un **`200 OK`**.

# Paso 2.3: Crear las peticiones del Camino Feliz (CRUD)
Vamos a crear dentro de tu colección las peticiones básicas para projects y assets.

**A. Para `Projects`:**
1. Clica en los tres puntitos (`...`) al lado de tu colección **CMS Jr.** y selecciona **Add request**. Llámala `List Projects`.
   - **Método:** `GET`
   - **URL:** `{{base_url}}/api/projects/`
   - **Cabeceras (*Headers*):** `Authorization: Token <tu_token>`
   - *Resultado esperado:* Devuelve la lista paginada de proyectos (`count`, `next`, `previous`, `results`).

2. Crea otra petición llamada `Create Project`:
   - **Método:** `POST`
   - **URL:** `{{base_url}}/api/projects/`
   - **Body:** Selecciona `raw` -> `JSON` y envía los datos del nuevo proyecto:
     ```json
     {
         "name": "Proyecto de Prueba"
     }
     ```
   - *Resultado esperado:* Código `201 Created` con el JSON del proyecto creado (el campo `owner` se asigna automáticamente al usuario autenticado).

3. Añade las peticiones restantes del ciclo CRUD de proyectos:
   - `Get Project Detail` (`GET` a `{{base_url}}/api/projects/{id}/`)
   - `Update Project` (`PATCH` a `{{base_url}}/api/projects/{id}/` enviando el nuevo nombre)
   - `Delete Project` (`DELETE` a `{{base_url}}/api/projects/{id}/`)

**B. Para `Assets`:**
Crea peticiones equivalentes para la ruta de assets (`{{base_url}}/api/assets/`) para cubrir su ciclo completo:
1. `List Assets` (`GET`)
2. `Create Asset` (`POST` enviando `project`, `name`, `asset_type` como `MODEL_3D`, `IMAGE` o `VIDEO`, e `is_public`).
3. `Get Asset Detail`, `Update Asset` y `Delete Asset`.

---

# Paso 2.4: Probar los "Caminos Infelices" (Control de Errores y Seguridad)

Un desarrollo profesional no solo comprueba que el sistema funciona cuando todo va bien, sino que valida que **falla 
exactamente como marcan las reglas de negocio y seguridad**. Añadimos las siguientes peticiones de control de errores a la colección:

1. **Prueba de la Regla 1 (Error 400 - Validación de Negocio):**
   - **Nombre:** `Fail - Duplicate MODEL_3D`
   - **Método / URL:** `POST` a `{{base_url}}/api/assets/`
   - **Acción:** Intentar crear un segundo asset de tipo `MODEL_3D` en un proyecto que ya contiene uno.
   - *Resultado esperado:* La API interrumpe la petición desde el Serializer y devuelve un código **`400 Bad Request`** 
      informando de que el proyecto ya dispone de un modelo 3D.

2. **Prueba de la Regla 3 (Error 403 - Anti-Cheat / Permisos):**
   - **Nombre:** `Fail - Unauthorized Asset Creation`
   - **Método / URL:** `POST` a `{{base_url}}/api/assets/`
   - **Acción:** Autenticarse con el token de un usuario comercial (`comercial1`) e intentar crear o modificar un asset 
       en un proyecto propiedad de otro usuario.
   - *Resultado esperado:* La clase de permisos `IsProjectOwnerOrAdmin` intercepta la acción y bloquea el acceso 
      devolviendo un código **`403 Forbidden`** (o `404 Not Found` según la consulta del queryset).

3. **Prueba sin Autenticación (Error 401 - Seguridad Global):**
   - **Nombre:** `Fail - No Token`
   - **Método / URL:** `GET` a `{{base_url}}/api/projects/`
   - **Acción:** Eliminar o no proporcionar la cabecera `Authorization` en la petición.
   - *Resultado esperado:* El sistema rechaza la conexión por defecto devolviendo un código **`401 Unauthorized`** 
      (*"Authentication credentials were not provided"*).

---

# Paso 2.5: Exportar la Colección y Guardarla en el Repositorio

Una vez validados todos los endpoints (tanto los caminos felices como los infelices):
1. Haz clic en los tres puntitos (`...`) al lado del nombre de la colección **CMS Jr.** en Postman.
2. Selecciona **Export** (formato recomendado Collection v2.1).
3. Guarda el archivo `.json` resultante.
4. En la raíz de tu repositorio local (`cms-jr-intern-1`), crea una carpeta llamada exactamente **`postman`**.
5. Mueve el archivo `.json` dentro de dicha carpeta para que quede versionado junto al código fuente.

=====================================  PROBLEMAS CON EL PR  =====================================================

Mensaje de Luis:
La autenticación con token está bien montada (endpoint para obtenerlo incluido), la paginación correcta y los filtros 
bien pensados en los dos ViewSets. Y la descripción del PR es clara. 

Antes de aprobarlo, quiero que revises una cosa del requirements.txt. Compará tu versión con la de main y fíjate:

Tu Django pasó de 5.1.4 a 6.1.2 (y DRF de 3.15.2 a 3.18.3). ¿Fue a propósito? ¿Sabías que habías actualizado Django 
a una versión mayor? Piensa qué implica cambiar la versión del framework sin quererlo en un proyecto de equipo.

Aparecieron dependencias nuevas que tú no instalaste directamente: asgiref, sqlparse, iniconfig, pluggy, packaging. 
¿Sabes qué son y por qué están ahí? ¿Cuál de todas las nuevas es la que de verdad necesitabas para esta fase?

Relee el comentario que venía en el requirements.txt original (el que borraste). Decía algo sobre pip freeze. 
¿Qué crees que pasó aquí?

Cuando tengas claro el porqué, deja el requirements.txt solo con lo que el proyecto necesita de verdad y actualiza 
el PR. Esto no es un capricho: un requirements limpio es lo que hace que el entorno de otra persona (o el servidor) sea 
reproducible.

---

### 💡 Resolución y Feedback del PR (requirements.txt)

**¿Qué pasó?**
Cometí el error de ejecutar un `pip freeze > requirements.txt`. No pensé en que eso podría ocasionar conflictos con el
equipo. no había leido la advertencia que habían en el requirements.txt sobre exactamente no usar ese comando. Ocasionó:
1. **Actualización involuntaria:** Django saltó de la versión base `5.1.4` a la `6.1.2`, y DRF se actualizó a la `3.18.3`.
2. **Inyección de subdependencias:** Se colaron paquetes internos del ecosistema y de testing que no instalamos 
     directamente (`asgiref`, `sqlparse`, `iniconfig`, `pluggy`, `packaging`).

**¿Cómo se ha solucionado?**
He revertido el archivo a su estado original para mantener la versión de Django `5.1.4` intacta y reproducible para 
todo el equipo, añadiendo de forma limpia y manual únicamente la dependencia que necesitábamos para esta fase:

- `django-filter>=23.0`
Esta dependencia nos permite integrar de forma nativa la filtración avanzada de consultas en nuestros ViewSets de 
Django REST Framework. Gracias a ella, los clientes pueden filtrar los listados de la API por campos específicos 
(como el `owner` de un proyecto o el `asset_type` de un archivo) y realizar búsquedas personalizadas mediante 
parámetros en la URL sin necesidad de escribir lógica de filtrado manual en Python.


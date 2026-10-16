// 1. Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const MY_TOKEN = 'c133cccc7e3e1578ec3ed0cedc88dc17381fa59f'; // <-- TU TOKEN

const projectsList = document.getElementById('projects-list');
const form = document.getElementById('create-project-form');
const errorBox = document.getElementById('error-box');

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
}

function hideError() {
    errorBox.classList.add('hidden');
    errorBox.textContent = '';
}

// --- 1. CARGAR PROYECTOS (GET) ---
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            headers: { 'Authorization': `Token ${MY_TOKEN}` }
        });

        const data = await response.json();
        projectsList.innerHTML = '';

        data.results.forEach(project => {
            const li = document.createElement('li');

            // Inyectamos el texto del proyecto
            const textSpan = document.createElement('span');
            textSpan.innerHTML = `<strong>${project.name}</strong> <br> <small>ID: ${project.id} | Propietario: ${project.owner}</small>`;
            li.appendChild(textSpan);

            // EXTRA: Creamos el botón de borrar
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '🗑️ Borrar';
            deleteBtn.className = 'btn-delete';

            // Evento para borrar (DELETE)
            deleteBtn.addEventListener('click', async (event) => {
                // IMPORTANTÍSIMO: Esto evita que el clic en el botón active también la carga de assets
                event.stopPropagation();
                await deleteProject(project.id);
            });

            li.appendChild(deleteBtn);

            // Evento para cargar assets al pinchar el LI
            li.addEventListener('click', () => loadAssets(project.id, li));

            projectsList.appendChild(li);
        });
    } catch (error) {
        showError("Error de red al cargar proyectos.");
    }
}

// --- NUEVA FUNCIÓN: BORRAR PROYECTO (DELETE) ---
async function deleteProject(projectId) {
    // Pedimos confirmación para no borrar sin querer
    if (!confirm("¿Estás seguro de que quieres eliminar este proyecto?")) return;

    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Token ${MY_TOKEN}`
            }
        });

        if (response.ok) {
            // Si el backend devuelve un 204 No Content, recargamos la lista
            loadProjects();
        } else if (response.status === 403) {
            showError("Error 403: No tienes permiso para borrar este proyecto (no eres el dueño ni admin).");
        } else {
            showError("Error al intentar borrar el proyecto.");
        }
    } catch (error) {
        showError("Error de red al intentar borrar.");
    }
}

// --- 2. CREAR PROYECTO (POST) ---
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideError();

    const projectName = document.getElementById('project-name').value;

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${MY_TOKEN}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: projectName })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 403) showError("Error 403: Sin permiso.");
            else if (response.status === 400) showError(`Error 400: ${JSON.stringify(data)}`);
            else showError(`Error ${response.status}`);
            return;
        }

        document.getElementById('project-name').value = '';
        loadProjects();

    } catch (error) {
        showError("Error crítico al crear.");
    }
});

// --- 3. CARGAR ASSETS (GET con filtro) ---
async function loadAssets(projectId, liElement) {
    if (liElement.querySelector('.assets-box')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/assets/?project=${projectId}`, {
            headers: { 'Authorization': `Token ${MY_TOKEN}` }
        });

        const data = await response.json();

        const assetsDiv = document.createElement('div');
        assetsDiv.className = 'assets-box';
        assetsDiv.style.marginTop = '10px';
        assetsDiv.style.paddingLeft = '15px';
        assetsDiv.style.borderLeft = '3px solid var(--primary)';
        assetsDiv.style.fontSize = '0.9em';

        if (data.results.length === 0) {
            assetsDiv.innerHTML = '<span style="color: var(--text-muted);">No hay assets en este proyecto.</span>';
        } else {
            data.results.forEach(asset => {
                assetsDiv.innerHTML += `<div>📦 ${asset.name} (${asset.asset_type})</div>`;
            });
        }

        liElement.appendChild(assetsDiv);

    } catch (error) {
        showError("Error al cargar los assets.");
    }
}

// Inicializamos la vista
loadProjects();
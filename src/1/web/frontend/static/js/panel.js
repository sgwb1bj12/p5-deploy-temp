const API = "/api/tareas";

const form = document.getElementById("form-tarea");
const inputTitulo = document.getElementById("titulo");
const feedback = document.getElementById("feedback");
const lista = document.getElementById("lista-tareas");

function mostrarFeedback(texto, tipo) {
    feedback.textContent = texto;
    feedback.className = "feedback " + (tipo || "");
    if (texto) {
        setTimeout(() => {
            feedback.textContent = "";
            feedback.className = "feedback";
        }, 3500);
    }
}

function renderTareas(tareas) {
    lista.innerHTML = "";
    if (tareas.length === 0) {
        const vacio = document.createElement("p");
        vacio.className = "empty";
        vacio.textContent = "No hay tareas visibles.";
        lista.appendChild(vacio);
        return;
    }
    tareas.forEach((tarea) => {
        const div = document.createElement("article");
        div.className = "tarea";

        const h3 = document.createElement("h3");
        h3.textContent = tarea.title;

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `Propietario: ${tarea.owner} | Creada: ${tarea.created_at}`;

        const estado = document.createElement("div");
        estado.className = "estado";
        estado.textContent = `Estado: ${tarea.status}`;

        const acciones = document.createElement("div");
        acciones.className = "acciones";

        const btnToggle = document.createElement("button");
        btnToggle.className = "btn btn-primary";
        btnToggle.textContent = tarea.completed ? "Marcar pendiente" : "Marcar completada";
        btnToggle.addEventListener("click", () => alternarEstado(tarea.id, !tarea.completed));

        const btnEliminar = document.createElement("button");
        btnEliminar.className = "btn btn-danger";
        btnEliminar.textContent = "Eliminar";
        btnEliminar.addEventListener("click", () => eliminarTarea(tarea.id));

        acciones.appendChild(btnToggle);
        acciones.appendChild(btnEliminar);

        div.appendChild(h3);
        div.appendChild(meta);
        div.appendChild(estado);
        div.appendChild(acciones);
        lista.appendChild(div);
    });
}

async function cargarTareas() {
    try {
        const respuesta = await fetch(API);
        if (!respuesta.ok) throw new Error("Error al cargar tareas");
        const datos = await respuesta.json();
        renderTareas(datos);
    } catch (error) {
        mostrarFeedback(error.message, "error");
    }
}

async function crearTarea(event) {
    event.preventDefault();
    const title = inputTitulo.value.trim();
    if (!title) {
        mostrarFeedback("El título es obligatorio.", "error");
        return;
    }
    try {
        const respuesta = await fetch(API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title }),
        });
        if (!respuesta.ok) {
            const err = await respuesta.json().catch(() => ({}));
            throw new Error(err.error || "No se pudo crear la tarea.");
        }
        inputTitulo.value = "";
        mostrarFeedback("Tarea creada correctamente.", "ok");
        await cargarTareas();
    } catch (error) {
        mostrarFeedback(error.message, "error");
    }
}

async function alternarEstado(id, nuevoEstado) {
    try {
        const respuesta = await fetch(`${API}/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed: nuevoEstado }),
        });
        if (!respuesta.ok) throw new Error("No se pudo actualizar la tarea.");
        await cargarTareas();
    } catch (error) {
        mostrarFeedback(error.message, "error");
    }
}

async function eliminarTarea(id) {
    if (!confirm("¿Eliminar esta tarea?")) return;
    try {
        const respuesta = await fetch(`${API}/${id}`, { method: "DELETE" });
        if (!respuesta.ok) throw new Error("No se pudo eliminar la tarea.");
        mostrarFeedback("Tarea eliminada correctamente.", "ok");
        await cargarTareas();
    } catch (error) {
        mostrarFeedback(error.message, "error");
    }
}

form.addEventListener("submit", crearTarea);

cargarTareas();

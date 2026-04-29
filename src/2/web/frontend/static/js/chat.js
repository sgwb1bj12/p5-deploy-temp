document.addEventListener("DOMContentLoaded", function () {
    var chatInput = document.getElementById("chat_input");
    var chatSend = document.getElementById("chat_send");
    var chatMessages = document.getElementById("chat_messages");

    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addMessage(text, type) {
        var div = document.createElement("div");
        div.className = "chat-msg " + type;
        div.textContent = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showLoading() {
        var div = document.createElement("div");
        div.className = "chat-msg bot loading";
        div.textContent = "...";
        div.id = "loading_msg";
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeLoading() {
        var el = document.getElementById("loading_msg");
        if (el) el.remove();
    }

    async function sendMessage() {
        var message = chatInput.value.trim();
        if (message === "") return;

        addMessage(message, "user");
        chatInput.value = "";
        showLoading();

        try {
            var chatResp = await fetch(window.SVAIA_CHAT_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + window.SVAIA_TOKEN
                },
                body: JSON.stringify({ message: message })
            });

            removeLoading();

            if (chatResp.status === 401) {
                addMessage("Error de autenticación: token ausente o inválido.", "bot");
                return;
            }
            if (!chatResp.ok) {
                addMessage("Error del microservicio de chat: " + chatResp.status, "bot");
                return;
            }

            var chatData = await chatResp.json();
            var respuesta = chatData.message;
            addMessage(respuesta, "bot");

            var saveResp = await fetch("/api/mensajes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ contenido: message, respuesta: respuesta })
            });

            if (!saveResp.ok) {
                console.warn("No se pudo persistir el mensaje", saveResp.status);
            }
        } catch (error) {
            removeLoading();
            addMessage("Error: " + error.message, "bot");
        }
    }

    if (chatSend) {
        chatSend.addEventListener("click", sendMessage);
    }
    if (chatInput) {
        chatInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") sendMessage();
        });
    }
});

from flask import Flask, request, jsonify, render_template_string
from database import buscar_productos, listar_productos
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_seguro")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")


def menu_principal():
    return (
        "👋 Bienvenido a la pinturería\n\n"
        "Elige una opción:\n"
        "1️⃣ Ver productos\n"
        "2️⃣ Buscar producto\n"
        "3️⃣ Ver ayuda\n"
        "4️⃣ Horarios de atención\n\n"
        "También puedes escribir directamente el nombre de un producto."
    )


def procesar_mensaje(mensaje: str) -> str:
    mensaje = (mensaje or "").strip().lower()

    if not mensaje:
        return "No se recibió ningún mensaje."

    saludos = [
        "hola",
        "buenos dias",
        "buen día",
        "buen dia",
        "buenas",
        "buenas tardes",
        "buenas noches",
    ]

    if any(saludo in mensaje for saludo in saludos) or mensaje in ["menu", "menú", "inicio"]:
        return menu_principal()

    if mensaje == "1":
        resultados = listar_productos(10)

        if not resultados:
            return "No hay productos cargados."

        lineas = ["📋 Lista de productos:\n"]
        for p in resultados:
            lineas.append(
                f"- {p['nombre']} | {p['categoria']} | Stock: {p['stock']} | ${p['precio']}"
            )

        lineas.append("\nEscribe 'menu' para volver al menú principal.")
        return "\n".join(lineas)

    if mensaje == "2":
        return (
            "🔎 Escribe el nombre o una palabra clave del producto que buscas.\n"
            "Ejemplos:\n"
            "- latex\n"
            "- rodillo\n"
            "- impermeabilizante"
        )

    if mensaje == "3":
        return (
            "ℹ️ Ayuda:\n"
            "- Escribe 1 para ver productos\n"
            "- Escribe 2 para buscar un producto\n"
            "- Escribe 4 para ver horarios\n"
            "- O escribe directamente el nombre del producto"
        )

    if mensaje == "4":
        return (
            "🕒 Horarios de atención:\n"
            "Lunes a Viernes: 08:00 a 18:00\n"
            "Sábados: 08:00 a 13:00\n"
            "Domingos: cerrado"
        )

    resultados = buscar_productos(mensaje)

    if not resultados:
        return f"No encontré productos para '{mensaje}'."

    if len(resultados) == 1:
        p = resultados[0]
        return (
            "📦 Stock del producto\n"
            f"Nombre: {p['nombre']}\n"
            f"Categoría: {p['categoria']}\n"
            f"Stock disponible: {p['stock']}\n"
            f"Precio: ${p['precio']}"
        )

    lineas = [f"🔎 Encontré {len(resultados)} productos:\n"]
    for p in resultados:
        lineas.append(
            f"- {p['nombre']} | {p['categoria']} | Stock: {p['stock']} | ${p['precio']}"
        )

    return "\n".join(lineas)


def enviar_mensaje_whatsapp(numero: str, texto: str):
    print("=== DEBUG ENV ===")
    print("VERIFY_TOKEN:", VERIFY_TOKEN)
    print("WHATSAPP_TOKEN cargado:", bool(WHATSAPP_TOKEN))
    print("PHONE_NUMBER_ID:", PHONE_NUMBER_ID)

    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("Faltan variables WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto},
    }

    print("=== ENVÍO A META ===")
    print("URL:", url)
    print("Payload:", payload)

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        print("=== RESPUESTA META ===")
        print("Status:", r.status_code)
        print("Body:", r.text)
    except Exception as e:
        print("Error enviando mensaje a Meta:", e)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "Bot de pinturería activo",
        "endpoints": [
            "/chat",
            "/productos",
            "/buscar?q=latex",
            "/webhook",
        ],
    })


@app.route("/chat", methods=["GET"])
def chat():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Chat Cliente</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .contenedor {
                width: 420px;
                margin: 30px auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            }
            .header {
                background: #1f6feb;
                color: white;
                padding: 15px;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
            }
            .chat-box {
                height: 420px;
                overflow-y: auto;
                padding: 15px;
                background: #fafafa;
            }
            .mensaje {
                margin: 10px 0;
                padding: 10px 12px;
                border-radius: 10px;
                max-width: 80%;
                white-space: pre-wrap;
            }
            .usuario {
                background: #d1e7ff;
                margin-left: auto;
                text-align: right;
            }
            .bot {
                background: #e8e8e8;
                margin-right: auto;
            }
            .input-area {
                display: flex;
                border-top: 1px solid #ddd;
            }
            .input-area input {
                flex: 1;
                padding: 12px;
                border: none;
                font-size: 16px;
                outline: none;
            }
            .input-area button {
                background: #1f6feb;
                color: white;
                border: none;
                padding: 0 20px;
                cursor: pointer;
                font-size: 16px;
            }
            .input-area button:hover {
                background: #1558b0;
            }
        </style>
    </head>
    <body>
        <div class="contenedor">
            <div class="header">💬 Chat Cliente</div>
            <div class="chat-box" id="chatBox">
                <div class="mensaje bot">Hola 👋 Escribe "hola" para ver el menú.</div>
            </div>
            <div class="input-area">
                <input type="text" id="mensajeInput" placeholder="Escribe tu mensaje..." />
                <button onclick="enviarMensaje()">Enviar</button>
            </div>
        </div>

        <script>
            async function enviarMensaje() {
                const input = document.getElementById("mensajeInput");
                const chatBox = document.getElementById("chatBox");
                const mensaje = input.value.trim();

                if (!mensaje) return;

                const divUsuario = document.createElement("div");
                divUsuario.className = "mensaje usuario";
                divUsuario.textContent = mensaje;
                chatBox.appendChild(divUsuario);

                input.value = "";

                const response = await fetch("/webhook", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ mensaje: mensaje })
                });

                const data = await response.json();

                const divBot = document.createElement("div");
                divBot.className = "mensaje bot";
                divBot.textContent = data.respuesta || "Sin respuesta del bot.";
                chatBox.appendChild(divBot);

                chatBox.scrollTop = chatBox.scrollHeight;
            }

            document.getElementById("mensajeInput").addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    enviarMensaje();
                }
            });
        </script>
    </body>
    </html>
    """)


@app.route("/productos", methods=["GET"])
def productos():
    resultados = listar_productos()
    return jsonify(resultados)


@app.route("/buscar", methods=["GET"])
def buscar():
    termino = request.args.get("q", "").strip()

    if not termino:
        return jsonify({
            "error": "Debes enviar un término de búsqueda. Ejemplo: /buscar?q=latex"
        }), 400

    resultados = buscar_productos(termino)

    if not resultados:
        return jsonify({
            "mensaje": f"No se encontraron productos para: {termino}"
        })

    return jsonify(resultados)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        print("=== VERIFY WEBHOOK ===")
        print("mode:", mode)
        print("token recibido:", token)
        print("challenge:", challenge)

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

        return "Token inválido", 403

    data = request.get_json(silent=True) or {}
    print("=== PAYLOAD RECIBIDO ===")
    print(data)

    if "mensaje" in data:
        respuesta = procesar_mensaje(data.get("mensaje", ""))
        return jsonify({"respuesta": respuesta}), 200

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        cambios = changes["value"]

        print("=== VALUE COMPLETO ===")
        print(cambios)

        if "messages" not in cambios:
            print("=== EVENTO SIN MENSAJE ===")
            print(cambios)
            return "EVENT_RECEIVED", 200

        mensaje_data = cambios["messages"][0]

        if mensaje_data.get("type") != "text":
            print("Mensaje no es de tipo text:", mensaje_data.get("type"))
            return "EVENT_RECEIVED", 200

        numero = mensaje_data["from"]
        mensaje = mensaje_data["text"]["body"]

        print("=== MENSAJE WHATSAPP ===")
        print("Número:", numero)
        print("Mensaje:", mensaje)

        respuesta = procesar_mensaje(mensaje)
        print("Respuesta generada:", respuesta)

        enviar_mensaje_whatsapp(numero, respuesta)

        return "EVENT_RECEIVED", 200

    except Exception as e:
        print("Error procesando webhook:", e)
        print("Payload recibido:", data)
        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
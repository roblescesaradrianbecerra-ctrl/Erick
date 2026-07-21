import os
import uuid
import enved
from flask import Flask, render_template_string, request
from PIL import Image, ImageDraw, ImageFont

# CONFIGURACIÓN BÁSICA
aplicacion = Flask(__name__)
DIRECTORIO_RENDERS = "renderiza"
os.makedirs(DIRECTORIO_RENDERS, exist_ok=True)

# --- FUNCIÓN PARA GENERAR LA IMAGEN (FUNCIONA SIEMPRE) ---
def generar_imagen(datos):
    # Crear lienzo
    img = Image.new("RGB", (800, 600), color="#1a1a2e")
    dibujo = ImageDraw.Draw(img)

    # Usar fuente que existe en todos los servidores
    try:
        fuente = ImageFont.truetype("DejaVuSans.ttf", 14)
        fuente_titulo = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except:
        fuente = ImageFont.load_default()
        fuente_titulo = ImageFont.load_default()

    # Escribir datos en la imagen
    dibujo.text((20, 20), "ERICK RENDERIZADO", fill="#ff4757", font=fuente_titulo)
    dibujo.text((20, 55), f"Cuartos: {datos.get('cuartos', '3')} | Baños: {datos.get('banos', '2')}", fill="#ffffff", font=fuente)
    dibujo.text((20, 80), f"Medidas: {datos.get('medidas', '20 metros x 20 metros')}", fill="#ffffff", font=fuente)
    dibujo.text((20, 105), f"Estilo: {datos.get('estilo', 'Moderno minimalista')} | Color: {datos.get('color', 'Azul')}", fill="#ffffff", font=fuente)
    
    # Marca de agua obligatoria para la muestra gratis
    dibujo.text((20, 570), "© MUESTRA CON MARCA DE AGUA", fill="#ff4757", font=fuente)

    # Convertir para mostrar en la página
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


# --- TU PÁGINA WEB COMPLETA ---
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ERICK RENDERIZADO</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #fff; padding: 20px; max-width: 720px; margin: 0 auto; }
h1 { color: #e94560; text-align: center; font-size: 2.6em; margin-bottom: 1.5em; }
h2 { color: #aaa; margin: 20px 0 10px; }
.container { max-width: 720px; margin: 40px auto; padding: 0 20px; }
.card { background: #1a1a2e; border-radius: 16px; padding: 30px; margin-bottom: 20px; }
.card h2 { color: #e94560; margin-bottom: 24px; font-weight: 1.3em; }
.etiqueta { display: block; margin-bottom: 0.85em; color: #aaa; }
input, select, textarea { width: 100%; padding: 11px 14px; margin-bottom: 16px; border: none; border-radius: 8px; background: #16213e; color: #fff; font-size: 1em; }
input:focus, select:focus, textarea:focus { outline: 2px solid #e94560; }
textarea { resize: vertical; min-height: 80px; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.btn-gen { margin-top: 28px; width: 100%; padding: 14px; font-size: 1.3em; font-weight: bold; background: linear-gradient(135deg, #ff4757, #e94560); border: none; border-radius: 8px; color: white; cursor: pointer; opacity: 0.9; transition: all 0.2s; }
.btn-gen:hover { opacity: 1; transform: translateY(-1px); }
#resultado { margin-top: 28px; display: none; }
#resultado img { width: 100%; border-radius: 8px; margin-bottom: 14px; border: 3px solid #ff4757; }
.accion-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.btn-pay { background: linear-gradient(135deg, #007bff, #0077b6); }
.btn-wa { background: linear-gradient(135deg, #25d366, #128c7e); }
.precio-note { color: #e94560; padding: 30px; text-align: center; font-size: 1.2em; }
.pie-de-pagina { text-align: center; color: #aaa; padding: 30px; }
</style>
</head>
<body>
<encabezado>
<h1>✨ GENERAR RENDER GRATIS</h1>
</encabezado>
<div class="container">
<div class="card">
<h2>📝 Solicita tu render gratis</h2>
<form id="form" method="POST">
<div class="row2">
<div>
<label class="etiqueta">Nombre completo</label>
<input name="nombre" required>
</div>
<div>
<label class="etiqueta">Teléfono / WhatsApp</label>
<input name="telefono" required>
</div>
</div>
<div class="row2">
<div>
<label class="etiqueta">Número de cuartos</label>
<select name="cuartos">
<option value="1">1</option>
<option value="2">2</option>
<option value="3" selected>3</option>
<option value="4">4</option>
<option value="5">5 o más</option>
</select>
</div>
<div>
<label class="etiqueta">Número de baños</label>
<select name="banos">
<option value="1">1</option>
<option value="2" selected>2</option>
<option value="3">3</option>
<option value="4">4 o más</option>
</select>
</div>
</div>
<div>
<label class="etiqueta">Medidas del terreno/espacio</label>
<input name="medidas" value="20 metros x 20 metros ventanales grandes mucha iluminación con balcón a la fachada | Niveles 2">
</div>
<div>
<label class="etiqueta">Estilo arquitectónico</label>
<select name="estilo">
<option value="Moderno minimalista" selected>Moderno minimalista</option>
<option value="Clásico">Clásico</option>
<option value="Rústico">Rústico</option>
<option value="Industrial">Industrial</option>
<option value="Campestre">Campestre</option>
</select>
</div>
<div>
<label class="etiqueta">Color o combinación preferida</label>
<input name="color" value="Azul">
</div>
<button type="submit" class="btn-gen">✨ GENERAR MUESTRA GRATIS</button>
</form>
</div>

<!-- AQUÍ APARECE LA IMAGEN GENERADA -->
<div id="resultado" {% if imagen_generada %} style="display:block;" {% endif %}>
<div class="card">
<h2>✅ TU MUESTRA LISTA</h2>
{% if imagen_generada %}
<img src="data:image/png;base64,{{ imagen_generada }}" alt="Render generado">
{% endif %}
<div class="accion-btns">
<button class="btn-pay btn-gen">💳 Pagar $200 MXN sin marca</button>
<button class="btn-wa btn-gen">💬 Enviar por WhatsApp</button>
</div>
<p class="precio-note"><strong>Nota:</strong> Gratis con marca de agua; pago obtienes alta calidad limpia.</p>
</div>
</div>

</div>
<div class="pie-de-pagina">© ERICK RENDERIZADO - Todos los derechos reservados</div>
</body>
</html>
"""

# --- RUTA PRINCIPAL ---
@aplicacion.route("/", methods=["GET", "POST"])
def inicio():
    imagen_generada = None
    if request.method == "POST":
        datos_form = {
            "cuartos": request.form.get("cuartos", "3"),
            "banos": request.form.get("banos", "2"),
            "medidas": request.form.get("medidas", "20 metros x 20 metros"),
            "estilo": request.form.get("estilo", "Moderno minimalista"),
            "color": request.form.get("color", "Azul")
        }
        imagen_generada = generar_imagen(datos_form)
    return render_template_string(HTML, imagen_generada=imagen_generada)

if __name__ == "__main__":
    aplicacion.run()

import os
import uuid
import threading
from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
RENDERS_DIR = "renders"
os.makedirs(RENDERS_DIR, exist_ok=True)
jobs = {}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ERICK RENDERIZADO</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #f0f0f0; }
  header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); text-align: center; padding: 40px 20px 30px; border-bottom: 3px solid #e94560; }
  header h1 { font-size: 2.6em; color: #fff; letter-spacing: 3px; }
  header h1 span { color: #e94560; }
  header p { color: #aaa; margin-top: 8px; font-size: 1.05em; }
  .container { max-width: 720px; margin: 40px auto; padding: 0 20px 60px; }
  .card { background: #1a1a1a; border-radius: 16px; padding: 36px; border: 1px solid #2a2a2a; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
  .card h2 { color: #e94560; margin-bottom: 24px; font-size: 1.3em; }
  label { display: block; font-size: 0.85em; color: #aaa; margin-bottom: 5px; margin-top: 16px; }
  input, select, textarea { width: 100%; padding: 11px 14px; border-radius: 8px; background: #111; border: 1px solid #333; color: #fff; font-size: 0.95em; }
  input:focus, select:focus, textarea:focus { outline: none; border-color: #e94560; }
  textarea { resize: vertical; min-height: 80px; }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .btn-gen { margin-top: 28px; width: 100%; padding: 15px; background: linear-gradient(135deg, #e94560, #c62a47); color: #fff; font-size: 1.1em; font-weight: 700; border: none; border-radius: 10px; cursor: pointer; }
  .btn-gen:hover { opacity: 0.9; transform: translateY(-1px); }
  #progress-area { display: none; margin-top: 28px; }
  .progress-bar-bg { background: #2a2a2a; border-radius: 99px; height: 10px; overflow: hidden; }
  .progress-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #e94560, #ff6b6b); border-radius: 99px; transition: width 0.4s ease; }
  #status-msg { text-align: center; margin-top: 12px; color: #aaa; font-size: 0.95em; }
  #result-area { display: none; margin-top: 28px; text-align: center; }
  #result-area img { width: 100%; border-radius: 12px; border: 2px solid #e94560; }
  .action-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 20px; }
  .btn-pay, .btn-wa { padding: 14px; border-radius: 10px; font-weight: 700; font-size: 1em; border: none; text-decoration: none; display: flex; align-items: center; justify-content: center; color: #fff; }
  .btn-pay { background: linear-gradient(135deg, #00b4d8, #0077b6); }
  .btn-wa { background: linear-gradient(135deg, #25d366, #128c7e); }
  .price-note { background: #1f1f1f; border: 1px solid #333; border-radius: 10px; padding: 14px 18px; margin-top: 24px; font-size: 0.9em; color: #bbb; line-height: 1.6; }
  .price-note strong { color: #e94560; }
  footer { text-align: center; padding: 30px; color: #444; font-size: 0.82em; }
</style>
</head>
<body>
<header>
  <h1>ERICK <span>RENDERIZADO</span></h1>
  <p>Renders arquitectónicos con Inteligencia Artificial · Entrega inmediata</p>
</header>
<div class="container">
  <div class="card">
    <h2>🏠 Solicita tu render gratis</h2>
    <form id="form">
      <div class="row2">
        <div><label>Nombre completo</label><input name="nombre" required placeholder="Ej. Juan Pérez"></div>
        <div><label>Teléfono / WhatsApp</label><input name="telefono" required placeholder="Ej. 4491234567"></div>
      </div>
      <div class="row2">
        <div><label>Número de cuartos</label>
          <select name="cuartos">
            <option>1</option><option>2</option><option selected>3</option><option>4</option><option>5+</option>
          </select>
        </div>
        <div><label>Número de baños</label>
          <select name="banos">
            <option>1</option><option selected>2</option><option>3</option><option>4+</option>
          </select>
        </div>
      </div>
      <div class="row2">
        <div><label>Medidas del terreno</label><input name="medidas" placeholder="Ej. 10x20 m"></div>
        <div><label>Número de niveles</label>
          <select name="niveles">
            <option>1</option><option selected>2</option><option>3</option>
          </select>
        </div>
      </div>
      <div class="row2">
        <div><label>Estilo arquitectónico</label>
          <select name="estilo">
            <option>Moderno minimalista</option>
            <option>Contemporáneo</option>
            <option>Clásico</option>
            <option>Industrial</option>
            <option>Mediterráneo</option>
            <option>Otro</option>
          </select>
        </div>
        <div><label>Color principal de fachada</label><input name="color" placeholder="Ej. Blanco, Gris, Beige"></div>
      </div>
      <label>Descripción adicional (opcional)</label>
      <textarea name="descripcion" placeholder="Cochera, jardín, alberca..."></textarea>
      <button class="btn-gen" type="submit">✨ GENERAR RENDER GRATIS</button>
    </form>
    <div id="progress-area"><div class="progress-bar-bg"><div class="progress-bar-fill" id="prog-fill"></div></div><p id="status-msg">Iniciando...</p></div>
    <div id="result-area"><img id="render-img" src="" alt="Render"><div class="action-btns"><a class="btn-pay" href="https://mpago.la/2CskJif" target="_blank">💳 Pagar $200 MXN sin marca</a><a class="btn-wa" href="https://wa.me/" target="_blank">💬 Enviar por WhatsApp</a></div><div class="price-note"><strong>Nota:</strong> Gratis con marca de agua; pago obtienes alta calidad limpia.</div></div>
  </div>
  <footer>© ERICK RENDERIZADO</footer>
</div>
<script>
const form = document.getElementById('form');
form.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = e.submitter;
  btn.disabled = true;
  document.getElementById('progress-area').style.display = 'block';
  document.getElementById('result-area').style.display = 'none';
  const datos = new FormData(form);
  const prog = setInterval(()=>{
    const w = Math.min(95, parseFloat(document.getElementById('prog-fill').style.width||0)+Math.random()*7);
    document.getElementById('prog-fill').style.width = w+'%';
    document.getElementById('status-msg').textContent = w<40?'Recibiendo datos...':w<80?'Diseñando render...':'Terminando...';
  },350);
  try{
    const r = await fetch('/generar',{method:'POST',body:datos});
    const d = await r.json();
    clearInterval(prog);
    document.getElementById('prog-fill').style.width='100%';
    setTimeout(()=>{
      document.getElementById('progress-area').style.display='none';
      if(d.ok){document.getElementById('render-img').src='/ver/'+d.id;document.getElementById('result-area').style.display='block';}
      btn.disabled=false;
    },800);
  }catch(err){clearInterval(prog);btn.disabled=false;}
});
</script>
</body>
</html>
"""

def generar_imagen(datos, job_id):
    try:
        img = Image.new('RGB', (800, 600), color='#1a1a2e')
        d = ImageDraw.Draw(img)
        fnt = ImageFont.load_default()
        d.text((40,40),"ERICK RENDERIZADO",font=fnt,fill="#e94560")
        d.text((40,90),f"Cuartos: {datos.get('cuartos')} | Baños: {datos.get('banos')}",font=fnt,fill="#ddd")
        d.text((40,120),f"Medidas: {datos.get('medidas')} | Niveles: {datos.get('niveles')}",font=fnt,fill="#ddd")
        d.text((40,150),f"Estilo: {datos.get('estilo')} | Color: {datos.get('color')}",font=fnt,fill="#ddd")
        d.text((40,540),"© MUESTRA CON MARCA DE AGUA",font=fnt,fill="#e94560")
        ruta = os.path.join(RENDERS_DIR,f"{job_id}.png")
        img.save(ruta)
        jobs[job_id] = {"estado":"listo","ruta":ruta}
    except Exception as e: jobs[job_id]={"estado":"error"}

@app.route('/')
def inicio(): return render_template_string(HTML)
@app.route('/generar',methods=['POST'])
def generar():
    jid=str(uuid.uuid4())
    jobs[jid]={"estado":"procesando"}
    threading.Thread(target=generar_imagen,args=(request.form.to_dict(),jid),daemon=True).start()
    return jsonify({"ok":True,"id":jid})
@app.route('/ver/<jid>')
def ver(jid):
    if jid not in jobs or jobs[jid]["estado"]!="listo":return "No disponible",404
    return send_file(jobs[jid]["ruta"],mimetype="image/png")
if __name__=="__main__": app.run(host='0.0.0.0',port=8080,debug=False,use_reloader=False)
  

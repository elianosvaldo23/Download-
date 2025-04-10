from flask import Flask, render_template, request,send_file
import os
from os.path import exists
app = Flask(__name__)

procesos = []
def killprocess():
	for proceso in procesos:
		proceso.terminate()

@app.route('/')
def hello(name=None):
	if not exists("./renderity_console.temp"):
		open("./renderity_console.temp","w").write("")
	logs = open("./renderity_console.temp","r").read()
	if not exists("autocron.temp"):
		open("autocron.temp","w").write("off")
	autocron = open("autocron.temp","r").read()
	if autocron == "on":
		autocron_button = '''<div class="row">
            <div class="col-12 text-center py-3">
                <a href="./autocron/off"><button class="btn btn-danger fs-2">𝙳𝙴𝚃𝙴𝙽𝙴𝚁 𝙰𝚄𝚃𝙾-𝙲𝚁𝙾𝙽𝙹𝙾𝙱</button></a>
            </div>
        </div>'''
	else:
	           autocron_button = '''<div class="row">
            <div class="col-12 text-center py-3">
                <a href="./autocron/on"><button class="btn btn-primary fs-2">𝙸𝙽𝙸𝙲𝙸𝙰𝚁 𝙰𝚄𝚃𝙾-𝙲𝚁𝙾𝙽𝙹𝙾𝙱</button></a>
            </div>
        </div>'''
	archivos_python = [archivo for archivo in os.listdir(".") if archivo.endswith(".py") and not archivo == "renderity.py" and not archivo == "renderity_utils.py"]
	if archivos_python:
	   archivos_py = ""
	   for archivo in archivos_python:
	   	archivos_py += '''<tbody>
                        <tr>
                            <td></td><td>'''+archivo+'''</td><td></td>
                            <td>
                                
                            </td>
                            <td>
                                <a href="./start/'''+archivo+'''"><button class="btn btn-outline-success">
                                    <i class="bi bi-play"></i> 𝙴𝙹𝙴𝙲𝚄𝚃𝙰𝚁</button></a>
                            </td>
                        </tr>
                    </tbody>\n'''
	else:
		archivos_py = '''<tbody>
                        <tr>
                            <td></td><td>NO HAY NINGÚN ARCHIVO PYTHON</td><td></td>
                            <td>
                                
                            </td>
                            <td>
                            </td>
                        </tr>
                    </tbody>'''
	return '''<!DOCTYPE html>
<html>
<head>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <link rel="stylesheet" href="https://unpkg.com/xterm/css/xterm.css" />
    <style>
    #terminal-container {
      height: 400px;
      width: 80%;
    }
@keyframes gradientAnimation {
    0% { background-position: 0 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0 50%; }
}

.glowing-text {
    background: linear-gradient(to right, #15a1ff, #1181cd, #0d629b, #2b96ff, #6ab6ff, #aaf4ff, #ffffff);
    background-size: 400% 100%;
    -webkit-text-fill-color: transparent;
    -webkit-background-clip: text;
    animation: gradientAnimation 10s linear infinite;
}</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
</head>
<body style="user-select:none;" class="bg-dark">
    <div class="container">
        <div class="row">
            <div class="col-12 text-center pt-5">
                <h1 style="font-size:5em;" class="glowing-text">ЯΞИDΞЯIΓУ</h1><h1 style="font-size:2em;" class="glowing-text">𝙱𝙴𝚃𝙰</h1>
            </div>
        </div>
        {{[AUTO-CRON]}}
        <div class="row">
            <div class="col-12 text-center py-3">
                <a href="./killproccess"><button class="btn btn-warning fs-2">𝙳𝙴𝚃𝙴𝙽𝙴𝚁 𝚃𝙾𝙳𝙾</button></a>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <table class="table bg-light">
                    <thead>
                        <tr>
                            <th></th>
                            <th class="text-primary">ɱɿς ƿყ੮Һ૦Ո</th>
                            <th></th>
                            <th></th>
                            <th>૦ƿ८ɿ૦Ո૯ς</th>
                        </tr>
                    </thead>
                    {{[ARCHIVOS]}}
                </table>
            </div>
        </div>
    </div>
<div class="container mt-4">
  <div class="row">
    <div class="col">
      <div class="d-flex justify-content-center">
      <div class='input-group d-flex justify-content-center'>
        <button id="boton1" class="btn btn-outline-primary">LOGS</button>
        <button id="boton2" class="btn btn-outline-primary">API</button><button id="boton3" class="btn btn-outline-primary">UPLOAD</button><button id="boton4" class="btn btn-outline-primary">SHELL</button>
       </div>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <div id="contenido" class="p-3 mt-3 bg-black text-light">
        𝙱𝙸𝙴𝙽𝚅𝙴𝙽𝙸𝙳𝙾 𝙰 𝚁𝙴𝙽𝙳𝙴𝚁𝙸𝚃𝚈 𝙲𝙾𝙽𝚂𝙾𝙻𝙴, 𝙿𝚄𝙴𝙳𝙴 𝚅𝙴𝚁 𝙻𝙾𝚂 𝙻𝙾𝙶𝚂 𝙳𝙴 𝚂𝚄 𝙱𝙾𝚃, 𝙿𝙰𝚁𝙰 𝙰𝙿𝚁𝙴𝙽𝙳𝙴𝚁 𝙰 𝚄𝚂𝙰𝚁 𝙻𝙰 𝙰𝙿𝙸 𝙿𝚄𝙻𝚂𝙴 𝙴𝙻 𝙱𝙾𝚃𝙾𝙽 '𝙰𝙿𝙸'
      </div>
    </div>
  </div>
</div>
<h1 style="font-size:2em; position:fixed; bottom:20px; right:20px; left:20px; text-align:center;" class="text-light">Creado por Alejandro Ortíz</h1>
<script src="https://unpkg.com/xterm/lib/xterm.js"></script>
<script>
$(document).ready(function() {
  $("#boton1").click(function() {
    $("#contenido").html("{{[LOGS]}}");
  });
  $("#boton4").click(function() {
    $("#contenido").html("<div class='container mt-4'><div id='terminal-container'></div><form id='command-form'><div class='input-group mb-3'><button class='btn btn-outline-primary bg-dark'>$</button><input type='text' class='form-control bg-dark text-light' id='command-input' placeholder='Ingresa un comando'><button type='submit' class='btn btn-outline-primary bg-dark'>EJECUTAR</button></div></form></div>");
    // Crea una instancia de la terminal
    const terminal = new Terminal({ 
      rendererType: 'canvas',
      convertEol: true,
      fontFamily: 'Courier New',
      fontSize: 14,
      cursorBlink: true
    });

    // Conecta la terminal al div del contenedor
    terminal.open(document.getElementById('terminal-container'));
    
    // Envia el comando al servidor y muestra la respuesta en tiempo real
    const commandForm = document.getElementById('command-form');
    const commandInput = document.getElementById('command-input');
    
    commandForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const command = commandInput.value;
      commandInput.value = '';
      
      terminal.writeln(`$ ${command}`);
      
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/command', true);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          response.output.forEach(line => terminal.writeln(line));
          response.error.forEach(line => terminal.writeln(line));
        }
      };
      xhr.send(`command=${encodeURIComponent(command)}`);
    });
  });
  $("#boton3").click(function() {
    $("#contenido").html('<form action="/upload" method="post" enctype="multipart/form-data"> <div class="mb-3"><label for="archivo" class="form-label">Seleccionar archivo</label> <input type="file" class="form-control" id="archivo" name="archivo"></div><button type="submit" class="btn btn-primary">Subir archivo</button></form>');
  });
  $("#boton2").click(function() {
    $("#contenido").html("<span style='color:#9055ff;'>from</span> renderity_utils <span style='color:#9055ff;'>import</span> apilog<br><br><span style='color:#71ff6a;'>#AÑADIR NUEVA ENTRADA A LA CONSOLA</span><br>apilog()<span style='color:#0096ff;'>.put</span>(<span style='color:#ffb355;'>'Nueva entrada'</span>)<br><br><span style='color:#71ff6a;'>#BORRAR LOGS DE LA CONSOLA</span><br>apilog()<span style='color:#0096ff;'>.clear</span>()");
  });
});

</script>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''.replace("{{[ARCHIVOS]}}", archivos_py).replace("{{[LOGS]}}",logs).replace("{{[AUTO-CRON]}}",autocron_button)

@app.route('/start/<file>')
def start(file):
    print("INICIANDO ARCHIVO")
    import subprocess
    subpro = subprocess.Popen(["python3",file])
    procesos.append(subpro)
    return '''<!DOCTYPE html>
<html>
<head>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <style>
@keyframes gradientAnimation {
    0% { background-position: 0 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0 50%; }
}

.glowing-text {
    background: linear-gradient(to right, #15a1ff, #1181cd, #0d629b, #2b96ff, #6ab6ff, #aaf4ff, #ffffff);
    background-size: 400% 100%;
    -webkit-text-fill-color: transparent;
    -webkit-background-clip: text;
    animation: gradientAnimation 10s linear infinite;
}</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
</head>
<body class="bg-dark">
    <div class="container pt-5">
        <div class="row pt-5">
            <div class="col-12 text-center pt-5">
                <h1 style="font-size:5em;" class="glowing-text">ЯΞИDΞЯIΓУ</h1>
            </div>
        </div>
        <div class="row">
            <div class="col-12 text-center py-3">
                <button class="btn btn-outline-light fs-2">CÓDIGO PYTHON INICIADO</button>
            </div>
        </div>
        <div class="row pt-5">
            <div class="col-12 text-center py-3 pt-5">
                <a href="../../"><button class="btn btn-primary fs-2">𝚅𝙾𝙻𝚅𝙴𝚁</button></a>
            </div>
        </div>


    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
@app.route('/killproccess')
def kill():
	killprocess()
	renderity = open("renderity_console.temp","r").read()
	open("renderity_console.temp","w").write(renderity+str("<span style='color:#ffb22b;'>[]</span> - 𝚂𝙴 𝙳𝙴𝚃𝚄𝚅𝙾 𝚃𝙾𝙳𝙾 - <span style='color:#ffb22b;'>[]</span>")+"<br>")
	open("autocron.temp","w").write("off")
	return '''<script>window.location.href = "../../";</script>'''
@app.route('/autocron/<opcion>')
def autocron(opcion):
	if opcion == "on":
		renderity = open("renderity_console.temp","r").read()
		open("autocron.temp","w").write("on")
		open("renderity_console.temp","w").write(renderity+str("<span style='color:#0098FF;'>[]</span> - 𝙰𝚄𝚃𝙾𝙲𝚁𝙾𝙽 𝙸𝙽𝙸𝙲𝙸𝙰𝙳𝙾 - <span style='color:#0098FF;'>[]</span>")+"<br>")
		if not exists("autocron/autocron_conf.py"):
			os.mkdir("autocron")
			host = request.host_url
			open("autocron/autocron_conf.py","w").write('''import time\nimport requests\nvalidador = True\ntimec = 0\nwhile validador:\n				time.sleep(60)\n				if open("autocron.temp","r").read() == "on":\n					timec += 1\n					renderity = open("renderity_console.temp","r").read()\n					requests.get("'''+host+'''", headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"})\n					print("AUTOCRON EJECUTADO EN '''+host+'''")\n				else:\n					import sys\n					sys.exit()''')
		import subprocess
		subpro = subprocess.Popen(["python3","autocron/autocron_conf.py"])
		procesos.append(subpro)
		print("AUTOCRON INICIADO")
	else:
		renderity = open("renderity_console.temp","r").read()
		open("renderity_console.temp","w").write(renderity+str("<span style='color:#ff000a;'>[]</span> - 𝙰𝚄𝚃𝙾𝙲𝚁𝙾𝙽 𝙳𝙴𝚃𝙴𝙽𝙸𝙳𝙾 - <span style='color:#ff000a;'>[]</span>")+"<br>")
		open("autocron.temp","w").write("off")
	return '''<script>window.location.href = "../../";</script>'''
@app.route('/upload', methods=['POST'])
def upload():
    # Obtener el archivo seleccionado por el usuario
    archivo = request.files['archivo']
    archivo.save(os.path.join('./', archivo.filename))
    return '''<script>window.location.href = "../../";</script>'''

@app.route('/command', methods=['POST'])
def execute_command():
    # Obtener el comando ingresado en el input del formulario
    command = request.form['command']

    # Ejecutar el comando utilizando el módulo subprocess
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Obtener las líneas de salida del comando
    output_lines = []
    for line in process.stdout:
        output_lines.append(line.strip())

    # Obtener las líneas de error del comando
    error_lines = []
    for line in process.stderr:
        error_lines.append(line.strip())

    # Devolver las líneas de salida y error al cliente
    return {'output': output_lines, 'error': error_lines}
@app.route("/files/<ambiente>/<path>")
def downloader(ambiente,path):
	if exists("./"+ambiente+"/"+path):
		return send_file("./"+ambiente+"/"+path, as_attachment=True)
	else:
		return '''NO ENCONTRADO'''
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=5000)

from flask import Flask, request, render_template, Response, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import boto3
import cv2
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Crear el cliente de Rekognition con las credenciales
client = boto3.client(
    'rekognition',
    aws_access_key_id = os.getenv("ACCESS_KEY"),
    aws_secret_access_key = os.getenv("SECRET_KEY")
)

# Datos del modelo personalizado
model = os.getenv("MODEL_ARN")
min_confidence = 90
directorio_actual = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = directorio_actual + '/static/assets/video'
ALLOWED_EXTENSION = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'wmv'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY_APP")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

video = None
videoCargado = False
camaraIniciada = False
pathVideo = ""


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisis-tiempo-real')
def capturar_camara():
    return render_template('analisis_tiempo_real.html')

@app.route('/analizar-video')
def analizar_video():
    return render_template('analisis_video.html')

@app.route("/camara_feed")
def camara_feed():
    global camaraIniciada
    camaraIniciada = True
    return Response( generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")
    
@app.route("/video_feed")
def video_feed():
    return Response( generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/finalizar-captura')
def finalizarCaptura():     
    global video, videoCargado, camaraIniciada
    if video != None :
        video.release()
        video = None
    videoCargado = False
    camaraIniciada = False    
    data = {'mensaje': '¡Solicitud procesada con éxito!'}
    return jsonify(data), 200
    
def generate():
    global video, model, min_confidence, videoCargado, pathVideo, camaraIniciada, directorio_actual
    if camaraIniciada == True :
        # print("CAMARA INICIADA")
        # cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        video = cv2.VideoCapture(0)
    elif  videoCargado == True :
        # print("VIDEO CARGADO INICIADO")
        ruta_archivo = pathVideo
        video = cv2.VideoCapture( ruta_archivo )  # Ruta de tu video            
    else: 
        # print("VIDEO ALMACENADO INICIADO")   
        ruta_archivo = os.path.join(directorio_actual, 'static/assets/video', 'AlmendraD.mp4')          
        video = cv2.VideoCapture( ruta_archivo )  # Ruta de tu video
    while True:
        ret, frame = video.read()
        if not ret:
            break                
        # cv2.rectangle( frame, (20,20), (100,100), (0, 255, 0), 2)
        # Convertir el frame a un formato de imagen (por ejemplo, JPEG)
        _, buffer = cv2.imencode('.jpg', frame)
        bytes_image = bytearray(buffer)
        
        response = client.detect_custom_labels(
            ProjectVersionArn = model,
            MinConfidence = min_confidence,
            Image = {
                'Bytes': bytes_image
            }
        )        
        # Obtener las dimensiones de la imagen (ancho y alto)
        alto, ancho = frame.shape[:2]        
        for bounding_box in response['CustomLabels']:
            if ( bounding_box['Name'] == "piedra" or bounding_box['Name'] == "rama" ):    
                left = int(bounding_box['Geometry']['BoundingBox']['Left'] * ancho)
                top = int(bounding_box['Geometry']['BoundingBox']['Top'] * alto)
                width = int(bounding_box['Geometry']['BoundingBox']['Width'] * ancho)
                height = int(bounding_box['Geometry']['BoundingBox']['Height'] * alto)            
                # Coordenadas del rectángulo
                bottom_right_x = left + width
                bottom_right_y = top + height            
                # Dibujar el rectángulo en la imagen
                cv2.rectangle(frame, (left, top), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)  # Color verde, grosor 2            
                # Agregar texto a la imagen con la etiqueta
                cv2.putText(frame, "DESCARTAR", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)  # Color verde, tamaño 0.7, grosor 2            
        
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')
    if video != None :
        video.release()
        video = None   
    
def allowed_file(filename):
    global ALLOWED_EXTENSION
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global pathVideo, videoCargado    
    if request.method == 'POST':       
        if 'file' not in request.files:
            data = {'mensaje': '¡Error al cargar el archivo!'}
            return jsonify(data), 400            
        file = request.files['file']       
        if file.filename == '':
            data = {'mensaje': '¡Error al cargar el archivo!'}
            return jsonify(data), 400            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pathVideo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save( pathVideo )
            videoCargado = True                        
            data = {'mensaje': '¡Solicitud procesada con éxito!'}
            return jsonify(data), 200                    
    else:
        return redirect( url_for('analizar_video') )


# if __name__ == '__main__':
#     app.run(port=5000, debug=True)       
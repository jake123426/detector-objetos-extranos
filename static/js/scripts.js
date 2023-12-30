
window.addEventListener('DOMContentLoaded', event => {
    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {        
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});

const btnIniciarCamara = document.getElementById('btnIniciarCamara');
const btnDetenerCamara = document.getElementById('btnDetenerCamara');
const imgCamara = document.getElementById('imgCamara');
const btnVideoAlmacenado = document.getElementById('btnVideoAlmacenado');
const imgVideo = document.getElementById('imgVideo');
const btnDetenerVideo = document.getElementById('btnDetenerVideo');
const uploadForm = document.getElementById('uploadForm');


btnVideoAlmacenado?.addEventListener('click', function() {
    imgVideo.src = srcGetVideo        
}); 

btnIniciarCamara?.addEventListener('click', function() {        
    imgCamara.src = srcGetCamera;
});

btnDetenerCamara?.addEventListener('click', function() {
    imgCamara.src = srcImgCamara;            
    fetch('/finalizar-captura')
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo completar la solicitud');
            }            
        })
});

btnDetenerVideo?.addEventListener('click', function() {
    imgVideo.src = srcImgVideo;        
    fetch('/finalizar-captura')
        .then(response => {
            if (!response.ok) {
                throw new Error('No se pudo completar la solicitud');
            }           
        })
});

uploadForm?.addEventListener('submit', function(event) {        

    event.preventDefault(); // Evitar el envío por defecto del formulario   
    // Obtener el archivo de video seleccionado por el usuario
    const videoFile = document.querySelector('input[type="file"]').files[0];
    if ( videoFile != null || videoFile != undefined ){
        document.getElementById('uploadForm').reset();
        // Crear un objeto FormData para enviar el archivo al servidor
        const formData = new FormData();
        formData.append('file', videoFile);
    
        // Enviar el archivo mediante una petición POST a una URL específica
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then( response => response.json())
        .then ( res =>{
            if ( res.mensaje === '¡Solicitud procesada con éxito!'){
                var miToast = new bootstrap.Toast(document.getElementById('miToast')); // Crear una instancia del toast
                miToast.show();                
                imgVideo.src = srcGetVideo; 
            }else{
                var myModal = new bootstrap.Modal(document.getElementById('exampleModal'));
                myModal.show();            
            }
        })
        .catch( error => {                  
            var myModal = new bootstrap.Modal(document.getElementById('exampleModal'));
            myModal.show();        
        });
    } else {
        var miToast = new bootstrap.Toast(document.getElementById('miToast2')); 
        miToast.show();
    }
});



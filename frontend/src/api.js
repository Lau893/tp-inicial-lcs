import axios from 'axios';

const apiClient = axios.create({
  // Las peticiones se hacen a la misma URL que el frontend (ej. http://localhost:3000)
  // y el proxy de React las redirigirá al backend.
  baseURL: '/', 
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Helper para convertir una imagen de formato Data URI a un objeto Blob
const dataURIToBlob = (dataURI) => {
  // 1. Separar los metadatos del contenido de la imagen
  // "data:image/jpeg;base64,LzlqLzRBQ... => ["data:image/jpeg;base64", "LzlqLzRBQ..."]
  const [meta, data] = dataURI.split(',');

  // 2. Extraer el tipo MIME de los metadatos
  // "data:image/jpeg;base64" => "image/jpeg"
  const mimeString = meta.split(':')[1].split(';')[0];

  // 3. Decodificar el string base64 a datos binarios
  const byteString = atob(data);

  // 4. Crear un buffer y una vista de 8-bits para los datos binarios
  const arrayBuffer = new ArrayBuffer(byteString.length);
  const uint8Array = new Uint8Array(arrayBuffer);

  // 5. Llenar el buffer
  for (let i = 0; i < byteString.length; i++) {
    uint8Array[i] = byteString.charCodeAt(i);
  }

  // 6. Retornar el objeto Blob, que es el formato de archivo que necesitamos
  return new Blob([arrayBuffer], { type: mimeString });
};


export const registrarEmpleado = async (id, imageSrc) => {
  const formData = new FormData();
  formData.append('id_empleado', id);
  formData.append('file', dataURIToBlob(imageSrc), 'captura.jpg');

  return apiClient.post('/registrar', formData);
};

export const reconocerEmpleado = async (imageSrc) => {
  const formData = new FormData();
  formData.append('file', dataURIToBlob(imageSrc), 'captura.jpg');

  return apiClient.post('/reconocer', formData);
};
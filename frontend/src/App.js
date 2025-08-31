import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Form,
  Alert,
  Spinner,
  Image,
  Tabs,
  Tab,
} from 'react-bootstrap';
import { registrarEmpleado, reconocerEmpleado } from './api';

const videoConstraints = {
  width: 1280,
  height: 720,
  facingMode: 'user',
};

function App() {
  const webcamRef = useRef(null);
  const recognitionIntervalRef = useRef(null);

  // Estado para el registro
  const [idEmpleado, setIdEmpleado] = useState('');
  const [registroImg, setRegistroImg] = useState(null);
  const [registroResultado, setRegistroResultado] = useState(null);
  const [registroError, setRegistroError] = useState('');
  const [registroLoading, setRegistroLoading] = useState(false);

  // Estado para el reconocimiento
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [reconocimientoResultado, setReconocimientoResultado] = useState(null);

  // Limpia los resultados cuando se cambia de pestaña
  const handleTabSelect = (key) => {
    setRegistroResultado(null);
    setRegistroError('');
    setRegistroImg(null);
    setReconocimientoResultado(null);
    if (isRecognizing) {
      // Detiene el reconocimiento si estaba activo al cambiar de pestaña
      clearInterval(recognitionIntervalRef.current);
      recognitionIntervalRef.current = null;
      setIsRecognizing(false);
    }
  };

  const handleRegister = async () => {
    if (!idEmpleado) {
      setRegistroError('Por favor, ingrese un ID de empleado.');
      return;
    }
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      setRegistroError('No se pudo capturar la imagen de la webcam.');
      return;
    }
    setRegistroImg(imageSrc);
    setRegistroLoading(true);
    setRegistroError('');
    setRegistroResultado(null);

    try {
      const response = await registrarEmpleado(idEmpleado, imageSrc);
      setRegistroResultado(response.data);
    } catch (err) {
      setRegistroError(
        err.response?.data?.detail || 'Ocurrió un error al registrar.'
      );
    } finally {
      setRegistroLoading(false);
    }
  };

  const recognitionLoop = useCallback(async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot({ width: 640, height: 360 }); // Usar una resolución menor para el loop
      if (imageSrc) {
        try {
          const response = await reconocerEmpleado(imageSrc);
          setReconocimientoResultado(response.data);
        } catch (error) {
          console.error('Error en el reconocimiento:', error);
          setReconocimientoResultado({ reconocido: false });
        }
      }
    }
  }, [webcamRef]);

  const toggleRecognition = () => {
    if (isRecognizing) {
      clearInterval(recognitionIntervalRef.current);
      recognitionIntervalRef.current = null;
      setIsRecognizing(false);
      setReconocimientoResultado(null);
    } else {
      setIsRecognizing(true);
      setReconocimientoResultado(null);
      recognitionIntervalRef.current = setInterval(recognitionLoop, 1500);
    }
  };

  const getOverlay = () => {
    if (!isRecognizing || !reconocimientoResultado) return null;

    const { reconocido, id_empleado } = reconocimientoResultado;
    const message = reconocido ? `ID Empleado: ${id_empleado}` : 'Desconocido';
    const backgroundColor = reconocido ? 'rgba(0, 200, 0, 0.7)' : 'rgba(200, 0, 0, 0.7)';

    return (
      <div className="recognition-overlay" style={{ backgroundColor }}>
        {message}
      </div>
    );
  };

  return (
    <Container className="mt-4 mb-4">
      <h1 className="text-center mb-4">Sistema de Reconocimiento Facial</h1>
      <Row>
        <Col md={7}>
          <Card>
            <Card.Header as="h5">Cámara en Vivo</Card.Header>
            <Card.Body className="p-2">
              <div className="webcam-container">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  videoConstraints={videoConstraints}
                  className="w-100 rounded"
                />
                {getOverlay()}
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={5}>
          <Card>
            <Card.Body>
              <Tabs defaultActiveKey="reconocer" onSelect={handleTabSelect} variant="pills" className="mb-3" fill>
                <Tab eventKey="registrar" title="Registrar">
                  <h5 className="mt-3">Registrar Nuevo Empleado</h5>
                  <p className="text-muted small">Ingrese un ID, luego capture la foto para registrar al empleado.</p>
                  <Form.Group className="mb-3">
                    <Form.Label>ID de Empleado</Form.Label>
                    <Form.Control
                      type="number"
                      placeholder="Ej: 1, 2, 3..."
                      value={idEmpleado}
                      onChange={(e) => setIdEmpleado(e.target.value)}
                    />
                  </Form.Group>
                  <Button
                    variant="primary"
                    onClick={handleRegister}
                    disabled={registroLoading}
                    className="w-100"
                  >
                    {registroLoading ? (
                      <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true"/> Procesando...</>
                    ) : (
                      'Capturar y Registrar'
                    )}
                  </Button>

                  <div className="mt-3">
                    {registroError && <Alert variant="danger">{registroError}</Alert>}
                    {registroResultado && <Alert variant="success">{registroResultado.mensaje}</Alert>}
                  </div>

                  {registroImg && (
                    <div className="mt-3 text-center">
                      <p>Última foto capturada:</p>
                      <Image src={registroImg} rounded fluid style={{ maxHeight: '150px' }} className="snapshot-img"/>
                    </div>
                  )}
                </Tab>

                <Tab eventKey="reconocer" title="Reconocer">
                  <h5 className="mt-3">Reconocimiento en Tiempo Real</h5>
                  <p className="text-muted small">Active el reconocimiento para analizar el video de la cámara continuamente.</p>
                  <Button
                    variant={isRecognizing ? 'danger' : 'success'}
                    onClick={toggleRecognition}
                    className="w-100 p-3"
                  >
                    {isRecognizing ? 'Detener Reconocimiento' : 'Iniciar Reconocimiento'}
                  </Button>
                </Tab>
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default App;

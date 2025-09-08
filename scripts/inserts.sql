-- PRODUCTOS
INSERT INTO producto (nombre, precio) VALUES ('Galletitas de avena', 2.80);
INSERT INTO producto (nombre, precio) VALUES ('Barra de cereal con chocolate', 1.25);
INSERT INTO producto (nombre, precio) VALUES ('Budin de limon', 4.50);
INSERT INTO producto (nombre, precio) VALUES ('Alfajor de maicena', 1.50);
INSERT INTO producto (nombre, precio) VALUES ('Muffins de arandanos', 5.00);
INSERT INTO producto (nombre, precio) VALUES ('Tostadas de arroz', 2.10);
INSERT INTO producto (nombre, precio) VALUES ('Yogur bebible de frutilla', 3.20);
INSERT INTO producto (nombre, precio) VALUES ('Premezcla para pizza', 2.90);
INSERT INTO producto (nombre, precio) VALUES ('Bizcochos de grasa', 2.00);
INSERT INTO producto (nombre, precio) VALUES ('Grisines con sesamo', 2.30);

--ROLES
INSERT INTO rol (nombre) VALUES ('Encargado');
INSERT INTO rol (nombre) VALUES ('Operario');
INSERT INTO rol (nombre) VALUES ('Seguridad');
INSERT INTO rol (nombre) VALUES ('Administrador');

-- EMPLEADOS
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Carlos', 'Gomez', '28123456', 1);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Ana', 'Fernandez', '30789012', 1);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Juan', 'Perez', '32456789', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Maria', 'Rodriguez', '33123456', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Pedro', 'Martinez', '31789012', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Laura', 'Sanchez', '34456789', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Diego', 'Lopez', '35123456', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Sofia', 'Diaz', '36789012', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Martin', 'Gonzalez', '37456789', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Lucia', 'Torres', '38123456', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Javier', 'Ramirez', '39789012', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Valentina', 'Romero', '40456789', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Matias', 'Acosta', '41123456', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Camila', 'Benitez', '42789012', 2);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Roberto', 'Silva', '25456789', 3);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Florencia', 'Ortiz', '26123456', 3);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Lionel', 'Messi', '25456722', 4);
INSERT INTO empleado (nombre ,apellido ,documento, id_rol) VALUES ('Ariel', 'Ortega', '26123499', 4);

-- CLIENTES (40 en total)
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Supermercado La Estrella', '30112233445', 'Av. Corrientes 1234');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Almacen Don Jose', '30223344556', 'Calle Florida 567');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Kiosco 24 Horas', '30334455667', 'Av. Santa Fe 890');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Distribuidora El Sol', '30445566778', 'Av. Rivadavia 2345');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Tienda de Comestibles', '30556677889', 'Calle Lavalle 678');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Maxikiosco El Trebol', '30667788990', 'Av. Cordoba 3456');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Autoservicio Belgrano', '30778899001', 'Calle Belgrano 123');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Mercado Central SRL', '30889900112', 'Av. de Mayo 901');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Despensa La Familia', '30990011223', 'Calle Peru 234');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Punto de Venta Express', '30001122334', 'Av. Callao 456');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Comercial del Norte', '30112233446', 'Calle Paraguay 789');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Provisiones del Sur', '30223344557', 'Av. Independencia 1011');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Emporio del Sabor', '30334455668', 'Calle Defensa 1213');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Minimercado La Esquina', '30445566779', 'Av. Boedo 1415');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Servicompras 24', '30556677890', 'Calle Chile 1617');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Tiendita de la Abuela', '30667788991', 'Av. Caseros 1819');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Abastecedora Central', '30778899002', 'Calle Mexico 2021');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Super Ahorro', '30889900113', 'Av. Jujuy 2223');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Buen Gusto', '30990011224', 'Calle Venezuela 2425');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Provision', '30001122335', 'Av. Entre Rios 2627');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Market Plaza', '30112233447', 'Calle Sarandi 2829');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Todo Suelto', '30223344558', 'Av. Pueyrredon 3031');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Despensa del Barrio', '30334455669', 'Calle Ecuador 3233');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Gigante de los Precios', '30445566780', 'Av. Nazca 3435');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Almacen de Ramos Generales', '30556677891', 'Calle Aranguren 3637');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Confianza', '30667788992', 'Av. Gaona 3839');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Mercadito Amigo', '30778899003', 'Calle Neuquen 4041');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Supermercado Economico', '30889900114', 'Av. Warnes 4243');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Canasta Basica', '30990011225', 'Calle Paysandu 4445');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Rincon del Ahorro', '30001122336', 'Av. San Martin 4647');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('Despensa San Cayetano', '30112233448', 'Calle Nicasio Oroño 4849');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Vaca Lechera', '30223344559', 'Av. Juan B. Justo 5051');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Emporio de la Galleta', '30334455670', 'Calle Darwin 5253');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Reina de la Oferta', '30445566781', 'Av. Dorrego 5455');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Palacio de la Comida', '30556677892', 'Calle Humboldt 5657');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Esquina del Sabor', '30667788993', 'Av. Niceto Vega 5859');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Punto Justo', '30778899004', 'Calle Gorriti 6061');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Despensa de la Suerte', '30889900115', 'Av. Honduras 6263');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('El Trebol de la Fortuna', '30990011226', 'Calle El Salvador 6465');
INSERT INTO cliente (nombre, documento, direccion) VALUES ('La Ultima Parada', '30001122337', 'Av. Cabildo 6667');
-- AVISO: Legacy (SQLite-like). No usar para el backend Postgres actual.
-- Para semillas del backend usar scripts/seed.sql

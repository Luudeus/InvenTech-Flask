CREATE DATABASE INVENTECH;
USE INVENTECH;
CREATE TABLE Item (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    marca VARCHAR(255) NOT NULL,
    fecha_de_vencimiento DATE,
    categoria VARCHAR(100),
    stock INT NOT NULL
);

CREATE TABLE User (
    RUT VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255),
    permisos VARCHAR(255),
    contrasenia VARCHAR(255)
);


INSERT INTO Item (nombre, marca, fecha_de_vencimiento, categoria, stock) VALUES 
('Arroz', 'Marca A', '2024-12-31', 'Pastas y Cereales', 100),
('Fideos', 'Marca B', '2025-06-30', 'Pastas y Cereales', 80),
('Leche', 'Marca C', '2024-11-30', 'Lácteos', 120),
('Yogur', 'Marca D', '2024-12-15', 'Lácteos', 90),
('Manzanas', 'Marca E', '2024-05-01', 'Frutas y Verduras', 150),
('Papas', 'Marca F', '2024-04-30', 'Frutas y Verduras', 110),
('Carne de res', 'Marca G', '2024-05-10', 'Carnes', 70),
('Pollo', 'Marca H', '2024-05-05', 'Carnes', 85),
('Atún en lata', 'Marca I', '2025-01-31', 'Alimentos enlatados', 95),
('Salsa de tomate', 'Marca J', '2024-09-30', 'Alimentos enlatados', 110),
('Jabón de manos', 'Marca K', '2025-02-28', 'Cuidado Personal', 75),
('Papel higiénico', 'Marca L', '2025-03-31', 'Limpieza', 120),
('Cepillo de dientes', 'Marca M', '2025-04-30', 'Cuidado Personal', 100),
('Refresco de cola', 'Marca N', '2024-08-31', 'Bebidas', 150),
('Agua mineral', 'Marca O', '2025-12-31', 'Bebidas', 200),
('Helado', 'Marca P', '2024-09-30', 'Confitería', 80),
('Chocolate', 'Marca Q', '2025-07-31', 'Confitería', 100),
('Pan', 'Marca R', '2024-04-30', 'Panadería', 130),
('Mantequilla', 'Marca S', '2024-11-30', 'Lácteos', 90),
('Galletas', 'Marca T', '2025-08-31', 'Confitería', 110);



INSERT INTO User (RUT, nombre, correo, permisos, contrasenia) VALUES 
('100122334', 'Juan Pérez', 'juanperez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('234567890', 'Ana Gómez', 'anagomez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('345678901', 'Carlos Ruiz', 'carlosruiz@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('456789012', 'María López', 'marialopez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('567890123', 'Lucía Hernández', 'luciahernandez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('678901234', 'Miguel Ángel', 'miguelangel@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('789012345', 'Sofía Martínez', 'sofiamartinez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('890123456', 'Diego Torres', 'diegotorres@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('901234567', 'Andrea Jiménez', 'andreajimenez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('012345678', 'Roberto García', 'robertogarcia@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('112233445', 'Sara Molina', 'saramolina@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('223344556', 'Luis Navarro', 'luisnavarro@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('334455667', 'Marta Sánchez', 'martasanchez@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('445566778', 'Fernando Castro', 'fernandocastro@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('556677889', 'Laura Ortiz', 'lauraortiz@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('667788990', 'Daniel Romero', 'danielromero@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('778899001', 'Patricia Navarrete', 'patricianavarrete@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('889900112', 'Iván Morales', 'ivanmorales@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('990011223', 'Carmen Díaz', 'carmendiaz@mail.com', 'normal', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26'),
('123456789', 'admin', 'admin@inventech.cl', 'admin', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26');
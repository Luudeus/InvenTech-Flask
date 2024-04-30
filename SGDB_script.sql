CREATE DATABASE SGDB;
USE SGDB;
CREATE TABLE Book (
    id_book INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    anio YEAR,
    genero VARCHAR(100),
    stock INT NOT NULL
);

CREATE TABLE User (
    RUT VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255),
    permisos VARCHAR(255),
    contrasenia VARCHAR(255)
);

CREATE TABLE Lending (
    order_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    RUT_User VARCHAR(10) NOT NULL,
    id_book INT NOT NULL,
    fecha_entrega DATE,
    fecha_devolucion DATE,
    estado VARCHAR(50),
    FOREIGN KEY (RUT_User) REFERENCES User(RUT),
    FOREIGN KEY (id_book) REFERENCES Book(id_book)
);

CREATE TABLE Solicitud (
    solicitud_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    RUT_User VARCHAR(10) NOT NULL,
    id_book INT NOT NULL,
    titulo_libro VARCHAR(255) NOT NULL,
    fecha_solicitud DATE,
    FOREIGN KEY (RUT_User) REFERENCES User(RUT),
    FOREIGN KEY (id_book) REFERENCES Book(id_book)
);

INSERT INTO Book (titulo, autor, anio, genero, stock) VALUES 
('Cien Años de Soledad', 'Gabriel García Márquez', 1967, 'Novela', 10),
('1984', 'George Orwell', 1949, 'Distopía', 15),
('El Principito', 'Antoine de Saint-Exupéry', 1943, 'Fábula', 20),
('El Amor en los Tiempos del Cólera', 'Gabriel García Márquez', 1985, 'Novela', 5),
('El Viejo y el Mar', 'Ernest Hemingway', 1952, 'Novela', 10),
('El Hobbit', 'J.R.R. Tolkien', 1937, 'Fantasía', 12),
('Orgullo y Prejuicio', 'Jane Austen', 1910, 'Novela', 8),
('To Kill a Mockingbird', 'Harper Lee', 1960, 'Novela', 10),
('Un Mundo Feliz', 'Aldous Huxley', 1932, 'Distopía', 7),
('Fahrenheit 451', 'Ray Bradbury', 1953, 'Distopía', 9),
('El Gran Gatsby', 'F. Scott Fitzgerald', 1925, 'Novela', 14),
('El Guardián Entre el Centeno', 'J.D. Salinger', 1951, 'Novela', 6),
('Lolita', 'Vladimir Nabokov', 1955, 'Novela', 8),
('El Señor de los Anillos', 'J.R.R. Tolkien', 1954, 'Fantasía', 10),
('El Código Da Vinci', 'Dan Brown', 2003, 'Novela Misterio', 20),
('Harry Potter y la Piedra Filosofal', 'J.K. Rowling', 1997, 'Fantasía', 30),
('El Alquimista', 'Paulo Coelho', 1988, 'Novela', 12),
('Crimen y Castigo', 'Fiódor Dostoievski', 1917, 'Novela', 7),
('La Sombra del Viento', 'Carlos Ruiz Zafón', 2001, 'Novela', 5),
('El guardián entre el centeno', 'J.D. Salinger', 1951, 'Novela', 11);




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
('123456789', 'Bibliotecario', 'bibliotecario@futuralib.cl', 'bibliotecario', 'scrypt:32768:8:1$HzP950Lc5oxQ6Guw$b6ef14338b8db610ef345d05b18e268950380ae6c43e72f3c6a75d802ebd0a3b1c140fc0664a1cce270917f319abd80817bfc6b67d1f615c955c14801fb52e26');


INSERT INTO Lending (RUT_User, id_book, fecha_entrega, fecha_devolucion, estado) VALUES 
('100122334', 1, '2023-01-01', '2023-01-15', 'Devuelto'),
('234567890', 2, '2023-01-10', NULL, 'Prestado'),
('345678901', 3, '2023-02-01', '2023-02-15', 'Devuelto'),
('456789012', 4, '2023-02-10', NULL, 'Prestado'),
('567890123', 5, '2023-03-01', '2023-03-15', 'Devuelto'),
('678901234', 6, '2023-03-10', NULL, 'Prestado'),
('789012345', 7, '2023-04-01', '2023-04-15', 'Devuelto'),
('890123456', 8, '2023-04-10', NULL, 'Prestado'),
('901234567', 9, '2023-05-01', '2023-05-15', 'Devuelto'),
('012345678', 10, '2023-05-10', NULL, 'Prestado'),
('112233445', 11, '2023-06-01', '2023-06-15', 'Devuelto'),
('223344556', 12, '2023-06-10', NULL, 'Prestado'),
('334455667', 13, '2023-07-01', '2023-07-15', 'Devuelto'),
('445566778', 14, '2023-07-10', NULL, 'Prestado'),
('556677889', 15, '2023-08-01', '2023-08-15', 'Devuelto'),
('667788990', 16, '2023-08-10', NULL, 'Prestado'),
('778899001', 17, '2023-09-01', '2023-09-15', 'Devuelto'),
('889900112', 18, '2023-09-10', NULL, 'Prestado'),
('990011223', 19, '2023-10-01', '2023-10-15', 'Devuelto'),
('123456789', 20, '2023-10-10', NULL, 'Prestado');
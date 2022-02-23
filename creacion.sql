CREATE TABLE cliente
(
    cliente_id BIGINT,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    telefono BIGINT,
    PRIMARY KEY(cliente_id)
);

CREATE TABLE estacion
(
    estacion_id INT,
    nombre VARCHAR NOT NULL,
    pais VARCHAR NOT NULL,
    ciudad VARCHAR NOT NULL,
    PRIMARY KEY(estacion_id)
);

CREATE TABLE ruta
(
    ruta_id SERIAL,
    nombre VARCHAR NOT NULL,
    estacion_origen INT,
    estacion_destino INT,
    monto_vip NUMERIC(10,2) NOT NULL CHECK(monto_vip > 0),
    monto_ejecutivo NUMERIC(10,2) NOT NULL CHECK(monto_ejecutivo > 0),
    monto_economico NUMERIC(10,2) NOT NULL CHECK(monto_economico > 0),
    sillas_vip INT CHECK(sillas_vip >= 0 AND sillas_vip <= 10),
    sillas_ejecutivo INT CHECK(sillas_ejecutivo >= 0 AND sillas_ejecutivo <= 20),
    sillas_economico INT CHECK(sillas_economico >= 0 AND sillas_economico <= 30),
    PRIMARY KEY(ruta_id),
    FOREIGN KEY(estacion_origen) REFERENCES estacion,
    FOREIGN KEY(estacion_destino) REFERENCES estacion
);

CREATE TABLE reserva
(
    reserva_id SERIAL,
    cliente_id INT,
    ruta_id INT,
    monto NUMERIC(10,2) CHECK(monto > 0),
    fecha TIMESTAMP NOT NULL default now(),
    medio_pago VARCHAR NOT NULL,
    tipo_silla VARCHAR NOT NULL CHECK(tipo_silla IN('vip','ejecutivo','economico')),
    PRIMARY KEY(reserva_id),
    FOREIGN KEY(cliente_id) REFERENCES cliente,
    FOREIGN KEY(ruta_id) REFERENCES ruta
)

CREATE OR REPLACE FUNCTION idDeEstacion(ciudadABuscar VARCHAR) RETURNS INTEGER AS $$
BEGIN
    RETURN estacion.estacion_id 
    FROM estacion
    WHERE estacion.ciudad=ciudadABuscar;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ciudadDeIdEstacion(id INTEGER) RETURNS VARCHAR AS $$
BEGIN
    RETURN estacion.ciudad 
    FROM estacion
    WHERE estacion.estacion_id=id;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getRutaID(origen INT, destino INT) RETURNS INT AS $$
BEGIN
    RETURN ruta.ruta_id
    FROM ruta
    WHERE ruta.estacion_origen = origen AND ruta.estacion_destino = destino;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getMontoVIP(id INT) RETURNS NUMERIC AS $$
BEGIN
    RETURN ruta.monto_vip
    FROM ruta
    WHERE ruta.ruta_id = id;
END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getMontoEjecutivo(id INT) RETURNS NUMERIC AS $$
BEGIN
    RETURN ruta.monto_ejecutivo
    FROM ruta
    WHERE ruta.ruta_id = id;
END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION getMontoEconomico(id INT) RETURNS NUMERIC AS $$
BEGIN
    RETURN ruta.monto_economico
    FROM ruta
    WHERE ruta.ruta_id = id;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gen_reserva_vip(id_de_ruta INT, id_de_cliente INT, pago_medio VARCHAR)
LANGUAGE plpgsql    
AS $$
BEGIN
    UPDATE ruta
    SET sillas_vip = sillas_vip - 1
    WHERE ruta_id = id_de_ruta;

    INSERT INTO reserva (cliente_id, ruta_id,monto,medio_pago,tipo_silla) VALUES (id_de_cliente, id_de_ruta, getMontoVIP(id_de_ruta),pago_medio,'vip');
END;
$$;

CREATE OR REPLACE PROCEDURE gen_reserva_ejecutivo(id_de_ruta INT, id_de_cliente INT, pago_medio VARCHAR)
LANGUAGE plpgsql    
AS $$
BEGIN
    UPDATE ruta
    SET sillas_ejecutivo = sillas_ejecutivo - 1
    WHERE ruta_id = id_de_ruta;

    INSERT INTO reserva
        (cliente_id, ruta_id,monto,medio_pago,tipo_silla)
    VALUES
        (id_de_cliente, id_de_ruta, getMontoEjecutivo(id_de_ruta), pago_medio, 'ejecutivo');
END;
$$;

CREATE OR REPLACE PROCEDURE gen_reserva_economico(id_de_ruta INT, id_de_cliente INT, pago_medio VARCHAR)
LANGUAGE plpgsql    
AS $$
BEGIN
    UPDATE ruta
    SET sillas_economico = sillas_economico - 1
    WHERE ruta_id = id_de_ruta;

    INSERT INTO reserva
        (cliente_id, ruta_id,monto,medio_pago,tipo_silla)
    VALUES
        (id_de_cliente, id_de_ruta, getMontoEconomico(id_de_ruta), pago_medio, 'economico');
END;
$$;
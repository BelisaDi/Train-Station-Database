CREATE OR REPLACE PROCEDURE registroCliente(id INT,nombre_1 VARCHAR, apellido_1 VARCHAR, email_1 VARCHAR, telefono_1 INT)
LANGUAGE plpgsql
AS $$
 BEGIN
  INSERT INTO cliente(cliente_id,nombre,appelido,email,telefono)
         VALUES(id, nombre_1, apellido_1, email_1, telefono_1);
 COMMIT;
 END;
$$;
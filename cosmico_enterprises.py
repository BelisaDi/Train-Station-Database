import flask, pandas, psycopg2
from flask import Flask, redirect, url_for, request, render_template
import networkx as nx

"""
Se crea la aplicación.
"""

app = flask.Flask(__name__)
app.config["DEBUG"] = True 


"""
Parámetros de conexión.
"""

parametrosDict = {
    "host": "isilo.db.elephantsql.com",
    "database": "eeubnhhz",
    "user": "eeubnhhz",
    "password": "Q3S6Rze1cdcsnnIi3aS9mMekOkQz2r4y"
}

"""
Función que retorna un data_frame dado un query.
"""
def query2DataFrame(sqlQuery):
    DBConnection = None 
    resultDataFrame = None
    try: 
        print("Connecting to database...")
        DBConnection = psycopg2.connect(**parametrosDict)
        resultDataFrame = pandas.read_sql_query(sqlQuery, DBConnection)
        DBConnection.close()
        return resultDataFrame
    except(Exception, psycopg2.DatabaseError) as error:
        print("Error en el query: ",error)
        return None 
    finally:
        if DBConnection is not None:
            DBConnection.close()

def maximizacion(Grafo,tipo):
    if tipo == 0:
        objetivo = "duracion (min)"
    elif tipo == 1:
        objetivo = "monto_vip"
    elif tipo == 2:
        objetivo = "monto_economico"
    elif tipo == 3:
        objetivo = "monto_ejecutivo"

    for index, row in rutas.iterrows():
        origen = row["origen_id"]
        destino = row["destino_id"]
        peso = row[objetivo]
        Grafo.add_edge(origen, destino, weight=peso)

rutas = pandas.read_csv('rutas2.csv', sep=';', encoding='latin1').fillna('-')
G_0 = nx.DiGraph()
G_1 = nx.DiGraph()
G_2 = nx.DiGraph()
G_3 = nx.DiGraph()
maximizacion(G_0,0)
maximizacion(G_1,1)
maximizacion(G_2,2)
maximizacion(G_3,3)

"""
Ahora si, rutas de la aplicación
"""

"""
HOME
"""
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

"""
ESTACIONES, CIUDADES Y PAÍSES
"""
@app.route("/estaciones", methods=["GET"])
def mostrarEstaciones():
    query = "SELECT * FROM estacion"
    tabla = query2DataFrame(query)
    return tabla.to_html()

"""
MAPA DEL SISTEMA
"""
@app.route("/mapa", methods=["GET"])
def mostrarMapa():
    return render_template("map.html")

"""
REGISTRARSE
"""
@app.route("/registro", methods=["GET"])
def formulario():
    return app.send_static_file("registroCliente.html")

@app.route("/resultadoRegistro",methods=["POST","GET"])
def registrarse():
    identificacion = str(request.values.get("ID"))
    nombre = str(request.values.get("Nombre"))
    apellido = str(request.values.get("Apellido"))
    email = str(request.values.get("Email"))
    telefono = str(request.values.get("Telefono"))
    DBConnection = None
    try:
        print("Connecting to database...")
        DBConnection = psycopg2.connect(**parametrosDict)
        cursorDB = DBConnection.cursor()
        if telefono == "":
            query = "INSERT INTO cliente(cliente_id, nombre, apellido, email) VALUES("+identificacion+",'"+nombre+"','"+apellido+"','"+email+"')"
        else:
            query = "INSERT INTO cliente(cliente_id, nombre, apellido, email, telefono) VALUES("+identificacion+",'"+nombre+"','"+apellido+"','"+email+"',"+telefono+")"
        cursorDB.execute(query)
        DBConnection.commit()
        DBConnection.close()
        return "Todo en orden!"
    except:
        return "Ocurrió un error... Vuélvalo a intentar."
    finally:
        if DBConnection is not None:
            DBConnection.close()

"""
REVISAR SI ESTÁ REGISTRADO
"""
@app.route("/revisarRegistro",methods=["GET"])
def checkRegister():
    return app.send_static_file("revisarRegistro.html")

@app.route("/resultadoRevisarRegistro",methods=["GET","POST"])
def retornoCheck():
    identificacion = str(request.values.get("ID"))
    query = "SELECT cliente.nombre, cliente.apellido FROM cliente WHERE cliente.cliente_id = "+identificacion 
    tabla = query2DataFrame(query)
    if tabla.empty: 
        return "No se encuentra en nuestra base de datos."
    else:
        return "Se encuentra registrado como "+tabla.at[0,"nombre"]+" "+tabla.at[0,"apellido"]

"""
RESERVA
"""
@app.route("/planearViaje", methods=["GET"])
def ingresoDatos():
    return app.send_static_file("buscarRuta.html")

@app.route("/resultadoRuta",methods=["POST","GET"])
def mostrarRuta():
    DBConnection = None
    try:
        print("Connecting to database...")
        DBConnection = psycopg2.connect(**parametrosDict)
        cursorDB = DBConnection.cursor()
        origen = request.values.get("origen")
        destino = request.values.get("destino")
        tipo_de_minimizacion = int(request.values.get("minimizar"))
        query_origen = "SELECT idDeEstacion('"+origen+"')"
        cursorDB.execute(query_origen)
        id_origen = int(cursorDB.fetchone()[0])
        query_destino = "SELECT idDeEstacion('"+destino+"')"
        cursorDB.execute(query_destino)
        id_destino = int(cursorDB.fetchone()[0])
        rutas = []
        ciudades_ids = {}
        if tipo_de_minimizacion == 0:
            resultado = nx.shortest_path(G_0, source=id_origen, target=id_destino)
        elif tipo_de_minimizacion == 1:
            resultado = nx.shortest_path(G_1, source=id_origen, target=id_destino)
        elif tipo_de_minimizacion == 2:
            resultado = nx.shortest_path(G_2, source=id_origen, target=id_destino)
        elif tipo_de_minimizacion == 3:
            resultado = nx.shortest_path(G_3, source=id_origen, target=id_destino)
        for i in range(len(resultado)-1):
            query_origen = "SELECT ciudadDeIdEstacion("+str(resultado[i])+")"
            query_destino = "SELECT ciudadDeIdEstacion("+str(resultado[i+1])+")"
            cursorDB.execute(query_origen)
            ciudad_1 = cursorDB.fetchone()[0]
            cursorDB.execute(query_destino)
            ciudad_2 =cursorDB.fetchone()[0]
            ciudades_ids[ciudad_1] = resultado[i]
            ciudades_ids[ciudad_2] = resultado[i+1]
            rutas.append(str(ciudad_1)+" - "+str(ciudad_2))
        DBConnection.close()
        script = "<html><body> Esta son las rutas sugeridas. Seleccione el tipo de silla deseado: "
        script += " <form action=\"http://localhost:5000/reserva\" method=\"POST\">"
        script += "<p> ID <input type = \"test\" name = \"ID\" / ></p>"
        script += "<p> Tipo de pago <select id=\"tipo_pago\" name=\"tipo_pago\"> <option value = \"tarjeta\"> Tarjeta </option> <option value = \"efectivo\"> Efectivo </option> <option value = \"apple_pay\"> Apple pay </option></select > <br/></p>"
        cont = 0
        for ruta in rutas:
            ciudades = ruta.split(" - ") 
            query_id_ruta = "SELECT getRutaID("+str(ciudades_ids[ciudades[0]])+","+str(ciudades_ids[ciudades[1]])+")"
            id_ruta_tabla = query2DataFrame(query_id_ruta)
            print(ciudades[0])
            print(ciudades[1])
            id_ruta = id_ruta_tabla.at[0,"getrutaid"]
            query_largo = "SELECT monto_vip,monto_ejecutivo,monto_economico,sillas_vip,sillas_ejecutivo,sillas_economico FROM ruta WHERE ruta.ruta_id = "+str(id_ruta)
            tabla = query2DataFrame(query_largo)
            tabla_mostrar = "<table class=\"egt\"><tr><th>Tipo de silla</th><th>Sillas disponibles</th><th>Precio por silla</th></tr>"
            tabla_mostrar += "<tr><td>VIP</td><td>" + str(tabla.at[0, "sillas_vip"])+"</td><td>" + str(tabla.at[0, "monto_vip"])+"</td></tr>"
            tabla_mostrar += "<tr><td>Ejecutivo</td><td>" + str(tabla.at[0, "sillas_ejecutivo"])+"</td><td>" + str(tabla.at[0, "monto_ejecutivo"])+"</td></tr>"
            tabla_mostrar += "<tr><td>Economico</td><td>" + str(tabla.at[0, "sillas_economico"])+"</td><td>" + str(tabla.at[0, "monto_economico"])+"</td></tr></table>"
            script += "<p>Ruta "+ruta+". Tipo de silla <select id=\"tipo_silla\" name=\"tipo_silla_"+str(cont)+"\"> <option value = \"vip\"> VIP </option> <option value = \"ejecutivo\"> Ejecutivo </option> <option value = \"economico\"> Economico </option></select > <br/>" + tabla_mostrar + " </p>"
            script += "<input type = \"hidden\" name = \"ruta_"+str(cont)+"\" value=\""+str(id_ruta)+"\"/>"
            cont += 1
        script += "<p> <input type = \"hidden\" name = \"count\" value=\""+str(cont)+"\"/> </p>"
        script += "<p> <input type = \"submit\" value = \"Reservar\"/> </p>"
        script += "</form></body ></html >"
        return script
    except(Exception, psycopg2.DatabaseError) as error:
        print("Error en el query: ", error)
        return None

@app.route("/reserva",methods=["POST","GET"])
def reservari():
    cont = int(request.values.get("count"))
    identificacion = int(request.values.get("ID"))
    DBConnection = None 
    try:
        print("Connecting to database...")
        DBConnection = psycopg2.connect(**parametrosDict)
        cursorDB = DBConnection.cursor()
        for i in range(cont):
            ruta_id = int(request.values.get("ruta_"+str(i)))
            tipo_silla = request.values.get("tipo_silla_"+str(i))
            tipo_pago = request.values.get("tipo_pago")
            query = "CALL gen_reserva_"+str(tipo_silla)+"("+str(ruta_id)+","+str(identificacion)+",'"+tipo_pago+"')"
            cursorDB.execute(query)
        DBConnection.commit()
        DBConnection.close()
        return "¡Reserva hecha!"
    except(Exception, psycopg2.DatabaseError) as error:
        print("Error en el query: ", error)
        return None
    finally:
        if DBConnection is not None:
            DBConnection.close()

"""
Revisar si tiene reserva
"""

@app.route("/revisarReserva",methods=["GET"])
def revisarReserva():
    return app.send_static_file("revisarReserva.html")

@app.route("/resultadoRevisarReserva",methods=["POST","GET"])
def checkReserva():
    identificacion = str(request.values.get("ID"))
    query = "SELECT * FROM reserva WHERE reserva.cliente_id = "+identificacion
    tabla = query2DataFrame(query)
    return tabla.to_html()


app.run()

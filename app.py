from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = "https://gisvector.dadep.gov.co/arcgis/rest/services/IDECA/IDECA_Mapa_Referencia/MapServer/0/query"


def obtener_localidades():
    parametros = {
        "where": "1=1",
        "outFields": "localidad_",
        "returnGeometry": "false",
        "returnDistinctValues": "true",
        "orderByFields": "localidad_ ASC",
        "f": "json"
    }

    respuesta = requests.get(
        API_URL,
        params=parametros,
        timeout=30
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    if "error" in datos:
        raise Exception(datos["error"])

    localidades = []

    for registro in datos.get("features", []):
        localidad = registro.get("attributes", {}).get("localidad_")

        if localidad and localidad not in localidades:
            localidades.append(localidad)

    return localidades


@app.route("/")
def inicio():

    try:
        localidades = obtener_localidades()

        return render_template(
            "index.html",
            localidades=localidades
        )

    except Exception as error:

        return f"""
        <h1>Error al obtener las localidades</h1>
        <p>{error}</p>
        """


@app.route("/paraderos")
def paraderos():

    localidad = request.args.get("localidad", "")

    parametros = {
        "where": f"localidad_ = '{localidad}'",
        "outFields": "cenefa_par,nombre_par,direccion_,localidad_,latitud_pa,longitud_p",
        "returnGeometry": "false",
        "f": "json",
        "resultRecordCount": 2000
    }

    try:

        respuesta = requests.get(
            API_URL,
            params=parametros,
            timeout=30
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        if "error" in datos:
            return f"""
            <h1>Error del servicio SITP</h1>
            <p>{datos["error"]}</p>
            """

        paraderos_data = []

        for registro in datos.get("features", []):

            atributos = registro.get("attributes", {})

            paraderos_data.append({
                "codigo": atributos.get("cenefa_par", ""),
                "nombre": atributos.get("nombre_par", ""),
                "direccion": atributos.get("direccion_", ""),
                "localidad": atributos.get("localidad_", ""),
                "latitud": atributos.get("latitud_pa", ""),
                "longitud": atributos.get("longitud_p", "")
            })

        return render_template(
            "paraderos.html",
            localidad=localidad,
            paraderos=paraderos_data,
            total=len(paraderos_data)
        )

    except requests.RequestException as error:

        return f"""
        <h1>Error al consultar los datos del SITP</h1>
        <p>{error}</p>
        """


if __name__ == "__main__":
    app.run(debug=True)
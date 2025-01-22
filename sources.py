from flask import Flask, request, render_template_string,jsonify
from templates import templates
import json
app = Flask(__name__)
from flask import Flask, render_template, make_response



@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Obtener parámetros de la solicitud
    data = request.get_json()
    data = json.loads(data)
    title = request.args.get('title', 'Default Title')
    content = request.args.get('content', 'Default Content')

    # Crear una plantilla HTML para la página


    # Renderizar HTML con los parámetros
    rendered_html = render_template_string(templates["solicitudMantenimiento"],data=data, title=title, content=content)

    # Devolver el HTML como respuesta
    return rendered_html
@app.route('/pdf')
def generar_pdf():
    # Definir las URLs de los logos
    logo_institucion_url = "https://hospitalsanrafael.gov.co/wp-content/uploads/2021/09/LOGO-horizontal.png"
    foto_equipo_url = "https://http2.mlstatic.com/D_NQ_NP_832955-MCO44668577828_012021-O.webp"

    # Datos a pasar a la plantilla
    data = {
        'logo_institucion': logo_institucion_url,
        'foto_equipo': foto_equipo_url,
        'equipo': 'Equipo ABC',
        'marca': 'Marca X',
        'modelo': 'Modelo Y',
        'serie': '12345',
        'inv_act': 'Activo',
        'servicio': 'Servicio Z',
        'ubicacion': 'Ubicación 1',
        'registro_sanitario': 'RS12345',
        'vida_util': '10 años',
        'tipo_equipo': 'Tipo 1',
        'fuente_alimentacion': 'AC',
        'voltaje_max': '220V',
        'voltaje_min': '110V',
        'potencia': '100W',
        'frecuencia': '50Hz',
        'corriente_max': '10A',
        'corriente_min': '5A',
        'temperatura': '25°C',
        'presion': '1 atm',
        'peso': '10kg',
        'forma_adquisicion': 'Compra',
        'fabricante': 'Fabricante ABC',
        'fecha_compra': '2023-01-01',
        'fecha_operacion': '2023-02-01',
        'vencimiento_garantia': '2025-01-01',
        'requiere_mantenimiento': True,
        'requiere_calibracion': False,
        'periodicidad_calibracion': 'Anual',
        'accesorios': [
            {'item': 'Accesorio 1', 'descripcion': 'Descripción 1', 'cantidad': 5},
            {'item': 'Accesorio 2', 'descripcion': 'Descripción 2', 'cantidad': 3},
        ],
        'historial': [
            {'fecha': '2023-02-01', 'reporte': 'Reporte 1', 'actividad': 'Mantenimiento', 'repuestos': 'Repuesto 1', 'hh': 2, 'hp': 3, 'observaciones': 'Observación 1', 'firma': 'Firma 1'},
            {'fecha': '2023-03-01', 'reporte': 'Reporte 2', 'actividad': 'Reparación', 'repuestos': 'Repuesto 2', 'hh': 1, 'hp': 1, 'observaciones': 'Observación 2', 'firma': 'Firma 2'},
        ],
        'fecha_actual': '2025-01-21'
    }

    # Renderizar la plantilla HTML
    html_output = render_template('plantilla.html', data=data)

    # Convertir HTML a PDF
    pdf_output = pdfkit.from_string(html_output, False)  # False para obtener el PDF en memoria

    # Crear una respuesta con el PDF
    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Hoja_de_Vida_Equipo.pdf'
    return response

@app.route('/html')
def generar_html():
    # Definir las URLs de los logos
    logo_institucion_url = "https://hospitalsanrafael.gov.co/wp-content/uploads/2021/09/LOGO-horizontal.png"
    foto_equipo_url = "https://http2.mlstatic.com/D_NQ_NP_832955-MCO44668577828_012021-O.webp"

    # Datos a pasar a la plantilla
    data = {
        'logo_institucion': logo_institucion_url,
        'foto_equipo': foto_equipo_url,
        'equipo': 'Equipo ABC',
        'marca': 'Marca X',
        'modelo': 'Modelo Y',
        'serie': '12345',
        'inv_act': 'Activo',
        'servicio': 'Servicio Z',
        'ubicacion': 'Ubicación 1',
        'registro_sanitario': 'RS12345',
        'vida_util': '10 años',
        'tipo_equipo': 'Tipo 1',
        'fuente_alimentacion': 'AC',
        'voltaje_max': '220V',
        'voltaje_min': '110V',
        'potencia': '100W',
        'frecuencia': '50Hz',
        'corriente_max': '10A',
        'corriente_min': '5A',
        'temperatura': '25°C',
        'presion': '1 atm',
        'peso': '10kg',
        'forma_adquisicion': 'Compra',
        'fabricante': 'Fabricante ABC',
        'fecha_compra': '2023-01-01',
        'fecha_operacion': '2023-02-01',
        'vencimiento_garantia': '2025-01-01',
        'requiere_mantenimiento': True,
        'requiere_calibracion': False,
        'periodicidad_calibracion': 'Anual',
        'accesorios': [
            {'item': 'Accesorio 1', 'descripcion': 'Descripción 1', 'cantidad': 5},
            {'item': 'Accesorio 2', 'descripcion': 'Descripción 2', 'cantidad': 3},
        ],
        'historial': [
            {'fecha': '2023-02-01', 'reporte': 'Reporte 1', 'actividad': 'Mantenimiento', 'repuestos': 'Repuesto 1', 'hh': 2, 'hp': 3, 'observaciones': 'Observación 1', 'firma': 'Firma 1'},
            {'fecha': '2023-03-01', 'reporte': 'Reporte 2', 'actividad': 'Reparación', 'repuestos': 'Repuesto 2', 'hh': 1, 'hp': 1, 'observaciones': 'Observación 2', 'firma': 'Firma 2'},
        ],
        'fecha_actual': '2025-01-21'
    }

    # Renderizar la plantilla HTML
    html_output = render_template_string(templates["hojaDeVida"], data=data)
    
    return html_output
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True) 
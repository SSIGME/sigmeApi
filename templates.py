templates={
    "hojaDeVida":"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hoja de Vida del Equipo</title>
    <style>
        body { font-family: 'Poppins', sans-serif; margin: 0; padding: 0; background-color: #eef1f5; color: #333; }
        .container { max-width: 1000px; margin: 40px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 4px 20px rgba(0,0,0,0.1); }
        .header { display: flex; justify-content: space-between; align-items: center;  border-bottom: 3px solid #003e80; }
        .header h1 {  font-size: 28px; text-transform: uppercase; margin: 0; }
        .logo img { max-height: 80px; }
        .content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }
        .identificacion { display: flex; gap: 20px; align-items: center; }
        .foto-equipo { margin-left: 10%;max-width: 200px; margin-right: 10%; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
        h2 { width: 100% ;color: #023970; border-bottom: 2px solid #00152c7c; padding-bottom: 5px; margin-top: 20px; }
        p { font-size: 16px; line-height: 1.6; }
        table { width: 80%; border-collapse: collapse; margin-top: 20px; border-radius: 10px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; }
        th { background-color:   #011652; color: white; }
        td { background-color: #f2f2f2; }
        h1{  padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px; background: linear-gradient(135deg, #050259, #0056b3); color: azure;}
        .footer { text-align: center; margin-top: 30px; padding: 30px;  background: linear-gradient(135deg, #050259, #0056b3); color: white; border-radius: 5px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header with Logo and Title -->
        <div class="header">
            <div class="logo">
                <img src="{{ data.logo_institucion }}" alt="Logo de la Institución">
            </div>
            <h1>Hoja de Vida del Equipo Hospitalario</h1>
        </div>
        <h2>Identificación del Equipo</h2>
        <!-- Identificación del Equipo -->
        <div class="identificacion">
            <img class="foto-equipo" src="{{ data.foto_equipo }}" alt="Foto del Equipo">
          
            <div class="content">
                
                <p><strong>Equipo:</strong> {{ data.equipo }}</p>
                <p><strong>Marca:</strong> {{ data.marca }}</p>
                <p><strong>Modelo:</strong> {{ data.modelo }}</p>
                <p><strong>Serie:</strong> {{ data.serie }}</p>
                <p><strong>Inventario/Activo:</strong> {{ data.inv_act }}</p>
                <p><strong>Servicio:</strong> {{ data.servicio }}</p>
                <p><strong>Ubicación:</strong> {{ data.ubicacion }}</p>
                <p><strong>Registro Sanitario:</strong> {{ data.registro_sanitario }}</p>
                <p><strong>Vida Útil:</strong> {{ data.vida_util }}</p>
                <p><strong>Tipo de Equipo:</strong> {{ data.tipo_equipo }}</p>
            </div>
        </div>

        <h2>Detalles Técnicos</h2>
        <!-- Detalles Técnicos -->
        <div class="content">
            <p><strong>Fuente de Alimentación:</strong> {{ data.fuente_alimentacion }}</p>
            <p><strong>Voltaje Máximo:</strong> {{ data.voltaje_max }}</p>
            <p><strong>Voltaje Mínimo:</strong> {{ data.voltaje_min }}</p>
            <p><strong>Potencia:</strong> {{ data.potencia }}</p>
            <p><strong>Frecuencia:</strong> {{ data.frecuencia }}</p>
            <p><strong>Corriente Máxima:</strong> {{ data.corriente_max }}</p>
            <p><strong>Corriente Mínima:</strong> {{ data.corriente_min }}</p>
            <p><strong>Temperatura:</strong> {{ data.temperatura }}</p>
            <p><strong>Presión:</strong> {{ data.presion }}</p>
            <p><strong>Peso:</strong> {{ data.peso }}</p>
        </div>

        <!-- Datos de Adquisición -->
        <h2>Datos de Adquisición</h2>
        <div class="content">
            <p><strong>Forma de Adquisición:</strong> {{ data.forma_adquisicion }}</p>
            <p><strong>Fabricante:</strong> {{ data.fabricante }}</p>
            <p><strong>Fecha de Compra:</strong> {{ data.fecha_compra }}</p>
            <p><strong>Fecha de Operación:</strong> {{ data.fecha_operacion }}</p>
            <p><strong>Vencimiento de Garantía:</strong> {{ data.vencimiento_garantia }}</p>
        </div>

        <!-- Mantenimiento y Calibración -->
        <h2>Mantenimiento y Calibración</h2>
        <div class="content">
            <p><strong>Requiere Mantenimiento:</strong> {{ "Sí" if data.requiere_mantenimiento else "No" }}</p>
            <p><strong>Requiere Calibración:</strong> {{ "Sí" if data.requiere_calibracion else "No" }}</p>
            <p><strong>Periodicidad de Calibración:</strong> {{ data.periodicidad_calibracion }}</p>
        </div>
        <!-- Registro de Accesorios y Componentes -->
        <h2>Registro de Accesorios y Componentes</h2>
        <table>
            <tr>
                <th>Item</th>
                <th>Descripción</th>
                <th>Cantidad</th>
            </tr>
            {% for accesorio in data.accesorios %}
            <tr>
                <td>{{ accesorio.item }}</td>
                <td>{{ accesorio.descripcion }}</td>
                <td>{{ accesorio.cantidad }}</td>
            </tr>
            {% endfor %}
        </table>
        <!-- Registro Histórico -->
        <h2>Registro Histórico del Equipo</h2>
        <table>
            <tr>
                <th>Fecha</th>
                <th>Reporte</th>
                <th>Actividad</th>
                <th>Repuestos</th>
                <th>(H.H)</th>
                <th>(H.P)</th>
                <th>Observaciones</th>
                <th>Firma Responsable</th>
            </tr>
            {% for registro in data.historial %}
            <tr>
                <td>{{ registro.fecha }}</td>
                <td>{{ registro.reporte }}</td>
                <td>{{ registro.actividad }}</td>
                <td>{{ registro.repuestos }}</td>
                <td>{{ registro.hh }}</td>
                <td>{{ registro.hp }}</td>
                <td>{{ registro.observaciones }}</td>
                <td>{{ registro.firma }}</td>
            </tr>
            {% endfor %}
        </table>



        <!-- Footer -->
        <div class="footer">
            <p>Documento generado por SIGME el - {{ data.fecha_actual }}</p>
        </div>
    </div>
</body>
</html>


""",
    "solicitudMantenimiento":
        
        """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formato Solicitud de Mantenimiento</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #eef2f7;
            color: #333;
        }
            h2 {
            font-size: 14px;
            font-weight: 300;
        }
        .container {
            max-width: 900px;
            margin: 0px auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #050259, #0056b3);
            color: #fff;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 22px;
        }
        .header p {
            margin: 5px 0 0;
            font-size: 14px;
            opacity: 0.85;
        }
        .section {
            padding: 15px;
            border-bottom: 1px solid #08356b;
        }
        .section-title {
            font-size: 16px;
            color: #0056b3;
            font-weight: bold;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 8px 12px;
            text-align: left;
            border: 1px solid #c6d5e6;
            font-size: 14px;
        }
        table th {
            background: #e3f1ff;
            font-weight: bold;
        }
        table td {
            background: #fff;
        }
        .checkbox-container {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .checkbox-container input {
            width: 16px;
            height: 16px;
            margin: 0;
        }
        .signature-section {
            display: flex;
            flex-direction: column;
            padding: 15px;
            gap: 15px;
        }
        .signature {
            flex: 1;
            border-top: 2px solid #0056b3;
            padding-top: 10px;
            text-align: center;
        }
        .signature span {
            display: block;
            margin-top: 5px;
            color: #666;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                box-shadow: none;
            }
            .header {
                padding: 15px;
            }
            .section {
                padding: 10px;
            }
            table th, table td {
                font-size: 12px;
                padding: 6px;
            }
            .section-title {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Sistema Integrado de Gestión</h1>
            <h2>Formato Solicitud de Mantenimiento Hospitalario</h2>
        </div>

        <!-- General Information Section -->
        <div class="section">
            <div class="section-title">Información General</div>
            <table>
                <tr>
                    <th>Fecha de Solicitud</th>
                    <td>{{ data.fecha }}</td>
                </tr>
                <tr>
                    <th>Hora</th>
                    <td>{{ data.hora }}</td>
                </tr>
                <tr>
                    <th>Solicitante</th>
                    <td>{{ data.solicitante }}</td>
                </tr>
                <tr>
                    <th>Área</th>
                    <td>{{ data.area }}</td>
                </tr>
            </table>
        </div>
    <div class="section">
            <div class="section-title">Información del Equipo</div>
            <table>
                <tr>
                    <th>Equipo o Concepto</th>
                    <td>{{ data.tipo }}</td>
                             </tr>
                          <tr>
                    <th>Marca</th>
                    <td>{{ data.marca }}</td>
                </tr>
                <tr>
                    <th>Modelo</th>
                    <td>{{ data.modelo }}</td>
                         </tr>
                          <tr>
                    <th>Referencia</th>
                    <td>{{ data.serie }}</td>
                </tr>
            </table>
        </div>
        <!-- Maintenance Section -->
        <div class="section">
            <div class="section-title">Mantenimiento</div>
            <table>
                <tr>
                    <th>Equipo Biomédico</th>
                    <td><input type="checkbox" checked></td>
                </tr>
                <tr>
                    <th>Equipo de Cómputo</th>
                    <td><input type="checkbox" disabled></td>
                </tr>
                <tr>
                    <th>Equipo Industrial</th>
                    <td><input type="checkbox" disabled></td>
                </tr>
                <tr>
                    <th>Infraestructura</th>
                    <td><input type="checkbox"  disabled></td>
                </tr>
            </table>
        </div>

        <!-- More Sections -->
        <div class="section">
            <div class="section-title">Mantenimiento Solicitado</div>
            <table>
                <tr>
                    <th>Preventivo</th>
                    <td><input type="checkbox" disabled></td>
                </tr>
                <tr>
                    <th>Correctivo</th>
                    <td><input type="checkbox"  checked></td>
                </tr>
            </table>
        </div>

    <div class="section">
            <div class="section-title">Descripción del Problema</div>
            <table>
                <tr>
                    <th>Descripción</th>
                </tr>
                <tr>
                    <td>{{ data.descripcionProblema }}</td>
                </tr>
            </table>
             <table>
                     <tr>
    <th>Es la primera ve que ocurre</th>
    <td>
        {% if data.esPrimeraVez %}
            Sí
        {% else %}
            No
        {% endif %}
    </td>
</tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Detalles del Impacto</div>
            <table>
                <tr>
                    <th>Equipo Fuera de Servicio</th>
                    <td>{{ data.equipoFueraServicio }}</td>
                </tr>
                <tr>
                    <th>Funciones Afectadas</th>
                    <td>{{ data.funcionesAfectadas }}</td>
             <tr>
    <th>Afecta la seguridad del paciente o del personal:</th>
    <td>
        {% if data.afectaSeguridad %}
            Sí
        {% else %}
            No
        {% endif %}
    </td>
</tr>

            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Ubicación y Condiciones</div>
            <table>
                <tr>
                    <th>Cambio Reciente de Ubicación</th>
               
                        <td>
        {% if data.cambioRecienteUbicacion %}
            Sí
        {% else %}
            No
        {% endif %}
    </td>
                </tr>
                <tr>
                    <th>Exposición a Condiciones Especiales</th>
                    <td>{{ data.exposicionCondiciones}}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Uso y Frecuencia</div>
            <table>
                <tr>
                    <th>Frecuencia de Uso</th>
                    <td>{{ data.frecuenciaUso }}</td>
                </tr>
                <tr>
                    <th>Uso Intensivo</th>
           
                               <td>
        {% if data.usoIntensivo %}
            Sí
        {% else %}
            No
        {% endif %}
    </td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Alertas y Señales</div>
            <table>
                <tr>
                    <th>Mensaje de Error</th>
                    <td>{{ data.mensajeError }}</td>
                </tr>
                <tr>
                    <th>Señal de Alarma</th>
                    <td>{{ data.senalAlarma }}</td>
                </tr>
                <tr>
                    <th>Sonido Inusual</th>
                    <td>{{ data.sonidoInusual }}</td>
                </tr>
            </table>
        </div>
    </div>
    </div>
    
</body>
</html>


"""
}
from flask import Flask, request, jsonify
from flask_cors import CORS
import xmlrpc.client
import base64
from datetime import datetime

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir solicitudes desde el frontend

# Conexión con Odoo
url = 'https://fiberpro-4-12-24-16870849.dev.odoo.com/'
db = 'fiberpro-2-12-2024-16837403'
username = 'z.barreto@fiberpro.com.pe'
password = 'ae6cd458ff84c2774a628a3fb3bd3c14edd310a1'

# Conexión a Odoo usando XML-RPC
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = 213
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Función para validar las fechas (en formato YYYY-MM-DD)
def validate_date(date_str):
    if not date_str:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None  # Si no es una fecha válida, devolvemos None

@app.route('/api/reclamos/quejas', methods=['POST'])
def crear_queja():
    data = request.json

    # Validar las fechas
    fecha_fields = [
        'fechaNacimiento', 'fechaVencimiento', 'fechaPresentacionQueja',
        'fechaNegativaQueja', 'fechaSuspendioServicioQueja',
        'fechaEmisionCartaApelacion', 'fechaEmisionApelacionSiCuatro',
        'fechaVencimientoApelacionSiCuatro', 'fechaEmisionApelacionSiCinco',
    ]
    for field in fecha_fields:
        if field in data:
            data[field] = validate_date(data[field])

    # Validación de campos requeridos
    required_fields = [
        'tipoUsuarioSeleccionado', 'selectQueja', 'empresaOperadoraQueja',
        'servicioObjetoQueja', 'numServicioQueja', 'codigoNumeroQueja',
        'negativaQueja', 'canalPresentacion', 'especificarCanalQuejaDos',
        'adjuntaPrueba', 'MediosCobranzasQuejas', 'constanciaPagoQueja',
        'pagoCuentaQueja', 'espeficiarQueja', 'apelacin', 'empresaOperadoraApelacion',
        'servicioMateriaApelacion', 'numeroServicioApelacion', 'codigoNumeroApelacion',
        'numeroCartaApelacion', 'detallePruebaApelacionUno', 'detallefsApelacionDos',
        'materiaEmpresaApelacionTres', 'apelacionopcioncuatro', 'numeroReciboApelacionSiCuatro',
        'montoReclamadoApelacionSiCuatro', 'detalleReclamoApelacionSiCuatro', 'apelacionOpcioncinco',
        'numeroReciboApelacionSiCinco', 'montoTotalApelacionSiCinco', 'detalleReclamoApelacionSiCinco',
        'materiaEmpresaEmitirApelacionSeis', 'informacionNecesariaApelacion', 'sustentoApelacion'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Incluir los datos personales en los datos de la queja
    ticket_data = {
        'state': "draft",
        'tipo_de_usuario_qja': data.get('tipoUsuarioSeleccionado'),
        'nombre_del_padre_abonado_qja': data.get('nombrePadre'),
        'nombre_de_la_madre_abonado_qja': data.get('nombreMadre'),
        'lugar_de_nacimiento_abonado_qja': data.get('lugarNacimiento'),
        'fecha_de_nacimiento_abonado_qja': data.get('fechaNacimiento'),
        'fecha_vencimiento_del_recibo_usuario_qja': data.get('fechaVencimiento'),
        'monto_de_tarifa_usuario_qja': data.get('montoTarifa'),
        'direccion_de_facturacion_usuario_qja': data.get('direccionFacturacion'),
        'nombre_cliente_qja': data.get('nombre'),
        'apellidos_qja': data.get('apellidos'),
        'relacion_familiar_qja': data.get('relacion'),
        'razon_social_qja': data.get('razonSocial'),
        'carta_de_poder_qja': data.get('cartaPoder'),
        'nro_contacto_qja': data.get('numeroContacto'),
        'tipo_doc_qja': data.get('tipoDoc'),
        'nro_documento_qja': data.get('numDoc'),
        'distrito_cliente_qja': data.get('distritos'),
        'direccion_cliente_qja': data.get('direccion'),
        'correo_electronico_qja': data.get('correo'),
        'notificacion_por_correo_electronico_qja': data.get('autoriza'),
        'queja': data.get('selectQueja'),
        'empresa_operadora_ds1': data.get('empresaOperadoraQueja'),
        'servicio_objeto_queja_dsq': data.get('servicioObjetoQueja'),
        'nmero_servicio_reclamado_dsq': data.get('numServicioQueja'),
        'cdigo_nmero_reclamo_dsq': data.get('codigoNumeroQueja'),
        'fecha_presentacin_reclamo_queja_uno': data.get('fechaPresentacionQueja'),
        'negativa_relacionada_queja_dos': data.get('negativaQueja'),
        'char_field_2bo_1ibhijmmb': data.get('fechaNegativaQueja'),
        'canal_presentacin_reclamo_queja_dos': data.get('canalPresentacion'),
        'canal_especificado_queja_dos': data.get('especificarCanalQuejaDos'),
        'fecha_en_la_cual_se_habra_suspendido_el_servicio': data.get('fechaSuspendioServicioQueja'),
        'medio_de_cobranza_queja_cuatro': data.get('MediosCobranzasQuejas'),
        'documento_queja': data.get('constanciaPagoMedioCobranza'),
        'lugar_donde_permiti_pago_cinco': data.get('pagoCuentaQueja'),
        'especificar_quejas': data.get('espeficiarQueja'),
        'informacion_necesaria_queja': data.get('informacionNecesariaQueja'),
        'descripcion_problema_queja': data.get('descripcionProblemaQueja'),
    }

    # Eliminar claves con valores None
    ticket_data = {key: value for key, value in ticket_data.items() if value is not None}

    try:
        # Crear el ticket en Odoo para la queja
        ticket_id_queja = models.execute_kw(db, uid, password, 'quejasfp', 'create', [ticket_data])
        ticket_name_queja = models.execute_kw(db, uid, password, 'quejasfp', 'read', [ticket_id_queja], {'fields': ['name']})

        return jsonify({'ticket_id': ticket_id_queja, 'ticket_name': ticket_name_queja[0]['name'], 'success': True})
    except Exception as e:
        return jsonify({"error": "Error creating ticket: " + str(e)}), 400
    
@app.route('/api/reclamos/apelaciones', methods=['POST'])
def crear_apelacion():
    data = request.json
    file_base64 = data.get('fileBase64')

    # Validar las fechas
    fecha_fields = [
        'fechaNacimiento', 'fechaVencimiento', 'fechaPresentacionQueja',
        'fechaNegativaQueja', 'fechaSuspendioServicioQueja',
        'fechaEmisionCartaApelacion', 'fechaEmisionApelacionSiCuatro',
        'fechaVencimientoApelacionSiCuatro', 'fechaEmisionApelacionSiCinco',
    ]
    for field in fecha_fields:
        if field in data:
            data[field] = validate_date(data[field])

    # Validación de campos requeridos
    required_fields = [
        'tipoUsuarioSeleccionado', 'apelacin', 'empresaOperadoraApelacion',
        'servicioMateriaApelacion', 'numeroServicioApelacion', 'codigoNumeroApelacion',
        'numeroCartaApelacion', 'detallePruebaApelacionUno', 'detallefsApelacionDos',
        'materiaEmpresaApelacionTres', 'apelacionopcioncuatro', 'numeroReciboApelacionSiCuatro',
        'montoReclamadoApelacionSiCuatro', 'detalleReclamoApelacionSiCuatro', 'apelacionOpcioncinco',
        'numeroReciboApelacionSiCinco', 'montoTotalApelacionSiCinco', 'detalleReclamoApelacionSiCinco',
        'materiaEmpresaEmitirApelacionSeis', 'informacionNecesariaApelacion', 'sustentoApelacion'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Incluir los datos personales en los datos de la apelación
    ticket_data = {
        'state': "draft",
        'tipo_de_usuario_ape': data.get('tipoUsuarioSeleccionado'),
        'nombre_del_padre_abonado_ape': data.get('nombrePadre'),
        'nombre_de_la_madre_abonado_ape': data.get('nombreMadre'),
        'lugar_de_nacimiento_abonado_ape': data.get('lugarNacimiento'),
        'fecha_de_nacimiento_abonado_ape': data.get('fechaNacimiento'),
        'fecha_vencimiento_del_recibo_usuario_ape': data.get('fechaVencimiento'),
        'monto_de_tarifa_usuario_ape': data.get('montoTarifa'),
        'direccion_de_facturacion_usuario_ape': data.get('direccionFacturacion'),
        'nombre_cliente_ape': data.get('nombre'),
        'apellidos_ape': data.get('apellidos'),
        'relacion_familiar_ape': data.get('relacion'),
        'razon_social_ape': data.get('razonSocial'),
        'carta_de_poder_ape': file_base64,
        'nro_contacto_ape': data.get('numeroContacto'),
        'tipo_doc_ape': data.get('tipoDoc'),
        'nro_documento_ape': data.get('numDoc'),
        'distrito_cliente_ape': data.get('distritos'),
        'direccion_cliente_ape': data.get('direccion'),
        'correo_electronico_ape': data.get('correo'),
        'notificacion_por_correo_electronico_ape': data.get('autoriza'),
        'apelacin': data.get('apelacin'),
        'empresa_operadora_ds': data.get('empresaOperadoraApelacion'),
        'servicio_materia_de_apelacin_ds': data.get('servicioMateriaApelacion'),
        'nmero_servicio_reclamado_ds': data.get('numeroServicioApelacion'),
        'cdigo_nmero_reclamo_ds': data.get('codigoNumeroApelacion'),
        'nmero_carta_resuelve_reclamo_ds': data.get('numeroCartaApelacion'),
        'fecha_emisin_carta_ds': data.get('fechaEmisionCartaApelacion'),
        'detalle_pruebas_apelacion_uno': data.get('detallePruebaApelacionUno'),
        'detalle_falta_sustentacion_apelacion_dos': data.get('detallefsApelacionDos'),
        'materia_empresa_comunicarse': data.get('materiaEmpresaApelacionTres'),
        'respuesta_empresa_apelacion_cuatro': data.get('apelacionopcioncuatro'),
        'numero_recibo_apelacion_cinco': data.get('numeroReciboApelacionSiCuatro'),
        'fecha_de_emision': data.get('fechaEmisionApelacionSiCuatro'),
        'fecha_de_vencimiento': data.get('fechaVencimientoApelacionSiCuatro'),
        'pronunciamiento_empresa_ape_cuatro': data.get('detalleReclamoApelacionSiCuatro'),
        'falto_acoger_ape_cinco': data.get('apelacionOpcioncinco'),
        'nmero_recibo_apleacion_cinco': data.get('numeroReciboApelacionSiCinco'),
        'fecha_de_emisin_1': data.get('fechaEmisionApelacionSiCinco'),
        'monto_total_corresponde_cinco': data.get('montoTotalApelacionSiCinco'),
        'detalle_extremo_apelacion_cinco': data.get('detalleReclamoApelacionSiCinco'),
        'materia_cual_empresa_ape_seis': data.get('materiaEmpresaEmitirApelacionSeis'),
        'informacin_necesaria_apelacion': data.get('informacionNecesariaApelacion'),
        'sustento_de_apelacin': data.get('sustentoApelacion'),
    }

    # Eliminar claves con valores None
    ticket_data = {key: value for key, value in ticket_data.items() if value is not None}

    try:
        # Crear el ticket en Odoo para la apelación
        ticket_id_ape = models.execute_kw(db, uid, password, 'apelacionfp', 'create', [ticket_data])
        ticket_name_ape = models.execute_kw(db, uid, password, 'apelacionfp', 'read', [ticket_id_ape], {'fields': ['name']})

        return jsonify({'ticket_id': ticket_id_ape, 'ticket_name': ticket_name_ape[0]['name'], 'success': True})
    except Exception as e:
        return jsonify({"error": "Error creating ticket: " + str(e)}), 400

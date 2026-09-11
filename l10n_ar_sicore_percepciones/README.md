# SICORE Percepciones IVA (RG 5329)

Reporte contable y exportable SICORE para las percepciones de IVA de la
RG 5329/2023 (**impuesto 767**, **régimen 602**, **operación 2**).

La localización de Odoo solo trae el SICORE de retenciones de ganancias
(impuesto 217, operación 1), que se arma sobre las retenciones registradas en
los pagos. Las percepciones viven en las líneas de impuesto de los comprobantes
de venta y no las contempla.

## Qué agrega

- Reporte **SICORE Percepciones IVA (AR)**, variante del reporte de impuestos
  genérico, con una línea que suma las percepciones del período.
- Dos botones en el menú de acciones del reporte:
  - **TXT SICORE Percepciones** → `sicoreim.txt`, 198 caracteres por renglón.
  - **TXT SICORE Sujetos** → `sicoresu.txt`, 83 caracteres por renglón.

## Configuración

El impuesto de percepción tiene que tener cargado **Código de ARCA = 602**
(pestaña de definición del impuesto). Es lo único que hay que configurar: tanto
la línea del reporte como el exportable se apoyan en ese código.

## Qué toma

Facturas, notas de débito y notas de crédito de cliente del período del reporte,
registradas, con una línea del impuesto de percepción. Por defecto solo las
autorizadas por ARCA (con CAE). Respeta los filtros de fecha, de asientos
registrados y de compañías del propio reporte.

## Diseño de registro

`sicoreim.txt` — 21 campos, 198 caracteres:

| # | Campo | Pos | Len | Valor |
|---|---|---|---|---|
| 1 | Código de comprobante | 0 | 2 | `01` Factura / `03` NC / `04` ND |
| 2 | Fecha del comprobante | 2 | 10 | dd/mm/aaaa |
| 3 | Número de comprobante | 12 | 16 | PV + número |
| 4 | Importe del comprobante | 28 | 16 | total del comprobante |
| 5 | Código de impuesto | 44 | 4 | `0767` |
| 6 | Código de régimen | 48 | 3 | `602` |
| 7 | Código de operación | 51 | 1 | `2` |
| 8 | Base de cálculo | 52 | 14 | neto gravado |
| 9 | Fecha de la percepción | 66 | 10 | = fecha del comprobante |
| 10 | Código de condición | 76 | 2 | `13` alícuota general |
| 11 | Sujeto suspendido | 78 | 1 | `0` |
| 12 | Importe percibido | 79 | 14 | 3% de la base |
| 13 | Porcentaje de exclusión | 93 | 6 | `0,00` |
| 14 | Fecha boletín | 99 | 10 | blancos |
| 15 | Tipo de documento | 109 | 2 | `80` (CUIT) |
| 16 | Número de documento | 111 | 20 | CUIT |
| 17 | Nro. certificado original | 131 | 14 | ceros |
| 18 | Denominación del ordenante | 145 | 30 | blancos |
| 19 | Acrecentamiento | 175 | 1 | `0` |
| 20 | CUIT país del retenido | 176 | 11 | ceros |
| 21 | CUIT del ordenante | 187 | 11 | ceros |

`sicoresu.txt` — CUIT (11) + denominación (20) + domicilio (20) + localidad (20)
+ código postal (10) + tipo de documento (2).

Importes con coma decimal, sin separador de miles. Codificación latin-1,
renglones terminados en CRLF.

## Constantes

Al principio de `models/account_report_handler.py`:

- `COD_CONDICION` — `13` alícuota general. Usar `14` si se percibe 1,5% sobre
  ventas gravadas al 10,5%.
- `BASE_NOTA_CREDITO` — `percepcion` replica el criterio del sistema anterior
  (base = importe percibido). `neto` usa el neto gravado, que es lo que dice el
  instructivo.
- `SOLO_AUTORIZADOS` — filtra por comprobantes con CAE.
- `ESTRICTO` — corta con un error si algún comprobante no se puede exportar
  (sin CUIT válido, sin fecha, tipo de documento sin equivalente SICORE) en vez
  de omitirlo en silencio.

## Referencias

- RG 5329/2023 — régimen de percepción de IVA sobre alimentos, bebidas y
  artículos de higiene y limpieza.
- RG 2233 (SICORE) — instructivo y diseños de registro.

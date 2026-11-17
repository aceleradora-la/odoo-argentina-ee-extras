# Bloquear pasar a borrador comprobantes validados en ARCA

Impide **Restablecer a borrador** en facturas, notas de crédito y notas de
débito electrónicas que ya fueron autorizadas por ARCA. Un comprobante con CAE
no se puede modificar en ARCA: si hay que corregir datos fiscales, se emite la
nota de crédito o débito que corresponda.

Compatible con Odoo **18.0 en adelante** (el mismo código corre en 18.0 y 19.0;
solo cambia la versión del manifiesto en cada rama).

## Por qué hace falta

`l10n_ar_edi` (Enterprise) ya oculta el botón en los comprobantes con CAE, pero
`l10n_ar_edi_ux` (ADHOC) lo anula a propósito con un *monkey patch* sobre
`_compute_show_reset_to_draft_button`, para dejar corregir facturas con
problemas de secuencia (ticket ADHOC 76633). Además, ocultar el botón no impide
llamar a `button_draft` por otro camino. Este módulo vuelve a ocultar el botón y
además bloquea la operación en el servidor.

## Qué hace

| Acción sobre un comprobante con CAE | Usuario común | Grupo autorizado |
|---|---|---|
| Ver el botón **Restablecer a borrador** | No | Sí |
| Pasar a borrador (botón, RPC, otro módulo) | Error | Sí, con nota en el chatter |
| Cancelar | Error | Error |
| Eliminar (una vez en borrador) | Error | Error |

Cuando un usuario autorizado pasa un comprobante a borrador, queda un mensaje
en el chatter con el CAE y la advertencia de no tocar cliente, fecha, importes
ni impuestos: al volver a confirmarlo, ARCA no se entera de esos cambios.

## Grupo autorizado

**Restablecer a borrador comprobantes validados en ARCA**
(`l10n_ar_edi_block_draft.group_arca_reset_draft`).

Está pensado para una o dos personas de administración, para corregir lo que
no se informa a ARCA:

- cuenta contable de las líneas;
- analítica;
- producto, descripción, cantidad o unidad (WSFE no recibe el detalle de ítems);
- vendedor, término de pago, referencia, dirección de entrega, notas;
- numeración en Odoo desfasada respecto de la autorizada por ARCA.

Para asignarlo: activar el modo desarrollador, ir a **Ajustes → Usuarios y
compañías → Grupos**, abrir el grupo y agregar los usuarios. El grupo no tiene
categoría (en 19.0 el campo cambió de `category_id` a `privilege_id`), así que
esta ruta funciona igual en las dos versiones.

## Qué se considera "validado en ARCA"

El comprobante tiene que cumplir las dos condiciones:

- su diario es un punto de venta electrónico (`journal_id.l10n_ar_afip_ws`
  cargado: WSFE, WSFEX, WSBFE, etc.);
- tiene código de autorización (`l10n_ar_afip_auth_code`, el CAE).

Quedan afuera, y se pueden seguir pasando a borrador:

- facturas de proveedor (aunque tengan cargado el CAE del proveedor, su diario
  no es un punto de venta electrónico);
- comprobantes de puntos de venta manuales o preimpresos;
- comprobantes registrados que ARCA no llegó a autorizar.

En una base de prueba (ARCA en modo homologación o validación "dummy") el
bloqueo aplica igual, porque esos comprobantes también tienen CAE.

## Cómo funciona

Sigue el mismo patrón que usa Odoo en sus localizaciones con factura
electrónica (Grecia, España):

- `_compute_show_reset_to_draft_button`: oculta el botón a los usuarios sin el
  grupo. Para los que lo tienen, lo recalcula con las reglas de `account`
  (hash, estado, cancelación pendiente) salteando la de `l10n_ar_edi`, igual
  que el patch de ADHOC; así el botón aparece esté o no instalado
  `l10n_ar_edi_ux`.
- `_check_draftable`: lo llama `button_draft` antes de pasar a borrador; ahí
  se levanta el `UserError` si el usuario no tiene el grupo.
- `button_draft`: deja la nota en el chatter.
- `button_cancel` y `_unlink_except_validated_in_arca`: bloquean cancelar y
  eliminar para todos.

## Dependencia

- `l10n_ar_edi`

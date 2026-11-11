# SYNTHEX — Documento de Requerimientos del Producto

**Versión:** 1.1  
**Estado:** MVP en desarrollo y validación  
**Tipo de documento:** Requerimientos funcionales y no funcionales

---

## 1. Descripción del proyecto

SYNTHEX busca incorporar una primera experiencia de fabricación dentro de su módulo actual de inventarios.

La solución permitirá a pequeñas y medianas empresas gestionar la transformación de materias primas y componentes en productos terminados, conectando los procesos de demanda, compras, producción e inventario.

Actualmente, estos procesos suelen gestionarse mediante hojas de cálculo o registros independientes. El objetivo es centralizar la información y ofrecer trazabilidad sobre los materiales utilizados, las cantidades producidas y los costos asociados.

## 2. Objetivo general

Diseñar y desarrollar un prototipo funcional que permita gestionar el proceso básico de fabricación de productos, desde la definición de sus componentes y recetas hasta la producción y actualización de inventarios.

La solución deberá ser intuitiva, interactiva, escalable y demostrar el uso de inteligencia artificial en una funcionalidad concreta.

## 3. Usuario objetivo

Para esta primera versión se manejará un único perfil:

**Administrador:** tendrá acceso a todos los módulos y podrá crear, consultar, modificar y gestionar la información del sistema.

La gestión de múltiples usuarios y permisos diferenciados se considera una mejora posterior.

## 4. Alcance funcional — Fase 1 (MVP)

### 4.1. Panel principal

- Visualizar indicadores generales de inventario y producción.
- Consultar órdenes de producción pendientes y terminadas.
- Identificar alertas de materiales insuficientes.
- Acceder a los módulos mediante tarjetas y navegación sencilla.

### 4.2. Catálogo de productos

- Crear productos terminados y componentes.
- Registrar código, nombre, unidad de medida, tipo y costo.
- Consultar y modificar artículos.
- Inactivar artículos que tengan movimientos históricos, evitando eliminar su trazabilidad.

### 4.3. Recetas de fabricación (BOM)

- Asociar componentes a un producto terminado.
- Definir las cantidades necesarias de cada componente.
- Calcular el costo estimado de materiales por unidad.
- Permitir modificaciones de recetas mediante nuevas versiones.
- Conservar la receta utilizada por cada orden de producción.

### 4.4. Gestión de demanda

- Registrar solicitudes de fabricación por producto y cantidad.
- Consultar las existencias disponibles de productos terminados.
- Calcular la necesidad neta de fabricación, descontando las existencias no comprometidas.
- Calcular los requerimientos de componentes según la receta.
- Identificar faltantes y determinar la cantidad máxima que puede fabricarse con los materiales disponibles.
- Permitir generar producción parcial y gestionar la cantidad pendiente.

### 4.5. Compras y recepción

- Generar solicitudes de compra para componentes faltantes.
- Consultar las cantidades solicitadas.
- Registrar la recepción de materiales.
- Actualizar el inventario únicamente cuando se confirme la recepción.
- Permitir gestionar cantidades recibidas parcialmente.

### 4.6. Órdenes de producción

- Crear órdenes de producción relacionadas con una demanda.
- Permitir órdenes parciales o totales.
- Reservar los componentes al liberar una orden.
- Registrar avances de producción.
- Registrar las cantidades reales consumidas y las unidades terminadas.
- Mantener las órdenes abiertas cuando exista producción pendiente.

### 4.7. Inventario y movimientos

- Consultar existencias físicas, reservadas y disponibles.
- Registrar entradas de compras y salidas por consumo de producción.
- Registrar entradas de productos terminados.
- Consultar el historial de movimientos.
- Mantener trazabilidad de las transacciones.

### 4.8. Costos y reportes básicos

- Calcular el costo estimado de materiales por producto.
- Calcular el costo real de materiales según el consumo registrado.
- Consultar cantidades producidas y materiales consumidos.
- Visualizar indicadores de órdenes de producción: totales, pendientes, en producción y completadas.
- Visualizar indicadores de compras: solicitudes registradas, pendientes y recibidas.
- Presentar información mediante tarjetas, tablas y gráficos.
- Consultar el detalle de consumo de componentes por orden de producción.
- Mostrar los costos estimados y reales de fabricación.
- Consultar movimientos de inventario relacionados con compras y producción.

Para el MVP, el costo de fabricación contempla materiales. No incluye mano de obra, depreciación ni costos indirect

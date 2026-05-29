---
name: ui-design-react
description: >
  Usa este skill para CUALQUIER tarea de UI en React — componentes, páginas,
  dashboards, formularios, landing pages o layouts completos. Activar cuando
  el usuario pida construir, crear, estilizar, rediseñar o mejorar cualquier
  interfaz visual en React. Aplica una estética minimalista moderna: espaciado
  generoso, tipografía con carácter, paleta de colores contenida y movimiento
  sutil. Siempre leer este skill antes de escribir cualquier código de UI.
---

## Stack
- React (componentes funcionales + hooks)
- Tailwind CSS v3
- Motion (Framer Motion) para animaciones
- Lucide React para íconos
- TypeScript cuando el proyecto lo use

---

## Dirección estética — Minimalismo Moderno

### Color
- Base: blanco roto `#F5F5F3` (claro) o casi-negro `#0A0A0A` (oscuro)
- Un único color de acento: frío y desaturado (slate, zinc o azul apagado)
- Máximo 3 colores en la paleta
- Sin gradientes de colores llamativos

### Tipografía
- Display / títulos: fuente con carácter fuerte y distintivo
  (Geist, Syne, DM Serif, Playfair — nunca Inter, Roboto ni Arial)
- Cuerpo / UI: sans limpia o monospace como par de la fuente display
- Implementar vía @import en CSS o next/font si se usa Next.js

### Espaciado y Layout
- Grid base de 8px
- Espaciado generoso — más aire del que parece necesario
- Asimetría sobre simetría rígida
- Sin border-radius exagerado (evitar botones pill por defecto)

### Sombras y Bordes
- Sombras: casi imperceptibles o ausentes (máximo `shadow-sm`)
- Bordes: 1px en color de muy bajo contraste
- Sin efectos glassmorphism

### Movimiento
- Entrada: fade + translateY, 200–300ms ease-out
- Hover: sutil y funcional — que se sienta pero no grite
- Usar Motion (Framer Motion) en React
- Una entrada bien orquestada por vista; evitar micro-interacciones dispersas

### Íconos
- Solo Lucide React
- Grosor de trazo: 1.5px
- Tamaño consistente por contexto (16px UI / 20px acciones / 24px hero)

---

## Lo que hay que evitar
- Morado o violeta como color de acento
- Sombras gruesas en cards
- Gradientes de colores llamativos
- Layouts de grilla simétrica y predecible
- Patrones genéricos de dashboard
- Glassmorphism

---

## Requisitos del entregable
- Componente(s) React listos para usar
- Variables CSS definidas en `:root` para el tema
- Responsivo mobile-first
- Comentarios solo donde la lógica no sea obvia
- Sin estilos inline — solo clases de Tailwind o CSS modules

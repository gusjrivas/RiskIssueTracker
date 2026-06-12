# Prompt 24 — Chore: incorporación de Playwright MCP para el equipo

## Contexto
Para poder verificar cambios de UI en vivo (login, formularios, badges de severidad) sin
scripts manuales, se incorporó el servidor MCP de Playwright al proyecto. Con esto Claude
Code puede manejar un navegador real: navegar, completar formularios, hacer click y sacar
screenshots — y cualquier miembro del equipo lo hereda al clonar el repo.

## Branch
`chore/add-playwright-mcp` → PR #38

## Prompts

> Nota: el prompt original es de una sesión anterior y no quedó preservado verbatim.
> El pedido fue incorporar Playwright como MCP a nivel proyecto para que todo el
> equipo pueda usar browser automation desde Claude Code.

## Implementación

Se agregó `.mcp.json` en la raíz del repo (configuración MCP **a nivel proyecto**,
versionada en git):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Uso

- Al abrir Claude Code en el repo por primera vez, aprobar el servidor MCP del proyecto
  cuando lo solicite.
- Quedan disponibles las herramientas `browser_navigate`, `browser_click`,
  `browser_fill_form`, `browser_snapshot`, `browser_take_screenshot`, etc.
- Los artefactos de sesión (snapshots, logs de consola) se guardan en `.playwright-mcp/`
  y los screenshots de verificación en `test-screenshots/` (ambos fuera de git).

## Resultado
- Verificación visual de la app en vivo desde Claude Code, sin escribir scripts de Playwright.
- Se usó inmediatamente para validar los fixes de los prompts 25 y 26 (login, severidad,
  permisos) con screenshots como evidencia.

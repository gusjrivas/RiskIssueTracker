# Índice de Prompts — RiskIssueTracker

Registro cronológico de todos los prompts y decisiones de diseño del proyecto,
desde el scaffolding inicial hasta el estado actual.

**Proyecto:** RiskIssueTracker  
**Autores:** Gustavo Julián Rivas · Rodolfo Di Chiazza  
**Stack:** FastAPI + React + PostgreSQL + Docker

---

## Fases del proyecto

| Archivo | Fase | Branch | Descripción |
|---|---|---|---|
| [01_prompt_scaffolding.md](01_prompt_scaffolding.md) | Setup | `feat/project-setup-complete` | Estructura, dominio, metodología de severidad, estados |
| [02_prompt_tdd-setup.md](02_prompt_tdd-setup.md) | Setup | `feat/project-setup-complete` | Framework de testing, 42 tests de severity calculator |
| [03_prompt_auth-module.md](03_prompt_auth-module.md) | Backend | `feat/project-setup-complete` | JWT, Google OAuth, flujo de aprobación (86 tests) |
| [04_prompt_projects-module.md](04_prompt_projects-module.md) | Backend | `feat/risks` | CRUD proyectos con ownership (127 tests) |
| [05_prompt_risks-module.md](05_prompt_risks-module.md) | Backend | `feat/risks` | Riesgos con severidad automática y máquina de estados |
| [06_prompt_issues-module.md](06_prompt_issues-module.md) | Backend | `feat/issues` | Issues con derivación desde riesgo, FK circular diferida |
| [07_prompt_history-audit-modules.md](07_prompt_history-audit-modules.md) | Backend | `feat/issues` | Historial append-only + log de auditoría completo |
| [08_prompt_backend-audit-bugfixes.md](08_prompt_backend-audit-bugfixes.md) | QA | `feat/issues` | 5 bugs corregidos, 342 tests pasando |
| [09_prompt_frontend.md](09_prompt_frontend.md) | Frontend | `feat/frontend` | SPA completa: auth, proyectos, riesgos, issues, historial |
| [10_prompt_docker-deployment.md](10_prompt_docker-deployment.md) | DevOps | `feat/frontend` | Docker fixes, UUID, setuptools, .env.example |
| [11_prompt_hotfix1-bugs-post-deploy.md](11_prompt_hotfix1-bugs-post-deploy.md) | Hotfix | `hotfix/bugs-mitigation-register` | PATCH/PUT, admin panel, mensajes en español |
| [12_prompt_ux-improvements.md](12_prompt_ux-improvements.md) | Features | `feat/ux-improvements` | Severidad en tiempo real, editar usuarios, unsaved changes |
| [13_prompt_hotfix2-useblocker-crash.md](13_prompt_hotfix2-useblocker-crash.md) | Hotfix | `hotfix2/useBlocker-crash` | Pantalla en blanco al abrir riesgo (useBlocker incompatible) |
| [14_prompt_hotfix3-issues-derived-lock.md](14_prompt_hotfix3-issues-derived-lock.md) | Hotfix | `hotfix3/issues-visibility-derived-lock` | Issues visibles, riesgo derivado solo lectura, crear issue, nombre proyecto |
| [15_prompt_readme.md](15_prompt_readme.md) | Docs | `hotfix3/...` | README completo con setup, API reference, arquitectura |
| [16_prompt_hotfix-password-validation.md](16_prompt_hotfix-password-validation.md) | Hotfix | `hotfix3/password-not-meeting-requirements` | Bug: validación de contraseña mostraba `[object Object]` en lugar del mensaje de error |
| [17_prompt_user-profile.md](17_prompt_user-profile.md) | Feature | `feature/user-profile` | Mi Perfil: cambio de contraseña + selector de tema claro/oscuro + fixes |
| [18_prompt_mitigation-plan-guard.md](18_prompt_mitigation-plan-guard.md) | Hotfix | `fix/mitigation-plan-save-guard` | Bug en save del plan de mitigación; modal 3 opciones al navegar con cambios pendientes |
| [19_prompt_owner-activity-log.md](19_prompt_owner-activity-log.md) | Feature | `fix/mitigation-plan-save-guard` | Owner assignment en riesgos/issues + activity log con before/after por campo |
| [20_prompt_soft-delete.md](20_prompt_soft-delete.md) | Feature | `fix/mitigation-plan-save-guard` | Borrado lógico (soft delete) + sección Papelera en AdminPage para restaurar |
| [21_prompt_dark-mode-fix.md](21_prompt_dark-mode-fix.md) | Fix | `fix/dark-mode-google-oauth` | Dark mode: migración a CSS variables en Tailwind + botón Google OAuth frontend |
| [22_prompt_google-oauth-backend.md](22_prompt_google-oauth-backend.md) | Feature | `feat/google-oauth-backend` | Google OAuth backend: endpoint /auth/google + UX pantalla acceso bloqueado |
| [23_prompt_new_login_page.md](23_prompt_new_login_page.md) | Feature | `feature/New-login-page` | Rediseño de la pantalla de login: 3 propuestas visuales, spec aprobada e implementación con sub-agentes |
| [24_prompt_playwright-mcp.md](24_prompt_playwright-mcp.md) | Chore | `chore/add-playwright-mcp` | Playwright MCP a nivel proyecto (`.mcp.json` versionado) para verificación de UI en navegador real |
| [25_prompt_bug-sweep.md](25_prompt_bug-sweep.md) | Fix | `fix/bug-sweep` | Barrido completo de bugs: 6 corregidos con TDD (severidad, auth, derive, paginación) |
| [26_prompt_permission-feedback.md](26_prompt_permission-feedback.md) | Fix | `fix/permission-feedback` | Feedback de permisos en riesgos/issues: banner + acciones deshabilitadas para usuarios sin permiso |
| [27_prompt_dashboard-stats.md](27_prompt_dashboard-stats.md) | Feature | `feature/dashboard-stats` | Dashboard `/dashboard`: matriz 3×3 severidad × zona con counts + bar charts por estado, filtrado por rol |

---

## Principios aplicados en todo el proyecto

- **TDD estricto:** test rojo → código mínimo → verde → refactor. Sin código sin tests.
- **Una rama por módulo:** nunca commit directo a main, siempre PR.
- **Separación de capas:** routers solo HTTP, services solo lógica, models solo estructura.
- **Archivos sensibles fuera de git:** `.env`, `settings.local.json` nunca commiteados.
- **Prueba funcional antes de merge:** verificación en browser antes de cada PR.
- **Append-only para auditoría:** `history_entries` y `audit_log` solo INSERT, nunca UPDATE/DELETE.

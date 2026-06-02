# Prompt 03 — Módulo de autenticación

## Contexto
Implementación completa del módulo de autenticación con JWT, Google OAuth y flujo de aprobación de usuarios.

## Prompts

### Módulo auth (TDD)
```
Implementá el módulo de autenticación completo siguiendo TDD:

Entidad User:
- id (UUID), email (único), full_name, google_id (opcional), password_hash (opcional)
- picture (URL avatar), role (admin|user), status (pending|active|inactive)
- Constraint: al menos uno de google_id o password_hash debe estar presente

Endpoints:
- POST /api/v1/auth/register — registro con email/password → status pending
- POST /api/v1/auth/login — login con email/password → JWT
- POST /api/v1/auth/google — login/registro con Google ID token → JWT
- GET /api/v1/auth/me — datos del usuario autenticado

Lógica:
- JWT HS256, expiración configurable (default 24h)
- Contraseña hasheada con bcrypt
- Google OAuth: verificar ID token con google-auth library
- Login retorna 403 con mensaje descriptivo si cuenta está pending o inactive

Dependencias FastAPI:
- get_current_user: extrae user del JWT, inyectable en cualquier endpoint
- require_admin: verifica role=admin, lanza 403 si no

Flujo de aprobación:
1. Usuario se registra → status=pending
2. Admin aprueba via PATCH /api/v1/admin/users/{id}/approve → status=active
3. Admin puede desactivar via PATCH /api/v1/admin/users/{id}/deactivate → status=inactive

Tests requeridos (TDD — primero los tests):
- Registro exitoso y fallido (email duplicado, password corto)
- Login exitoso, cuenta pending, cuenta inactive, credenciales incorrectas
- Token inválido / expirado
- Endpoint /me con token válido
- require_admin con user sin admin role
```

## Branch
`feat/project-setup-complete`

## Resultado
- 86 tests pasando
- Módulo auth completo con JWT + Google OAuth
- Schema UserResponse, RegisterRequest, LoginRequest, TokenResponse
- app/services/auth_service.py con hash_password, verify_password, create_access_token, decode_token

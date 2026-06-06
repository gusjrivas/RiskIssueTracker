# Prompt 22 — Feature: Google OAuth backend + UX de acceso bloqueado

## Contexto
El endpoint `POST /api/v1/auth/google` no existía. El frontend llamaba a esa ruta
pero el backend no la tenía implementada, resultando en "user not found" / "Failed to fetch".
Además, usuarios pendientes o desactivados no veían ningún mensaje en la interfaz.

## Branch
`feat/google-oauth-backend`

## Prompts

```
sigue sin funcionar cuando selecciono acceder con google se abre una ventana para elegir
la cuenta cuando la elijo se cierra pero no se lleva a ver el error
```

```
cuando un usario se registra por google hasta que el admin lo apruebe tiene que mostrar
en la pantalla de login pendiente de aprobación por el administrador
```

```
cuando un user este desactivado y quiera ingresar se debe mostrar un mensaje pendiente
de aprobación por administrador. desactive un usuario con Google OAuth y no se indica
nada al usuario desde la interfaz que sucede
```

## Implementación — backend

### Dependencia nueva
```toml
# pyproject.toml
"requests>=2.31"   # requerida por google.auth.transport.requests
```

### Servicio
```python
# app/services/auth_service.py
def login_with_google(db: Session, id_token_str: str) -> User:
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    try:
        id_info = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido")

    google_sub = id_info["sub"]
    email      = id_info["email"]
    full_name  = id_info.get("name", email)

    # Buscar por google_id, luego por email (para cuentas ya existentes con email/pass)
    user = db.execute(select(User).where(User.google_id == google_sub)).scalar_one_or_none()
    if user is None:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user is None:
        # Nuevo usuario: crear como pending
        user = User(email=email, full_name=full_name, google_id=google_sub,
                    role=UserRole.user, status=UserStatus.pending)
        db.add(user); db.commit(); db.refresh(user)
        raise HTTPException(403, "Cuenta pendiente de aprobación por un administrador")

    if user.google_id is None:       # asociar google_id a cuenta existente
        user.google_id = google_sub; db.commit()

    if user.status == UserStatus.pending:
        raise HTTPException(403, "Cuenta pendiente de aprobación")
    if user.status == UserStatus.inactive:
        raise HTTPException(403, "Cuenta desactivada")

    return user
```

### Endpoint
```python
# app/api/auth.py
@router.post("/google", response_model=TokenResponse)
def login_google(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    user = login_with_google(db, body.id_token)
    return TokenResponse(access_token=create_access_token(user))
```

El schema `GoogleAuthRequest` ya existía en `app/schemas/auth.py`.

## Diagnóstico — causa de "Failed to fetch"

El API container no tenía `GOOGLE_CLIENT_ID` al momento de verificar el token.
`verify_oauth2_token` fallaba con `ValueError` → backend devolvía 401 →
`client.js` hacía `window.location.href = '/login'` recargando la página y
borrando cualquier mensaje de error. Fix: restart del container con la variable del `.env`.

## Implementación — UX acceso bloqueado (frontend)

```jsx
// LoginPage.jsx
const [blocked, setBlocked] = useState(null)

const isAccessBlocked = (msg) =>
  msg?.toLowerCase().includes('pendiente') || msg?.toLowerCase().includes('desactivada')

// En handleGoogleResponse y handleSubmit:
} catch (err) {
  if (isAccessBlocked(err.message)) {
    setBlocked(err.message)   // pantalla dedicada
  } else {
    setError(err.message)     // error inline
  }
}

// Pantalla de acceso bloqueado
if (blocked) {
  return (
    <div className="card text-center space-y-3">
      <h2>{isPending ? 'Cuenta pendiente' : 'Cuenta desactivada'}</h2>
      <p className="text-muted">{blocked}</p>
      <button onClick={() => setBlocked(null)}>Volver al login</button>
    </div>
  )
}
```

## Flujo completo de primer login con Google

1. Usuario hace click "Acceder con Google" → Google popup → elige cuenta
2. Google devuelve `credential` (id_token JWT firmado)
3. Frontend → `POST /api/v1/auth/google` con el token
4. Backend verifica con `google.oauth2.id_token.verify_oauth2_token`
5. Si cuenta no existe → se crea como `pending` → 403 → pantalla "Cuenta pendiente"
6. Admin aprueba: `UPDATE users SET status='active', role='admin' WHERE email='...'`
7. Segundo login → 200 → JWT de la app → dashboard

## Resultado
- `POST /api/v1/auth/google` implementado y funcional
- Primer login crea cuenta `pending` y muestra pantalla de aprobación
- Cuenta desactivada muestra pantalla "Cuenta desactivada"  
- Ambas pantallas tienen botón "Volver al login"
- Compatible con cuentas existentes (email/password): asocia `google_id` automáticamente

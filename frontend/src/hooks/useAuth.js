// TODO: implement useAuth hook
// Expone: { user, token, loading, loginWithGoogle, loginWithPassword, register, logout }
// - loginWithGoogle(id_token): POST /auth/google → guarda JWT en localStorage
// - loginWithPassword(email, password): POST /auth/login → guarda JWT en localStorage
// - register(email, password, full_name): POST /auth/register
// - logout(): elimina JWT del localStorage
// - user: null si no autenticado, { id, email, full_name, role, status } si autenticado

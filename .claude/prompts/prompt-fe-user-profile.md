
to each user we need to add the feature "My Profile" where it can change the password, and it also can set theme light or dark, that will impact on all the UI according to value chosen

ok, but this new version does not even render login page, i get this error from vite in frontend:
Internal server error: [postcss] /app/src/index.css:59:5: The `bg-surface` class does not exist. If `bg-surface` is a custom class, make sure it is defined within a `@layer` directive

in "My Profile", when I hit "Claro" or "Oscuro", both cases this error appears in red: "Not Found"

Another error, also in "My Profile". Once a user has registered with an email @gmail.com , in the profile it appears this:
"Tu cuenta usa autenticación de Google. No podés cambiar la contraseña aquí"
That is a mistake, to have an email with that domain does not mean it is using Google Authentication. In fact, Google Auth is not implemented yet


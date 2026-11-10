# Initial administrator bootstrap

The student registration endpoint always creates a `student` role. It never
accepts a role or admin flag from the client. The admin app therefore needs a
one-time operator-controlled bootstrap after the database schema is ready.

## Preconditions

1. Apply and verify the approved database migration first.
2. Confirm Render's backend service is connected to the intended database.
3. Confirm `ENVIRONMENT` resolves to `staging` or `production` and that
   `JWT_SECRET` is a strong non-placeholder value.
4. Open the backend service's interactive Shell.

## Command

From the container's `/app` working directory, run:

```sh
python -m app.commands.bootstrap_admin
```

Enter the administrator name and email. Password entry is hidden and must meet
the same validation as student registration (12–128 characters, with upper,
lower, and numeric characters).

The command:

- requires an interactive terminal;
- serializes concurrent PostgreSQL invocations with an advisory transaction lock;
- aborts if any admin account already exists;
- aborts if the email already belongs to an account (it never promotes students);
- stores only a bcrypt password hash;
- is not exposed as an API endpoint and never prints the password.

After it succeeds, sign in at the admin app using the new credentials. Keep the
operator's access to Render Shell restricted. This command should be run once
per environment only after that environment's migration is verified.

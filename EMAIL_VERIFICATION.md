# Email Verification & Password Reset Implementation

## Overview
Complete email verification and password reset system added to the Bazar e-commerce platform.

## Backend Changes (Django)

### Models Added
**users/models.py:**
- Added `email_verified` field to User model (default: False)
- Created `EmailVerification` model:
  - user (FK to User)
  - token (UUID, unique)
  - created_at (auto)
  - is_used (boolean)
  - is_expired() method (24 hours expiry)

- Created `PasswordReset` model:
  - user (FK to User)
  - token (UUID, unique)
  - created_at (auto)
  - expires_at (1 hour from creation)
  - is_used (boolean)
  - is_expired() method

### API Endpoints Added
**users/urls.py:**
- `POST /api/auth/verify-email/<token>/` - Verify email with token
- `POST /api/auth/resend-verification/` - Resend verification email
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Confirm password reset with token

### Views Updated
**users/views.py:**
- **RegisterView**: Now sends verification email instead of returning JWT tokens
- **LoginView**: Checks email_verified status, returns 403 if not verified
- **VerifyEmailView**: Verifies email and returns JWT tokens
- **ResendVerificationView**: Sends new verification email
- **PasswordResetRequestView**: Sends password reset email
- **PasswordResetConfirmView**: Resets password with token

### Email Templates
**templates/emails/:**
- `verification_email.html` - Welcome email with verification button
- `password_reset_email.html` - Password reset email with reset button

### Settings Configuration
**shop/settings.py:**
- Added `FRONTEND_URL` setting (default: http://localhost:8081)
- Email backend configuration:
  - Development: Console backend (prints to terminal)
  - Production: SMTP (Gmail) via environment variables
- Email settings: HOST, PORT, TLS, credentials

### Admin Panel
**users/admin.py:**
- Added email_verified and is_seller to User list display
- Registered EmailVerification model with admin
- Registered PasswordReset model with admin
- Shows expired status for tokens

## Frontend Changes (Vue.js)

### New Pages Created

1. **EmailVerificationPage.vue** (`/email-verification`)
   - Shows "Check your email" message
   - Displays user's email address
   - Resend button with 60-second countdown
   - Instructions for troubleshooting

2. **EmailVerifiedPage.vue** (`/verify-email/:token`)
   - Verifies email token automatically on mount
   - Shows success message with confetti icon
   - Stores JWT tokens in localStorage
   - Redirects to catalog or profile

3. **PasswordResetPage.vue** (`/password-reset`)
   - Email input form
   - Sends reset link to email
   - Success message after sending

4. **PasswordResetConfirmPage.vue** (`/password-reset/confirm/:token`)
   - New password input with confirmation
   - Password strength requirements display
   - Validates password match and length
   - Success message with login link

### Updated Pages

**RegisterPage.vue:**
- Now redirects to EmailVerificationPage after registration
- Passes email in query params

**LoginPage.vue:**
- Handles 403 error for unverified emails
- Shows clear error message
- Displays "Resend verification email" link
- Added "Forgot Password?" link

### Services Updated
**services/index.js - authService:**
- `verifyEmail(token)` - Verify email with token
- `resendVerification(email)` - Resend verification email
- `requestPasswordReset(email)` - Request password reset
- `confirmPasswordReset(token, password)` - Reset password

### Router Updated
**router/index.js:**
- Added `/email-verification` route (guest)
- Added `/verify-email/:token` route (guest)
- Added `/password-reset` route (guest)
- Added `/password-reset/confirm/:token` route (guest)

### Store Updated
**stores/auth.js:**
- Updated `register()` to not set tokens immediately
- Returns response for email verification flow

## User Flow

### Registration Flow
1. User fills registration form
2. Backend creates user with `email_verified=False`
3. Backend sends verification email
4. User redirected to EmailVerificationPage
5. User clicks link in email
6. EmailVerifiedPage verifies token
7. Backend sets `email_verified=True` and returns JWT tokens
8. User logged in automatically

### Login Flow
1. User enters email/password
2. Backend checks credentials
3. If email not verified → 403 error with message
4. Frontend shows error with resend link
5. If verified → returns JWT tokens
6. User logged in

### Password Reset Flow
1. User clicks "Forgot Password?" on login page
2. User enters email on PasswordResetPage
3. Backend sends reset email
4. User clicks link in email
5. PasswordResetConfirmPage shows password form
6. User enters new password
7. Backend validates token and updates password
8. User redirected to login

## Security Features

- UUID tokens (not guessable)
- Token expiration (24h for email, 1h for password)
- One-time use tokens (marked as used after verification)
- Password minimum 8 characters
- Rate limiting on login (5/minute)
- Tokens stored in database, not in URL parameters
- Email verification required before login

## Email Configuration

### Development
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Emails printed to console for testing.

### Production
Set environment variables:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@bazar.com
FRONTEND_URL=https://yourdomain.com
```

## Testing Checklist

- [ ] Register new user
- [ ] Check console for verification email
- [ ] Click verification link
- [ ] Verify email is marked as verified
- [ ] Try to login before verification (should fail)
- [ ] Login after verification (should succeed)
- [ ] Test resend verification email
- [ ] Request password reset
- [ ] Check console for reset email
- [ ] Click reset link and set new password
- [ ] Login with new password
- [ ] Test expired tokens (wait or manually expire)
- [ ] Test used tokens (try to use same link twice)

## Database Migrations

```bash
python manage.py makemigrations users
python manage.py migrate
```

Creates:
- `users_emailverification` table
- `users_passwordreset` table
- Adds `email_verified` column to `users_user` table

## Admin Panel Features

- View all email verifications
- See which tokens are used/expired
- View all password reset requests
- Filter by status and date
- Search by user email or token

## Future Enhancements

- Email templates with company branding
- SMS verification as alternative
- Two-factor authentication (2FA)
- Social login (Google, Facebook)
- Email change verification
- Account deletion with confirmation
- Login history tracking
- Suspicious activity alerts

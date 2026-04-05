# Email Verification Testing Guide

## ✅ Implementation Complete!

Both backend and frontend are running:
- **Backend**: http://127.0.0.1:8000
- **Frontend**: http://localhost:8081
- **API Docs**: http://127.0.0.1:8000/swagger/

## Quick Test Steps

### 1. Test Registration with Email Verification

1. Go to http://localhost:8081/register
2. Fill in the registration form:
   - Email: test@example.com
   - First Name: Test
   - Last Name: User
   - Password: testpass123
   - Confirm Password: testpass123
3. Click "Зарегистрироваться"
4. You should be redirected to the email verification page
5. Check your Django console/terminal for the verification email
6. Copy the verification URL from the console
7. Paste it in your browser (or click the link)
8. You should see "Email Verified!" success page
9. You're now automatically logged in

### 2. Test Login Before Verification

1. Register a new user (follow step 1 above)
2. **Don't click the verification link**
3. Go to http://localhost:8081/login
4. Try to login with the unverified account
5. You should see error: "Please verify your email address before logging in"
6. Click "Resend verification email" link
7. Check console for new verification email

### 3. Test Password Reset

1. Go to http://localhost:8081/login
2. Click "Забыли пароль?" (Forgot Password?)
3. Enter your email address
4. Click "Send Reset Link"
5. Check Django console for password reset email
6. Copy the reset URL from console
7. Paste it in browser
8. Enter new password (minimum 8 characters)
9. Confirm password
10. Click "Reset Password"
11. You should see success message
12. Go to login and use new password

### 4. Test Resend Verification

1. Go to http://localhost:8081/email-verification?email=test@example.com
2. Wait for countdown (or click immediately)
3. Click "Resend Verification Email"
4. Check console for new email
5. Countdown should restart (60 seconds)

### 5. Test Expired Tokens

**Email Verification (24 hours):**
- Tokens expire after 24 hours
- To test: manually update `created_at` in database to 25 hours ago
- Try to verify - should show "Token expired" error

**Password Reset (1 hour):**
- Tokens expire after 1 hour
- To test: manually update `expires_at` in database to past time
- Try to reset - should show "Token expired" error

### 6. Test Used Tokens

1. Verify an email successfully
2. Try to use the same verification link again
3. Should show "Token already used" error

## Console Email Output Example

When you register, you'll see something like this in the Django console:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verify your email - Bazar
From: noreply@bazar.com
To: test@example.com
Date: Sat, 05 Apr 2026 20:00:00 -0000
Message-ID: <...>

Please verify your email by clicking: http://localhost:8081/verify-email/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Admin Panel Testing

1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Check "Email verifications" section:
   - See all verification tokens
   - Check which are used/expired
   - Filter by status
4. Check "Password resets" section:
   - See all reset requests
   - Check expiration times
   - View token usage
5. Check "Users" section:
   - See `email_verified` status
   - Filter by verified/unverified users

## API Testing (Swagger)

1. Go to http://127.0.0.1:8000/swagger/
2. Test endpoints:
   - `POST /api/auth/register/` - Register user
   - `POST /api/auth/verify-email/{token}/` - Verify email
   - `POST /api/auth/resend-verification/` - Resend email
   - `POST /api/auth/login/` - Login (should fail if not verified)
   - `POST /api/auth/password-reset/` - Request reset
   - `POST /api/auth/password-reset/confirm/` - Confirm reset

## Common Issues & Solutions

### Issue: Emails not showing in console
**Solution**: Check that `EMAIL_BACKEND` is set to console backend in settings.py

### Issue: Verification link doesn't work
**Solution**: Check that `FRONTEND_URL` in settings.py matches your frontend URL (http://localhost:8081)

### Issue: 403 error on login
**Solution**: This is expected! Verify your email first before logging in

### Issue: Token expired immediately
**Solution**: Check your system time is correct

### Issue: Can't find verification email in console
**Solution**: Scroll up in the Django console - emails are printed there

## Production Setup

For production, update `.env` file:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

**Note**: For Gmail, you need to create an "App Password":
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new password
4. Use that password in EMAIL_HOST_PASSWORD

## Features Implemented

✅ Email verification on registration
✅ Block login until email verified
✅ Resend verification email
✅ Password reset via email
✅ Token expiration (24h for email, 1h for password)
✅ One-time use tokens
✅ Beautiful HTML email templates
✅ Admin panel for token management
✅ Clear error messages
✅ Responsive UI
✅ Security best practices

## Next Steps

After testing, you can:
1. Customize email templates in `templates/emails/`
2. Add company logo to emails
3. Set up production email service (SendGrid, Mailgun, etc.)
4. Add SMS verification as alternative
5. Implement 2FA (Two-Factor Authentication)
6. Add social login (Google, Facebook)

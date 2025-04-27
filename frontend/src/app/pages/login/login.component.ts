import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { SnackbarService } from '../../services/snackbar.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule]
})
export class LoginComponent implements OnInit {
  activeTab: 'login' | 'signup' = 'login';
  loginForm: FormGroup;
  signupForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private snackbarService: SnackbarService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.signupForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    });
  }

  ngOnInit() {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  switchTab(tab: 'login' | 'signup') {
    this.activeTab = tab;
    this.errorMessage = '';
  }

  onLogin() {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.errorMessage = '';
      
      this.authService.login(email, password).subscribe({
        next: () => {
          // Wait for the user state to be initialized
          this.authService.currentUser$.subscribe(user => {
            if (user) {
              this.router.navigate(['/dashboard']);
            }
          });
        },
        error: (error) => {
          this.errorMessage = error.error?.message || 'Login failed. Please try again.';
          this.snackbarService.show(this.errorMessage, 'error');
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }

  onSignup() {
    if (this.signupForm.valid) {
      const { email, password, confirmPassword } = this.signupForm.value;
      
      if (password !== confirmPassword) {
        this.errorMessage = 'Passwords do not match';
        this.snackbarService.show(this.errorMessage, 'error');
        return;
      }

      this.errorMessage = '';
      
      this.authService.register(email, password).subscribe({
        next: () => {
          this.snackbarService.show('Registration successful! Please log in.', 'success');
          this.router.navigate(['/']);
        },
        error: (error) => {
          this.errorMessage = error.error?.message || 'Registration failed. Please try again.';
          this.snackbarService.show(this.errorMessage, 'error');
        }
      });
    } else {
      this.signupForm.markAllAsTouched();
    }
  }

  getLoginErrors(): string[] {
    const errors: string[] = [];
    const email = this.loginForm.get('email');
    const password = this.loginForm.get('password');

    if (email?.errors && email.touched) {
      if (email.errors['required']) errors.push('Email is required');
      if (email.errors['email']) errors.push('Please enter a valid email');
    }

    if (password?.errors && password.touched) {
      if (password.errors['required']) errors.push('Password is required');
      if (password.errors['minlength']) errors.push('Password must be at least 6 characters');
    }

    return errors;
  }

  getSignupErrors(): string[] {
    const errors: string[] = [];
    const email = this.signupForm.get('email');
    const password = this.signupForm.get('password');
    const confirmPassword = this.signupForm.get('confirmPassword');

    if (email?.errors && email.touched) {
      if (email.errors['required']) errors.push('Email is required');
      if (email.errors['email']) errors.push('Please enter a valid email');
    }

    if (password?.errors && password.touched) {
      if (password.errors['required']) errors.push('Password is required');
      if (password.errors['minlength']) errors.push('Password must be at least 6 characters');
    }

    if (confirmPassword?.errors && confirmPassword.touched) {
      if (confirmPassword.errors['required']) errors.push('Confirm password is required');
    }

    return errors;
  }
}

import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class LoginComponent {
  activeTab: 'login' | 'signup' = 'login';
  loginForm: FormGroup;
  signupForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router
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

  switchTab(tab: 'login' | 'signup') {
    this.activeTab = tab;
  }

  onLogin() {
    if (this.loginForm.valid) {
      // TODO: Implement login logic
      console.log('Login form submitted:', this.loginForm.value);
    } else {
      this.loginForm.markAllAsTouched();
    }
  }

  onSignup() {
    if (this.signupForm.valid) {
      // TODO: Implement signup logic
      console.log('Signup form submitted:', this.signupForm.value);
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

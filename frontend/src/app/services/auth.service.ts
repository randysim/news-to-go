import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface Tokens {
  refresh: string;
  access: string;
}

export interface RegisterResponse {
  message: string;
  user: User;
  tokens: Tokens;
}

export interface LoginResponse {
  refresh: string;
  access: string;
}

export interface RefreshResponse {
  access: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.initializeAuth();
  }

  private initializeAuth(): void {
    if (this.isAuthenticated()) {
      this.fetchUserInfo().subscribe({
        error: () => {
          // If fetching user info fails, clear auth state
          this.logout();
        }
      });
    }
  }

  private setCookie(name: string, value: string, days: number): void {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value};${expires};path=/;SameSite=Strict;Secure`;
  }

  private deleteCookie(name: string): void {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Strict;Secure`;
  }

  private getCookie(name: string): string | null {
    const nameWithEquals = name + '=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let cookie of cookieArray) {
      cookie = cookie.trim();
      if (cookie.indexOf(nameWithEquals) === 0) {
        return cookie.substring(nameWithEquals.length, cookie.length);
      }
    }
    return null;
  }

  register(email: string, password: string): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${environment.apiUrl}/users/`, { email, password })
      .pipe(
        tap(response => {
          this.setSession(response.tokens, response.user);
        })
      );
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/token/`, { email, password })
      .pipe(
        tap(response => {
          this.setSession(response, null);
          this.fetchUserInfo().subscribe();
        })
      );
  }

  private fetchUserInfo(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/users/`).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
      }),
      catchError(error => {
        console.error('Error fetching user info:', error);
        this.logout();
        return throwError(() => error);
      })
    );
  }

  refreshToken(): Observable<RefreshResponse> {
    return this.http.post<RefreshResponse>(`${environment.apiUrl}/auth/token/refresh/`, {})
      .pipe(
        tap(response => {
          this.setAccessToken(response.access);
        }),
        catchError(error => {
          this.logout();
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    this.deleteCookie(this.ACCESS_TOKEN_KEY);
    this.deleteCookie(this.REFRESH_TOKEN_KEY);
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  private setSession(tokens: Tokens, user: User | null): void {
    this.setAccessToken(tokens.access);
    this.setRefreshToken(tokens.refresh);
    if (user) {
      this.currentUserSubject.next(user);
    }
  }

  private setAccessToken(token: string): void {
    this.setCookie(this.ACCESS_TOKEN_KEY, token, 1/48); // 30 minutes
  }

  private setRefreshToken(token: string): void {
    this.setCookie(this.REFRESH_TOKEN_KEY, token, 1); // 1 day
  }

  getAccessToken(): string | null {
    return this.getCookie(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return this.getCookie(this.REFRESH_TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
} 
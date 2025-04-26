import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError, switchMap } from 'rxjs';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

// Create a token getter function that can be set by AuthService
let getAccessToken: () => string | null = () => null;
let getRefreshToken: () => string | null = () => null;
let logout: () => void = () => {};

// Function to set the token getters (called by AuthService)
export const setAuthTokenGetters = (
  accessTokenGetter: () => string | null,
  refreshTokenGetter: () => string | null,
  logoutFn: () => void
) => {
  getAccessToken = accessTokenGetter;
  getRefreshToken = refreshTokenGetter;
  logout = logoutFn;
};

export const authInterceptor: HttpInterceptorFn = (
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const router = inject(Router);
  const accessToken = getAccessToken();
  
  if (accessToken) {
    request = request.clone({
      setHeaders: {
        Authorization: `Bearer ${accessToken}`
      }
    });
  }

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !request.url.includes('auth/token/refresh')) {
        // Try to refresh the token
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
          logout();
          router.navigate(['/login']);
          return throwError(() => error);
        }

        // Make a direct HTTP call to refresh token (avoiding AuthService)
        return inject(HttpClient).post<{ access: string }>('/api/auth/token/refresh/', {})
          .pipe(
            switchMap((response) => {
              // Update the token using the getter
              const newToken = response.access;
              const newRequest = request.clone({
                setHeaders: {
                  Authorization: `Bearer ${newToken}`
                }
              });
              return next(newRequest);
            }),
            catchError((refreshError) => {
              logout();
              router.navigate(['/login']);
              return throwError(() => refreshError);
            })
          );
      }
      return throwError(() => error);
    })
  );
}; 
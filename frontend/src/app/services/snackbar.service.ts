import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface SnackbarMessage {
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class SnackbarService {
  private messageSubject = new BehaviorSubject<SnackbarMessage | null>(null);
  message$ = this.messageSubject.asObservable();

  show(message: string, type: 'success' | 'error' | 'info' = 'info', duration: number = 3000): void {
    this.messageSubject.next({ message, type, duration });
  }

  hide(): void {
    this.messageSubject.next(null);
  }
} 
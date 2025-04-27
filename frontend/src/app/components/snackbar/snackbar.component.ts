import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { SnackbarService, SnackbarMessage } from '../../services/snackbar.service';

@Component({
  selector: 'app-snackbar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="message" 
         [class]="'fixed bottom-4 right-4 px-4 py-2 rounded-md shadow-lg transform transition-all duration-300 ' + getTypeClass()"
         [class.opacity-0]="!isVisible"
         [class.opacity-100]="isVisible">
      {{ message.message }}
    </div>
  `,
  styles: [`
    :host {
      display: block;
      position: fixed;
      bottom: 1rem;
      right: 1rem;
      z-index: 1000;
    }
  `]
})
export class SnackbarComponent implements OnInit, OnDestroy {
  message: SnackbarMessage | null = null;
  isVisible = false;
  private subscription: Subscription = new Subscription();
  private timeoutId: any;

  constructor(private snackbarService: SnackbarService) {}

  ngOnInit(): void {
    this.subscription = this.snackbarService.message$.subscribe(message => {
      if (message) {
        this.showMessage(message);
      } else {
        this.hideMessage();
      }
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  }

  private showMessage(message: SnackbarMessage): void {
    this.message = message;
    this.isVisible = true;

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }

    this.timeoutId = setTimeout(() => {
      this.hideMessage();
    }, message.duration || 3000);
  }

  private hideMessage(): void {
    this.isVisible = false;
    setTimeout(() => {
      this.message = null;
    }, 300);
  }

  getTypeClass(): string {
    if (!this.message) return '';
    
    switch (this.message.type) {
      case 'success':
        return 'bg-green-500 text-white';
      case 'error':
        return 'bg-red-500 text-white';
      case 'info':
      default:
        return 'bg-blue-500 text-white';
    }
  }
} 
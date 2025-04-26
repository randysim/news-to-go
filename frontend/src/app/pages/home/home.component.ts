import { Component, OnDestroy, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  imports: [RouterModule, CommonModule],
  standalone: true
})
export class HomeComponent implements OnDestroy, OnInit {
    isAuthenticated = false;
    private authSubscription: Subscription = new Subscription();

    constructor(
        private authService: AuthService
    ) {}

    ngOnInit(): void {
        // Initialize authentication state
        this.isAuthenticated = this.authService.isAuthenticated();
        
        // Subscribe to auth state changes
        this.authSubscription = this.authService.currentUser$.subscribe({
            next: (user) => {
                this.isAuthenticated = !!user;
            },
            error: (error) => {
                console.error('Error in auth subscription:', error);
                this.isAuthenticated = false;
            }
        });
    }

    ngOnDestroy(): void {
        if (this.authSubscription) {
            this.authSubscription.unsubscribe();
        }
    }
}
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, CommonModule],
  templateUrl: './navbar.component.html'
})
export class NavbarComponent implements OnInit {
  isMobileMenuOpen = false;
  isAuthenticated = false;
  private authSubscription: Subscription = new Subscription();
  
  constructor(public authService: AuthService) {}

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

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  logout() {
    this.authService.logout();
  }
} 
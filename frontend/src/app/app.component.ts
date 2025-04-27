import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './components/navbar/navbar.component';
import { SnackbarComponent } from './components/snackbar/snackbar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, SnackbarComponent],
  template: `
    <app-navbar></app-navbar>
    <main class="container mx-auto px-4 py-8">
      <router-outlet></router-outlet>
    </main>
    <app-snackbar></app-snackbar>
  `
})
export class AppComponent {
  title = 'news-to-go';
}

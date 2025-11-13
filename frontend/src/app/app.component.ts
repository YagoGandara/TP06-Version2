import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Todo } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'TP05 – Angular + FastAPI';
  health = signal<any | null>(null);
  todos = signal<Todo[]>([]);
  newTitle = '';
  loading = signal(false);

  constructor(private api: ApiService) {
    this.refresh();
  }

  refresh() {
    this.api.health().subscribe(h => this.health.set(h));
    this.api.listTodos().subscribe(list => this.todos.set(list));
  }

  add() {
    if (!this.newTitle.trim()) return;
    this.loading.set(true);
    this.api.addTodo(this.newTitle.trim()).subscribe({
      next: (t) => {
        this.todos.update(v => [...v, t]);
        this.newTitle = '';
      },
      complete: () => this.loading.set(false)
    });
  }
}

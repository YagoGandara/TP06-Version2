import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment';

export type Todo = { id: number; title: string; done: boolean; description?: string };

declare global {
  interface Window { __env?: { apiBase?: string } }
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = (window.__env?.apiBase || environment.apiBaseUrl || '').replace(/\/+$/, '');
  constructor(private http: HttpClient) {}
  health()       { return this.http.get(`${this.base}/healthz`); }
  listTodos()    { return this.http.get<Todo[]>(`${this.base}/api/todos`); }
  addTodo(title: string) { return this.http.post<Todo>(`${this.base}/api/todos`, { title }); }
}

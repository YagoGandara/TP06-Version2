import { TestBed } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { ApiService, Todo } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    // Simulamos el env.js que inyecta el pipeline
    (window as any).__env = { apiBase: 'http://fake-api/' };

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService],
    });

    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    (window as any).__env = undefined;
  });

  it('debe hacer GET /healthz usando la base de env.js sin barras duplicadas', () => {
    service.health().subscribe();

    const req = http.expectOne('http://fake-api/healthz');
    expect(req.request.method).toBe('GET');

    req.flush({ ok: true });
  });

  it('debe listar todos con GET /api/todos', () => {
    const mock: Todo[] = [{ id: 1, title: 'A', done: false }];

    service.listTodos().subscribe((resp) => {
      expect(resp as any).toEqual(mock);
    });

    const req = http.expectOne('http://fake-api/api/todos');
    expect(req.request.method).toBe('GET');

    req.flush(mock);
  });

  it('debe crear un todo con POST /api/todos y el título correcto', () => {
    const title = 'Comprar facturas';

    service.addTodo(title).subscribe();

    const req = http.expectOne('http://fake-api/api/todos');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ title });

    req.flush({ id: 1, title, done: false });
  });
});

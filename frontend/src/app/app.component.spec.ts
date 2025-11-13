import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { AppComponent } from './app.component';
import { ApiService, Todo } from './api.service';

class ApiServiceStub {
  health = jasmine.createSpy('health').and.returnValue(
    of({ status: 'ok' }),
  );

  listTodos = jasmine.createSpy('listTodos').and.returnValue(
    of<Todo[]>([{ id: 1, title: 'Tarea inicial', done: false }]),
  );

  addTodo = jasmine
    .createSpy('addTodo')
    .and.callFake((title: string) =>
      of<Todo>({ id: 2, title, done: false }),
    );
}

describe('AppComponent (lógica)', () => {
  let component: AppComponent;
  let api: ApiServiceStub;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [AppComponent], // standalone
      providers: [{ provide: ApiService, useClass: ApiServiceStub }],
    });

    const fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    api = TestBed.inject(ApiService) as unknown as ApiServiceStub;
  });

  it('debe llamar a health() y listTodos() en el constructor (refresh)', () => {
    expect(api.health).toHaveBeenCalled();
    expect(api.listTodos).toHaveBeenCalled();

    expect(component.todos().length).toBe(1);
    expect(component.todos()[0].title).toBe('Tarea inicial');
  });

  it('add() no debe llamar al ApiService si el título está vacío o son solo espacios', () => {
    component.newTitle = '   ';

    component.add();

    expect(api.addTodo).not.toHaveBeenCalled();
    expect(component.todos().length).toBe(1); // sigue solo el inicial
  });

  it('add() debe trim()ear el título, llamar al ApiService y agregar el todo', () => {
    component.newTitle = '  Nueva tarea  ';

    component.add();

    expect(api.addTodo).toHaveBeenCalledWith('Nueva tarea');

    expect(component.todos().length).toBe(2);
    expect(component.todos()[1].title).toBe('Nueva tarea');

    expect(component.newTitle).toBe('');
    expect(component.loading()).toBeFalse();
  });
});

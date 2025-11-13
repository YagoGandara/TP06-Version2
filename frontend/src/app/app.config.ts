import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { provideRouter } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [provideHttpClient(withFetch()), provideRouter([])]
};

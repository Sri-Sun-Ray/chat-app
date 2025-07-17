import { NgModule } from '@angular/core';
import {SocketIoModule,SocketIoConfig} from 'ngx-socket-io';

const config: SocketIoConfig={
  url: 'http://localhost:5000',
  options: {
    extraHeaders: {
      token: localStorage.getItem('token') || ''
    }
  }
};

@NgModule({
  imports:[
    SocketIoModule.forRoot(config)
    // Add other modules here if needed, e.g. CommonModule, FormsModule, etc.
  ],
})
export class App {}
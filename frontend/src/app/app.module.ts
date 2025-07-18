// app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { ChatComponent } from './chat/chat.component'; // only if not standalone

const config: SocketIoConfig = {
  url: 'http://localhost:5000',
  options: {
    extraHeaders: {
      token: typeof window !== 'undefined' ? (localStorage.getItem('token') || '') : ''
    }
  }
};

@NgModule({
  imports: [
    BrowserModule,
    FormsModule,
    SocketIoModule.forRoot(config),
    ChatComponent,
    AppComponent,
     HttpClientModule // ✅ if it's standalone
  ],
  
})
export class AppModule {}

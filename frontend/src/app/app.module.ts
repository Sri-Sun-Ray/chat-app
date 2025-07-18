// app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';

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
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    FormsModule,
    SocketIoModule.forRoot(config),
    ChatComponent // ✅ if it's standalone
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}

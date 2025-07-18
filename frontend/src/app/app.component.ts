// app.component.ts
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ChatService } from './services/chat.service';

const userId = '123';


@Component({
  selector: 'app-root',
  template: `<h1>Chat App</h1>`,
  standalone: true,
  imports: [CommonModule],
  
})
export class AppComponent {
  
  chatService = inject(ChatService);
  

  constructor() {
    this.chatService.getMessages(userId).subscribe({
      next: (data) => console.log('Messages:', data),
      error: (err) => console.error('Error:', err),
    });
  }
}

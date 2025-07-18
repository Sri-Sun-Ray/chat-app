import { Component, OnInit } from '@angular/core';
import { ChatService } from '../services/chat';
import { SocketService } from '../services/socket';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';


@Component({
  standalone:true,
  selector: 'app-chat',
  imports: [CommonModule,FormsModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.scss'],
  
})
export class ChatComponent implements OnInit {

  users: any[]=[];
  selectedUser:any=null;
  messages:any[]=[];
  messageContent: string='';
  myId: string='';
  newMessage=''

  constructor(
    private chatService: ChatService,
    private socketService: SocketService
  ){}

  ngOnInit(): void{
    const token=localStorage.getItem('token');
    if(token){
      this.socketService.connect(token);
      this.loadUsers();
      
      this.socketService.on('receive_message',(msg:any)=>{
        if(msg.from===this.selectedUser.id){
          this.messages.push({
            ...msg,
            fromSelf:false
          });
        }
      });
    }
  }

  loadUsers(){
    this.chatService.getUsers().subscribe((res: any)=>{
      this.users=res;
    });
  }
  selectUser(user:any){
    this.selectedUser=user;
    this.chatService.getMessages(user.id).subscribe((res:any)=>{
      this.messages=res.map((msg:any)=>({
        ...msg,
        fromSelf: msg.sender===this.getCurrentUserId()
      }));
      });
    }

    sendMessage(){
      if(!this.newMessage.trim()) return;

      const msgData={
        to: this.selectedUser.id,
        content: this.newMessage,
      };
      this.messages.push({
        content: this.newMessage,
        fromSelf: true,
        createdAt: new Date() 
      });

      this.socketService.emit('send_message',msgData);
      this.newMessage='';
    }

    getCurrentUserId(){
      const token: any=localStorage.getItem('token');
      return JSON.parse(atob(token.split('.')[1])).id;
    }

}



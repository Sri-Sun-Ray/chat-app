import { Injectable } from '@angular/core';
import {io,Socket} from 'socket.io-client';
import { environment }  from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SocketService{

  private socket!:Socket;

  connect(token: string){
      this.socket=io(environment.socketUrl,{
        auth: {token}
      });
  }

  on(event: string, callback: Function)
  {
    this.socket.on(event,callback as any);
  }
  emit(event:string,data:any)
  {
    this.socket.emit(event,data);
  }
  disconnect(){
    if(this.socket) this.socket.disconnect();
  }


  
}

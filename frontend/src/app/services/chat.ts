import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor(private http: HttpClient){}

  getUsers(){
    return this.http.get(`${environment.apiUrl}/users`);
  }
  getMessages(userId: string){
    return this.http.get(`${environment.apiUrl}/messages/${userId}`)
  };
}

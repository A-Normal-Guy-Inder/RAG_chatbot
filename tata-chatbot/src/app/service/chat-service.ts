import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor(private http: HttpClient) {}

  sendQuestion(question: string): Observable<any> {
    return this.http.post(environment.apiUrl + "/chat", {
      question: question
    });
  }
}

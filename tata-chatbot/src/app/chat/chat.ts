import { Component, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../service/chat-service'

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.scss'],
})
export class Chat {
  messages: Message[] = [];
  newMessage = '';
  loading = false;

  @ViewChild('chatMessagesContainer')
  chatMessagesContainer!: ElementRef;

  constructor(private chatService: ChatService) {
    this.messages.push({
      text: 'Welcome to Tata Motors. How can I assist you today?',
      sender: 'bot'
    });
  }

  sendMessage(): void {
    const userQuery = this.newMessage.trim();
    if (!userQuery || this.loading) return;

    // ✅ Add user message
    this.messages.push({
      text: userQuery,
      sender: 'user'
    });

    this.newMessage = '';
    this.loading = true;
    this.scrollToBottom();

    // ✅ Call Flask API
    this.chatService.sendQuestion(userQuery).subscribe({
      next: (response) => {
        this.messages.push({
          text: response.response,
          sender: 'bot'
        });
        this.loading = false;
        this.scrollToBottom();
      },
      error: (error) => {
        console.error('API Error:', error);
        this.messages.push({
          text: 'Sorry, I am having trouble connecting. Please try again later.',
          sender: 'bot'
        });
        this.loading = false;
        this.scrollToBottom();
      }
    });
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatMessagesContainer) {
        this.chatMessagesContainer.nativeElement.scrollTop =
          this.chatMessagesContainer.nativeElement.scrollHeight;
      }
    }, 0);
  }
}

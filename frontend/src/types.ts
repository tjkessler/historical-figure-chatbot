export interface Persona {
  id: number;
  name: string;
  era: string;
  bio: string;
}

export interface ChatMessage {
  role: 'user' | 'bot';
  message: string;
}

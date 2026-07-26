import React, { useState, useRef, useEffect } from 'react';
import '../../ChatPage.css';
import sala1Img from '../../img/Sala1.png';
import sala2Img from '../../img/Sala2.png';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

console.log("API_BASE_URL:", API_BASE_URL);

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  imageIndex?: number;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Olá! Sou o ChatBot do SENAI Jaú, especialista no curso Técnico em Desenvolvimento de Sistemas.\nEstou aqui para ajudar você com informações sobre as disciplinas, mercado de trabalho,\nposibilidades de carreira, ou qualquer outra dúvida sobre o curso.\n\nFaça sua pergunta sobre o curso! Por exemplo:\n• Qual o objetivo do curso?\n• Quais disciplinas são estudadas?\n• Quanto tempo dura o curso?\n• Como é o mercado de trabalho?\n• Quais os requisitos para ingressar?',
      isUser: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const botResponseCount = useRef(0);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatResponse = (text: string) => {
    return text
      .replace(/\n/g, '<br>')
      .replace(/•/g, '•')
      .replace(/O Curso Técnico em Desenvolvimento de Sistemas tem como objetivo formar profissionais capacitados para analisar, projetar, desenvolver, testar, implantar e manter sistemas computacionais./g, 'O Curso Técnico em Desenvolvimento de Sistemas tem como objetivo formar profissionais capacitados para analisar, projetar, desenvolver, testar, implantar e manter sistemas computacionais.');
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue
        })
      });

      if (!response.ok) {
        throw new Error('Erro ao enviar mensagem');
      }

      const data = await response.json();
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isUser: false,
        imageIndex: botResponseCount.current % 2
      };
      botResponseCount.current += 1;
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Desculpe, ocorreu um erro. Por favor, tente novamente.',
        isUser: false,
        imageIndex: botResponseCount.current % 2
      };
      botResponseCount.current += 1;
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const suggestedQuestions = [
    'Qual o objetivo do curso técnico?',
    'Quais as principais disciplinas?',
    'Quanto tempo dura o curso?',
    'Como é o mercado de trabalho?',
    'Quais os requisitos para ingressar?'
  ];

  const askQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <div className="chat-page">
      <header className="chat-header">
        <div className="logo">
          <span className="logo-text">🤖 Senai Jaú 7.90</span>
        </div>
        <h1 className="chat-title">ChatBot Técnico em Desenvolvimento de Sistemas</h1>
        <p className="chat-subtitle">
          Respondo perguntas sobre o curso técnico em desenvolvimento de sistemas do SENAI Jaú<br />
          Baseado no plano do curso oficial
        </p>
      </header>

      <div className="chat-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user' : 'bot'}-message`}
          >
            <div 
              className="message-content"
              dangerouslySetInnerHTML={{ __html: formatResponse(message.content) }}
            />
            {!message.isUser && message.imageIndex !== undefined && (
              <img
                src={message.imageIndex === 0 ? sala1Img : sala2Img}
                alt={`Sala ${message.imageIndex + 1}`}
                className="bot-image"
              />
            )}
          </div>
        ))}
        {isLoading && (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <span>O assistente está pensando...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          className="input-field"
          placeholder="Digite sua pergunta sobre o curso técnico..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button
          className="send-button"
          onClick={sendMessage}
          disabled={isLoading}
        >
          <span>Enviar</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l11 2-11 2z"/>
          </svg>
        </button>
      </div>

      <div className="suggested-questions">
        <div className="suggested-title">💡 Perguntas Populares</div>
        <div className="suggested-list">
          {suggestedQuestions.map((question, index) => (
            <div
              key={index}
              className="suggested-item"
              onClick={() => askQuestion(question)}
            >
              {question}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

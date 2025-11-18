import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
import re
import os
import ssl
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

load_dotenv()

class CardGenerator : 
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_ai = True
            print("✅ Gemini API подключен!")
        else:
            self.use_ai = False
            print("⚠️ Gemini API ключ не найден.")
    async def generateCards(self,  text : str , numCards : int = 10) -> List[Dict[str,str]]:
        if self.use_ai :
            return await self.withGemini(text , numCards)
        else : 
            return self.generateSimple(text , numCards)
    async def withGemini(self , text : str , numCards : int) -> List[Dict[str,str]]:
        try : 
            prompt = self.createPrompt(text , numCards)
            print(f"🔄 Отправляю запрос в Gemini...")
            response = self.model.generate_content(
                prompt , 
                generation_config= {
                    'temperature' : 0.7 , 
                    'top_p' : 0.8 , 
                    'top_k' : 40 , 
                    'max_output_tokens' : 2048,
                }
            )
            print(f"✅ Получен ответ от Gemini")
            content = response.text
            cards = self.aiResponse(content)
            print(f"📝 Сгенерировано {len(cards)} карточек") 
            return cards[:numCards]
        except Exception as e : 
            print(f"❌ Ошибка Gemini: {e}")
            print("Connecting to simple algorithm...")
            return self.generateSimple(text,numCards)
    def createPrompt(self , text : str , numCards : int) -> str : 
        return f"""Ты эксперт по созданию образовательных флэшкарт. 

На основе следующего текста создай {numCards} флэшкарт для эффективного обучения.
ТЕКСТ:
{text[:4000]}

ТРЕБОВАНИЯ:
1. Каждая карточка должна иметь четкий ВОПРОС и полный ОТВЕТ
2. Вопросы должны проверять понимание ключевых концепций
3. Используй разные типы вопросов:
   - Определения ("Что такое X?")
   - Объяснения ("Как работает X?")
   - Примеры ("Приведи пример X")
   - Причины ("Почему X происходит?")
4. Ответы должны быть краткими (2-4 предложения) но исчерпывающими
5. Фокусируйся на самой важной информации

ФОРМАТ ОТВЕТА (строго соблюдай):
Q: [вопрос 1]
A: [ответ 1]

Q: [вопрос 2]
A: [ответ 2]

Q: [вопрос 3]
A: [ответ 3]

И так далее для всех {numCards} карточек.
Не добавляй никаких дополнительных комментариев или текста - только вопросы и ответы в указанном формате."""
    def aiResponse(self , content : str) -> List[Dict[str,str]] : 
        cards = []
        pattern = r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)'
        matches = re.findall(pattern , content , re.DOTALL | re.IGNORECASE)

        for question , answer in matches : 
            q = question.strip()
            a = answer.strip()

            if q and a and len(q) > 5 and len(a) > 10 :
                cards.append({
                    "question" : q,
                    "answer" : a
                })
        return cards
    def generateSimple(self , text : str , numCards : int) -> List[Dict[str,str]] :
        cards = []
        sentences = self.splitIntoSentences(text)
        validSentences = [
            s for s in sentences
            if 30 < len(s) < 400 and not s.startswith('http')
        ]
        cardTypes = ['definition', 'fill_blank'] 

        for i,sentence in enumerate(validSentences[:numCards * 2]):
            if len(cards) >= numCards : 
                break
            cardType = cardTypes[i % len(cardTypes)]
            card = self.createCard(sentence , cardType , i)

            if card : 
                cards.append(card)
        
        while len(cards) < min(numCards, len(validSentences)) : 
            idx = len(cards)
            if idx < len(validSentences) :
                cards.append({
                    "question" : f"О чем говорится в следующем утверждении?",
                    "answer" : validSentences[idx][:200]
                })

        return cards[:numCards]
    def createCard(self, sentence: str, card_type: str, index: int) -> Dict[str, str]:
        if len(sentence) < 30:
            return None
        if card_type == 'definition':
            keywords = self.extractKeywords(sentence)
            if keywords and len(keywords) > 0:
                return {
                    "question": f"Что означает '{keywords[0]}'?",
                    "answer": sentence
                }
            return None
        elif card_type == 'explanation':
            words = sentence.split()
            if len(words) > 10:
                question_part = ' '.join(words[:6])
                return {
                    "question": f"Продолжи и объясни: '{question_part}...'",
                    "answer": sentence
                }
            return None
        
        elif card_type == 'fill_blank':
            keywords = self.extractKeywords(sentence)
            if keywords and len(keywords) > 0:
                keyword = keywords[0]
                question = sentence.replace(keyword, "______", 1)
                return {
                    "question": f"Заполни пропуск: {question}",
                    "answer": keyword
                }
            return None
        
        elif card_type == 'summary':
            if len(sentence) > 100:
                preview = sentence[:70] + "..."
                return {
                    "question": f"Перескажи своими словами: '{preview}'",
                    "answer": sentence
                }
            else:
                return {
                    "question": f"Объясни: {sentence[:50]}...",
                    "answer": sentence
                }
        return None
    def splitIntoSentences(self , text : str) -> List[str] : 
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    def extractKeywords(self , sentence : str) -> List[str] : 
        stopWords = {
            'это', 'быть', 'в', 'на', 'с', 'по', 'для', 'от', 'к', 'и',
            'а', 'но', 'или', 'что', 'как', 'так', 'вот', 'же', 'то',
            'the', 'is', 'in', 'on', 'at', 'for', 'and', 'or', 'but',
            'which', 'are', 'was', 'were', 'been', 'be', 'have', 'has'
        }

        words = sentence.split()
        keywords = [
            w.strip('.,;:!?()[]{}')
            for w in words 
            if len(w) > 4 
            and w.lower() not in stopWords
            and any(c.isupper() for c in w)
        ]
        return keywords[:5]


class advancedCardGenerator(CardGenerator) :
    def __init__(self):
        super().__init__()
        self.difficulty_levels = ['easy' , 'medium' , 'hard']
    
    async def generateDiff(self , text : str , numCards : int = 10 , difficulty : str = 'medium') -> List[Dict[str,str]] :
        if not self.use_ai :
            return self.generateSimple(text,numCards)
        
        prompt = f"""Создай {numCards} флэшкарт уровня сложности "{difficulty}" из текста:

{text[:4000]}

Уровни сложности:
- easy: простые вопросы на запоминание фактов
- medium: вопросы на понимание концепций
- hard: вопросы требующие анализа и применения знаний

Формат:
Q: [вопрос]
A: [ответ]
""" 
        try : 
            response = self.model.generate_content(prompt)
            cards = self.aiResponse(response.text)
            return cards[:numCards]
        except : 
            return self.generateSimple(text, numCards)
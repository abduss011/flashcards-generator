from fastapi import FastAPI , UploadFile , File,  HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os


from models.cardGenerator import CardGenerator
from utils.pdfParser import parse_pdf
from utils.textProcessor import processText

app = FastAPI(
    title = "Flashcards API" ,
    description = "API для генерации флэшкарт из текста и PDF", 
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cardGenerator = CardGenerator()

class TextInput(BaseModel) : 
    text : str
    numCards : int = 10
class Flashcard(BaseModel) :
    question : str
    answer : str
class FlashcardsResponse(BaseModel) :
    cards : List[Flashcard]
    total : int

@app.get("/")
async def root():
    return {
        "message": "Flashcards API работает!",
        "endpoints": {
            "POST /generate/text": "Генерация карточек из текста",
            "POST /generate/pdf": "Генерация карточек из PDF",
            "GET /health": "Проверка работы сервера"
        }
    }

@app.get("/health")
async def healthCheck():
    return {"status": "healthy", "service": "flashcards-api"}

@app.post("/generate/text", response_model=FlashcardsResponse)
async def generateFromText(inputData : TextInput):
    try : 
        if len(inputData.text.strip()) < 50 :
            raise HTTPException(
                status_code=400,
                detail="Текст слишком короткий.Минимум 50 символов"
            )
        processedText = processText(inputData.text)

        cards = await cardGenerator.generateCards(
            processedText,
            numCards = inputData.numCards
        )
        if not cards : 
            raise HTTPException(
                status_code=500,
                detail="Не удалось сгенерировать карточки"
            )
        return FlashcardsResponse(
            cards=cards,
            total=len(cards)
        )
    except Exception as e: 
        raise HTTPException(status_code=500,detail=f"Ошибка генерации:{str(e)}")
    
@app.post("/generate/pdf", response_model = FlashcardsResponse)
async def generateFromPdf(file : UploadFile = File(...) , numCards : int = 10) :
    try : 
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Разрешены только PDF файлы"
            )
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024 :
            raise HTTPException(
                status_code=400,
                detail="Файл слишком большой.Максимум 10MB"
            )
        
        text = parse_pdf(contents)

        if len(text.strip()) < 50 :
            raise HTTPException(
                status_code=400,
                detail = "PDF содержит слишком мало текста"
            )
        
        processedText = processText(text)
        cards = await cardGenerator.generateCards(
            processedText,
            numCards = numCards
        )

        if not cards : 
            raise HTTPException(
                status_code=500,
                detail= "Не удалось сгенерировать карточки из PDF"
            )
        
        return FlashcardsResponse(
            cards = cards,
            total = len(cards)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail = f"Ошибка обработки PDF : {str(e)}"
        )
    
if __name__ == "__main__" :
    import uvicorn
    uvicorn.run(
        "app:app",
        host = "0.0.0.0",
        port=8004,
        reload=True
    )
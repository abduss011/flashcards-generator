import io
from typing import Union
import PyPDF2
import pdfplumber

def parse_pdf(pdf_content: Union[bytes, str]) -> str:
    try:
        start_page, end_page = _smart_page_range_detection(pdf_content)
        
        print(f"📖 Обрабатываю страницы {start_page}-{end_page}")
        if start_page > 0:
            text = extract_page_range(pdf_content, start_page, end_page)
        else:
            text = pyPdf2(pdf_content)
            if len(text.strip()) < 100:
                text = pdfPlumber(pdf_content)
        cleaned_text = cleanText(text)
        meaningful_text = _filter_meaningful_paragraphs(cleaned_text)
        
        print(f"✅ Извлечено {len(meaningful_text)} символов полезного текста")
        if len(meaningful_text.strip()) < 100:
            print("⚠️ Мало полезного текста, возвращаю весь текст")
            return cleaned_text
        
        return meaningful_text
    
    except Exception as e:
        raise Exception(f"Ошибка парсинга PDF: {str(e)}")
def _is_noise_text(text: str) -> bool:
    """
    Проверяет является ли текст мусором
    """
    if not text or len(text.strip()) < 20:
        return True
    
    noise_patterns = [
        r'copyright|©|все права защищены|isbn',
        r'издательство|publishing|press',
        r'printed in|напечатано',
        
        r'содержание|table of contents|оглавление',
        r'глава \d+|chapter \d+',
        r'часть \d+|part \d+',
        r'раздел \d+|section \d+',

        r'^\d+$',
        r'страница \d+|page \d+',
        
        r'автор:|author:|составитель',
        r'редактор:|editor:|под редакцией',
        
        r'^\s*$',
        r'^[\d\s\.\-—–]+$',
    ]
    
    import re
    text_lower = text.lower().strip()
    
    for pattern in noise_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    return False


def _filter_meaningful_paragraphs(text: str) -> str:
    paragraphs = text.split('\n\n')
    
    meaningful = []
    for para in paragraphs:
        para = para.strip()
        
        if len(para) < 50:
            continue
        
        if _is_noise_text(para):
            continue
        
        words = para.split()
        if len(words) < 10:
            continue
        upper_ratio = sum(1 for c in para if c.isupper()) / len(para)
        if upper_ratio > 0.5:  
            continue
        
        meaningful.append(para)
    
    return '\n\n'.join(meaningful)


def _smart_page_range_detection(pdf_content: bytes) -> tuple:
    import io
    import PyPDF2
    
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        for page_num in range(min(20, total_pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text().lower()
            content_markers = [
                'введение', 'introduction', 'chapter 1', 'глава 1',
                'part 1', 'часть 1', 'раздел 1'
            ]
            
            for marker in content_markers:
                if marker in text:
                    return (page_num, total_pages)
        return (min(3, total_pages), total_pages)
    
    except:
        return (0, 0)
    
def pyPdf2(pdfContent : bytes) -> str:
    try :
        pdfFile = io.BytesIO(pdfContent)
        pdfReader = PyPDF2.PdfReader(pdfFile)

        textParts = []
        for pageNum in range(len(pdfReader.pages)):
            page = pdfReader.pages[pageNum]
            textParts.append(page.extract_text())
        return '\n'.join(textParts)
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
        return ""


def pdfPlumber(pdfContent : bytes) -> str:
    try :
        pdfFile = io.BytesIO(pdfContent)

        textParts = []
        with pdfplumber.open(pdfFile) as pdf :
            for page in pdf.pages :
                text = page.extract_text()
                if text :
                    textParts.append(text)
        return '\n'.join(textParts)
    except Exception as e :
        print(f"pdfplumber failed: {e}")
        return ""

def cleanText(text : str) -> str :
    if not text :
        return ""
    import re
    text = re.sub(r'[ \t]+', ' ', text)
    
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()

def extract_metadata(pdfContent : bytes) -> dict:
    try : 
        pdfFile = io.BytesIO(pdfContent)
        pdfReader = PyPDF2.PdfReader(pdfFile)

        metadata = {
            'numPages' : len(pdfReader.pages),
            'title' : pdfReader.metadata.get('/Title' , 'Unknown'),
            'author' : pdfReader.metadata.get('/Author' , 'Unknown'),
            'subject' : pdfReader.metadata.get('/Subject' , 'Unknown'),
        }
        return metadata
    except Exception as e :
        return {'error' : str(e)}

def extract_page_range(pdfContent : bytes , startPage : int , endPage : int) -> str : 
    try : 
        pdfFile = io.BytesIO(pdfContent)
        pdfReader = PyPDF2.PdfReader(pdfFile)

        textParts = []
        for pageNum in range(startPage , min(endPage , len(pdfReader.pages))) :
            page = pdfReader.pages[pageNum]
            textParts.append(page.extract_text())
        text = '\n'.join(textParts)
        return cleanText(text)
    except Exception as e :
        raise Exception(f"Page extracting failed : {str(e)}")

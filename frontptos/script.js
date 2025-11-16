const API_URL = 'http://localhost:8004';
let curCards = [];
let curCardIndex = 0;
let isFlipped = false;

const themeToggle = document.getElementById('theme-toggle');
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const uploadArea = document.getElementById('upload-area');
const pdfInput = document.getElementById('pdf-input');
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const generateBtn = document.getElementById('generate-btn');
const uploadSection = document.getElementById('upload-section');
const cardsSection = document.getElementById('cards-section');
const flashcard = document.getElementById('flashcard');
const cardQuestion = document.getElementById('card-question');
const cardAnswer = document.getElementById('card-answer');
const curCardEl = document.getElementById('current-card');
const totCardsEl = document.getElementById('total-cards');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const backBtn = document.getElementById('back-btn');
const progressDots = document.getElementById('progress-dots');
const fileInfo = document.getElementById('file-info');
const btnText = document.querySelector('.btn-text');
const btnLoader = document.querySelector('.btn-loader');

function baseTheme() { 
    const savedTheme = localStorage.getItem('theme') || 'light'
    document.documentElement.setAttribute('data-theme' , savedTheme);
    updateThemeIcon(savedTheme);
}
function toggleTheme() { 
    const curTheme = document.documentElement.getAttribute('data-theme');
    newTheme = curTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme' , newTheme);
    localStorage.setItem('theme' , newTheme);
    updateThemeIcon(newTheme);
}
function updateThemeIcon(theme) { 
    const icon = themeToggle.querySelector('.theme-icon');
    if(theme === 'light') { 
        icon.textContent = '🌙';
    } else {
        icon.textContent = '☀️';
    }
}
themeToggle.addEventListener('click',toggleTheme);

tabs.forEach(tab => {
    tab.addEventListener('click' , () => {
        const targetTab = tab.getAttribute('data-tab');
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(targetTab + '-tab').classList.add('active');
        checkGenerateBtn();
    })
})

uploadArea.addEventListener('click' , () => pdfInput.click());
uploadArea.addEventListener('dragover' , (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
})

uploadArea.addEventListener('dragleave' , () => { 
    uploadArea.classList.remove('dragover');
})

uploadArea.addEventListener('drop' , (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if(file && file.type === 'application/pdf') {
        handleFileSelect(file);
    }
})

pdfInput.addEventListener('change' , (e) => {
    const file = e.target.files[0];
    if(file) {
        handleFileSelect(file);
    }
})

function handleFileSelect(file) { 
    document.querySelector('.upload-placeholder').style.display = 'none';
    fileInfo.classList.remove('hidden');
    fileInfo.querySelector('.file-name').textContent = file.name;

    generateBtn.disabled = false;
}

document.querySelector('.remove-file').addEventListener('click', (e) => {
    e.stopPropagation();
    pdfInput.value = '';
    document.querySelector('.upload-placeholder').style.display = 'block';
    fileInfo.classList.add('hidden');
    generateBtn.disabled = true;
});
textInput.addEventListener('input' , () => {
    const len = textInput.value.length;
    charCount.textContent = len;
    checkGenerateBtn();
})

function checkGenerateBtn() { 
    const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');

    if(activeTab === 'text'){
        generateBtn.disabled = textInput.value.trim().length < 50;
    } else {
        generateBtn.disabled = !pdfInput.files[0];
    }
}

generateBtn.addEventListener('click' , async () => {
    const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
    btnText.textContent = 'Generating...';
    btnLoader.classList.remove('hidden');
    generateBtn.disabled = true;

    try {
        if(activeTab === 'pdf') {
            const file = pdfInput.files[0];
            await processPDF(file);
        } else {
            const text = textInput.value;
            await processText(text);
        }
    } catch(error) {
        console.error('Error generating flashcards: ' , error);
        alert('An error occurred while generating flashcards. Please try again.');
    } finally {
        btnText.textContent = 'Generate Flashcards';
        btnLoader.classList.add('hidden');
        generateBtn.disabled = false;
    }
})

async function processPDF(file) { 
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('num_cards', '10');
        
        const response = await fetch(`${API_URL}/generate/pdf`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to process PDF');
        }
        
        const data = await response.json();
        displayCards(data.cards);
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

async function processText(text) { 
    try {
        const response = await fetch(`${API_URL}/generate/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                num_cards: 10
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate cards');
        }
        
        const data = await response.json();
        displayCards(data.cards);
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

function displayCards(cards){
    if(!cards || cards.length === 0){
        alert('Cards generation failed.Try other text');
        return;
    }

    curCards = cards;
    curCardIndex = 0;

    uploadSection.classList.add('hidden');
    cardsSection.classList.remove('hidden');
    totCardsEl.textContent = cards.length;
    updateCard();
    createProgressDots();
}

function updateCard() { 
    const card = curCards[curCardIndex];
    cardQuestion.textContent = card.question;
    cardAnswer.textContent = card.answer;
    curCardEl.textContent = curCardIndex + 1;

    if(isFlipped) {
        flashcard.classList.remove('flipped');
        isFlipped = false;
    }
    prevBtn.disabled = curCardIndex === 0;
    nextBtn.disabled = curCardIndex === curCards.length - 1;

    updateProgressDots();
}

function createProgressDots() {
    progressDots.innerHTML = '';
    const maxDots = Math.min(curCards.length, 10);

    for(let i = 0 ; i < maxDots ; i++){ 
        const dot = document.createElement('div');
        dot.className = 'progress-dot';
        progressDots.appendChild(dot);
    }
    updateProgressDots();
}

function updateProgressDots() {
    const dots = progressDots.querySelectorAll('.progress-dot');
    const maxDots = dots.length;
    const cardsPerDot = curCards.length / maxDots;
    const activeDotIndex = Math.floor(curCardIndex / cardsPerDot);

    dots.forEach((dot,index) => {
        dot.classList.toggle('active' , index === activeDotIndex);
    })
}



flashcard.addEventListener('click' , () => { 
    flashcard.classList.toggle('flipped');
    isFlipped = !isFlipped;
})

prevBtn.addEventListener('click' , () => { 
    if(curCardIndex > 0) {
        curCardIndex--;
        updateCard();
    }
})
nextBtn.addEventListener('click', () => {
    if(curCardIndex < curCards.length - 1) {
        curCardIndex++;
        updateCard();
    }
})


document.addEventListener('keydown' , (e) => { 
    if(cardsSection.classList.contains('hidden')) {
        return;
    }
    if(e.key === 'ArrowLeft' && curCardIndex > 0){
        curCardIndex--;
        updateCard();
    } else if(e.key === 'ArrowRight' && curCardIndex < curCards.length - 1){
        curCardIndex++;
        updateCard();
    } else if(e.key === ' '){
        e.preventDefault();
        flashcard.classList.toggle('flipped');
        isFlipped  = !isFlipped;
    }
});

backBtn.addEventListener('click' , () => {
    cardsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');

    curCards = [];
    curCardIndex = 0;
    isFlipped = false;

    pdfInput.value = '';
    textInput.value = '';
    charCount.textContent = '0';
    document.querySelector('.upload-placeholder').style.display = 'block';
    fileInfo.classList.add('hidden');
    checkGenerateBtn();
})
baseTheme();
checkGenerateBtn();
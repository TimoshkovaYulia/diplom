// Hero canvas
const canvas = document.getElementById('hero-bg');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
for(let i=0;i<80;i++){
    particles.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        dx: (Math.random()-0.5)*0.5,
        dy: (Math.random()-0.5)*0.5,
        radius: Math.random()*2+1
    });
}

function animate() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach(p=>{
        ctx.beginPath();
        ctx.arc(p.x,p.y,p.radius,0,Math.PI*2);
        ctx.fillStyle='rgba(255,255,255,0.6)';
        ctx.fill();
        p.x+=p.dx;
        p.y+=p.dy;
        if(p.x>canvas.width) p.x=0;
        if(p.x<0) p.x=canvas.width;
        if(p.y>canvas.height) p.y=0;
        if(p.y<0) p.y=canvas.height;
    });
    requestAnimationFrame(animate);
}
animate();

// Печатающий текст (пример)
const answerText = "x = 7";
let answerIndex = 0;
function typeAnswer() {
    const el = document.getElementById('typed-answer');
    if(!el) return;
    if(answerIndex < answerText.length) {
        el.textContent += answerText[answerIndex];
        answerIndex++;
        setTimeout(typeAnswer, 100);
    }
}
window.onload = typeAnswer;

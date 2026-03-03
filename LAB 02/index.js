class Hand {
    constructor(length, width, color) {
        this.length = length;
        this.width = width;
        this.color = color;
    }
    draw(ctx) {
        ctx.beginPath();
        ctx.lineWidth = this.width;
        ctx.strokeStyle = this.color;
        ctx.lineCap = "round";
        ctx.moveTo(0, 0); ctx.lineTo(this.length, 0);
        ctx.stroke();
    }
}

class Clock {
    constructor(id) {
        this.ctx = document.getElementById(id).getContext('2d');
        this.paused = false;
        this.hands = {
            h: new Hand(150, 6, 'black'), m: new Hand(230, 4, 'black'), s: new Hand(240, 2, 'red')
        };
        window.addEventListener('keydown', e => e.code === 'Space' && (this.paused = !this.paused));
        this.loop();
    }
    loop() {
        if (!this.paused) this.draw();
        requestAnimationFrame(() => this.loop());
    }
    draw() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, 800, 800);
        ctx.save();
        ctx.translate(400, 400);

        ctx.font = '30px Arial bold';
        for(let i=1; i<=12; i++) {
            const angle = i * Math.PI / 6 - Math.PI / 2;
            const x = Math.cos(angle) * 200;
            const y = Math.sin(angle) * 200;
            ctx.fillText(i.toString(), x - 12, y + 8);
        }
        
    
    
        ctx.rotate(-Math.PI/2);
        ctx.save();

        // Pętla rysująca oznaczenia godzinowe
        for(let i=0; i<12; i++) {
            ctx.rotate(Math.PI/6);
            ctx.beginPath(); ctx.moveTo(220,0); ctx.lineTo(250,0); ctx.stroke();
        }

        // Rysowanie tarczy zegara
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'black';
        ctx.beginPath(); ctx.arc(0,0,280,0,Math.PI*2); ctx.stroke();
        ctx.beginPath(); ctx.arc(0,0,10,0,Math.PI*2); ctx.fill();
        ctx.restore();


        for(let i=0; i<60; i++) {
            ctx.rotate(Math.PI/30);
            ctx.beginPath(); ctx.moveTo(240,0); ctx.lineTo(250,0); ctx.stroke();
        }

    
        // Obliczanie aktualnego czasu
        const d = new Date();
        const s = d.getSeconds() + d.getMilliseconds()/1000;
        const m = d.getMinutes() + s/60;
        const h = d.getHours()%12 + m/60;

        // Rysowanie wskazówek
        this.drawHand(this.hands.h, h * Math.PI/6);
        this.drawHand(this.hands.m, m * Math.PI/30);
        this.drawHand(this.hands.s, s * Math.PI/30);
        
        ctx.restore();
        
    }
    drawHand(hand, angle) {
        this.ctx.save(); this.ctx.rotate(angle); hand.draw(this.ctx); this.ctx.restore();
    }
}
new Clock('ClockCanvas');
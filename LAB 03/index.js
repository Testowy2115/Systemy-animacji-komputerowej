class Particle {
    constructor(x, y, vx, vy, hue, alpha, decay, active){
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.hue = hue;
        this.alpha = alpha;
        this.decay = decay;
        this.active = active;
    }
    update(gravity, canvasHeight){
        this.x += this.vx;
        this.y += this.vy;
        this.alpha -= this.decay;
        this.vy += gravity;
        this.vx *= 0.98;
        this.vy *= 0.98;
        if(this.alpha <= 0){
            this.active = false;
        }
        if(this.y >= canvasHeight){
            this.vy *= -0.6;
            this.y = canvasHeight;
        }
    }
    draw(ctx){
        ctx.fillStyle = `hsla(${this.hue}, 100%, 50%, ${this.alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

class Firework {
    constructor(startX, startY, targetX, targetY){
        this.x = startX;
        this.y = startY;
        this.targetX = targetX;
        this.targetY = targetY;
        this.speed = 8;
        this.exploded = false;
        this.active = true;
        this.hue = Math.random() * 360;
    }
    update(){
        if(!this.exploded){
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.hypot(dx, dy);
            if(distance < 5){
                this.exploded = true;
                this.active = false;
            } else {
                const angle = Math.atan2(dy, dx);
                this.x += Math.cos(angle) * this.speed;
                this.y += Math.sin(angle) * this.speed;
            }
        }
    }
    draw(ctx){
        ctx.fillStyle = `hsl(${this.hue}, 100%, 50%)`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
        ctx.fill();
    }
    explode(particleCount){
        const particles = [];
        for(let i = 0; i < particleCount; i++){
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 5 + 2;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            const alpha = 1;
            const decay = Math.random() * 0.015 + 0.005;
            particles.push(new Particle(this.x, this.y, vx, vy, this.hue + (Math.random() * 5 - 20), alpha, decay, true));
        }
        return particles;
    }
}

class FireworkShow {
    constructor(canvasId){
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext("2d");
        
        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.particles = [];
        this.rockets = [];
        
        this.gravityInput = document.getElementById('gravity');
        this.countInput = document.getElementById('particleCount');

        this.autoShowBtn = document.getElementById('autoShow');
        this.autoShowActive = false;
        this.lastAutoLaunch = 0;

        this.autoShowBtn.addEventListener('click', () => {
             this.autoShowActive = !this.autoShowActive;
             this.autoShowBtn.textContent = this.autoShowActive ? 'Wyłącz Automatyczny Pokaz' : 'Włącz Automatyczny Pokaz';
        });

        this.canvas.addEventListener("click", (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.canvas.width / rect.width;
            const scaleY = this.canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            this.rockets.push(new Firework(this.canvas.width / 2, this.canvas.height, x, y));
        });

        this.update();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    update(){
        const gravity = parseFloat(this.gravityInput.value);
        const count = parseInt(this.countInput.value);

        if(this.autoShowActive && Date.now() - this.lastAutoLaunch > 800){
            this.rockets.push(new Firework(
                Math.random() * this.canvas.width, 
                this.canvas.height, 
                Math.random() * this.canvas.width, 
                Math.random() * (this.canvas.height / 2)
            ));
            this.lastAutoLaunch = Date.now();
       }

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        //this.ctx.globalCompositeOperation = 'darker';


        this.rockets.forEach(rocket => {
            rocket.update();
            rocket.draw(this.ctx);
            if(rocket.exploded){
                this.particles.push(...rocket.explode(count));
            }
        });
        
        this.particles.forEach(particle => {
            particle.vx *= 0.95;
            particle.update(gravity, this.canvas.height);
            particle.draw(this.ctx);
        });

        this.rockets = this.rockets.filter(r => r.active);
        this.particles = this.particles.filter(p => p.active);
        
        requestAnimationFrame(() => this.update());
    }  
}

new FireworkShow("FireworkCanvas");
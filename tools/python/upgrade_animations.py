import re

html_path = r'd:\VS project\cultural_technology\123\pre2_standalone.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS: 
css_injection = r'''
      .slide {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        transition: transform var(--transition) cubic-bezier(0.25, 1, 0.5, 1), opacity 800ms cubic-bezier(0.25, 1, 0.5, 1), filter var(--transition) cubic-bezier(0.25, 1, 0.5, 1);
        filter: blur(8px) saturate(0.95);
        overflow: hidden;
        border-radius: 24px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.12), 0 10px 30px rgba(0,0,0,0.06);
        background: rgba(255, 255, 255, 0.95);
        backface-visibility: hidden;
        will-change: transform, opacity, filter;
        transform-origin: center center;
      }
      
      .deck-shell {
        perspective: 1500px;
        transform-style: preserve-3d;
      }

      /* Apple-style smooth dynamic easing */
      :root {
          --transition: 0.9s;
      }

      .slide.active {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale(1) rotateX(0) rotateY(0);
        filter: blur(0px) saturate(1);
        z-index: 4;
      }

      /* --- Animation Mode: Flow --- */
      .anim-flow .slide.leaving-next {
        opacity: 0;
        transform: translate3d(-10%, 0, -250px) rotateY(5deg) scale(0.9);
        filter: blur(12px);
      }
      .anim-flow .slide.leaving-prev {
        opacity: 0;
        transform: translate3d(10%, 0, -250px) rotateY(-5deg) scale(0.9);
        filter: blur(12px);
      }
      .anim-flow .slide.entering-next {
        transform: translate3d(10%, 0, -250px) rotateY(-5deg) scale(0.9);
      }
      .anim-flow .slide.entering-prev {
        transform: translate3d(-10%, 0, -250px) rotateY(5deg) scale(0.9);
      }

      /* --- Animation Mode: Cube --- */
      .anim-cube .slide.leaving-next {
        opacity: 0;
        transform: translate3d(-50%, 0, -500px) rotateY(-90deg);
        filter: blur(5px);
      }
      .anim-cube .slide.leaving-prev {
        opacity: 0;
        transform: translate3d(50%, 0, -500px) rotateY(90deg);
        filter: blur(5px);
      }
      .anim-cube .slide.entering-next {
        transform: translate3d(50%, 0, -500px) rotateY(90deg);
      }
      .anim-cube .slide.entering-prev {
        transform: translate3d(-50%, 0, -500px) rotateY(-90deg);
      }

      /* --- Animation Mode: Rise --- */
      .anim-rise .slide.leaving-next {
        opacity: 0;
        transform: translate3d(0, -20%, -300px) rotateX(-10deg) scale(0.9);
        filter: blur(10px);
      }
      .anim-rise .slide.leaving-prev {
        opacity: 0;
        transform: translate3d(0, 20%, -300px) rotateX(10deg) scale(0.9);
        filter: blur(10px);
      }
      .anim-rise .slide.entering-next {
        transform: translate3d(0, 20%, -300px) rotateX(10deg) scale(0.9);
      }
      .anim-rise .slide.entering-prev {
        transform: translate3d(0, -20%, -300px) rotateX(-10deg) scale(0.9);
      }

      /* Base Fallback */
      .slide.leaving-next, .slide.leaving-prev, .slide.entering-next, .slide.entering-prev {
        z-index: 3;
      }
'''

html_modified = re.sub(r'\.slide \{.*?\n      \}', '', html, flags=re.DOTALL)
html_modified = re.sub(r'\.slide\.active \{.*?\n      \}', '', html_modified, flags=re.DOTALL)
html_modified = re.sub(r'\.slide\.leaving-next \{.*?\n      \}', '', html_modified, flags=re.DOTALL)
html_modified = re.sub(r'\.slide\.leaving-prev \{.*?\n      \}', '', html_modified, flags=re.DOTALL)
html_modified = re.sub(r'\.slide\.entering-next \{.*?\n      \}', '', html_modified, flags=re.DOTALL)
html_modified = re.sub(r'\.slide\.entering-prev \{.*?\n      \}', '', html_modified, flags=re.DOTALL)

# Insert new css
html_modified = html_modified.replace('.deck-shell {', css_injection + '\n      .deck-shell {')


# 2. Update JS goTo function:
js_injection = r'''
      const animations = ['anim-flow', 'anim-cube', 'anim-rise'];
      
      function setInitial() {
        slides.forEach((sl, i) => {
          sl.classList.remove('active', 'leaving-next', 'leaving-prev');
          if (i === current) sl.classList.add('active');
        });
        syncCounter();
      }

      function goTo(index) {
        if (animating) return;
        if (index < 0 || index >= slides.length || index === current) return;   

        animating = true;
        const oldIndex = current;
        const dir = index > oldIndex ? 'next' : 'prev';
        const oldSlide = slides[oldIndex];
        const newSlide = slides[index];
        
        const randomAnim = animations[Math.floor(Math.random() * animations.length)];
        
        // Remove animation markers
        deck.classList.remove(...animations);
        // Apply random transition mode
        deck.classList.add(randomAnim);

        newSlide.classList.remove('active', 'leaving-next', 'leaving-prev', 'entering-next', 'entering-prev');    
        newSlide.classList.add(dir === 'next' ? 'entering-next' : 'entering-prev');

        requestAnimationFrame(() => {
          // slight delay for browser calculation
          requestAnimationFrame(() => {
            oldSlide.classList.remove('active', 'entering-next', 'entering-prev');
            oldSlide.classList.add(dir === 'next' ? 'leaving-next' : 'leaving-prev');

            newSlide.classList.remove('entering-next', 'entering-prev');
            newSlide.classList.add('active');
          });
        });

        window.setTimeout(() => {
          oldSlide.classList.remove('leaving-next', 'leaving-prev');
          current = index;
          syncCounter();
          animating = false;
        }, 950);
      }
'''

html_modified = re.sub(r'function goTo\(index\) \{.*?\}, 900\);\s*\}', js_injection, html_modified, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_modified)

print('Apple style animation upgraded!')

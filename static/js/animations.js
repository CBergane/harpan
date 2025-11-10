// =============================================================================
// HARPANS ANIMATIONS - animations.js
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // =========================================================================
    // 1. FADE-IN SCROLL ANIMATION
    // =========================================================================
    // Element "fader in" när de kommer i viewport
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                fadeObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Applicera på alla element med .fade-in-scroll
    document.querySelectorAll('.fade-in-scroll').forEach(el => {
        fadeObserver.observe(el);
    });

    
    // =========================================================================
    // 2. PARALLAX EFFECT
    // =========================================================================
    // Bakgrund rör sig långsammare än förgrund
    let ticking = false;

    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const parallaxElements = document.querySelectorAll('.parallax');
                const scrolled = window.pageYOffset;
                
                parallaxElements.forEach(el => {
                    const speed = el.dataset.speed || 0.5;
                    el.style.transform = `translateY(${scrolled * speed}px)`;
                });
                
                ticking = false;
            });
            ticking = true;
        }
    });

    
    // =========================================================================
    // 3. SMOOTH SCROLL
    // =========================================================================
    // Mjuk scrolling för interna länkar
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    
    // =========================================================================
    // 4. COUNT-UP ANIMATION
    // =========================================================================
    // Räknar upp siffror från 0
    function countUp(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        function updateCount() {
            start += increment;
            if (start < target) {
                element.textContent = Math.floor(start);
                requestAnimationFrame(updateCount);
            } else {
                element.textContent = target;
            }
        }
        
        updateCount();
    }

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.target);
                countUp(entry.target, target);
                statsObserver.unobserve(entry.target);
            }
        });
    });

    document.querySelectorAll('.count-up').forEach(el => {
        statsObserver.observe(el);
    });

    
    // =========================================================================
    // 5. MAGNETIC BUTTON EFFECT
    // =========================================================================
    // Knappar "följer" muspekaren lite
    document.querySelectorAll('.magnetic-btn').forEach(btn => {
        btn.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            this.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
            this.style.transition = 'transform 0.1s ease';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translate(0, 0)';
            this.style.transition = 'transform 0.3s ease';
        });
    });

    
    // =========================================================================
    // 6. STAGGER ANIMATION (för dynamiska listor)
    // =========================================================================
    // Lägg till stagger-delay på barn-element
    document.querySelectorAll('.stagger-container').forEach(container => {
        const items = container.querySelectorAll('.stagger-item');
        items.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
        });
    });

});

// Lucide icons refresh (för dynamiskt innehåll)
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}
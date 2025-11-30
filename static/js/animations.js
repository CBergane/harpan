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

(function () {
  function initLucide() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  // Run after DOM is ready
  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  onReady(function () {
    initLucide();

    // Re-init icons after HTMX swaps
    document.body.addEventListener("htmx:afterSwap", initLucide);

    /* -----------------------------
       Drawer (hamburger -> left)
    ------------------------------ */
    (function () {
      const openBtn  = document.getElementById("drawer-open");
      const closeBtn = document.getElementById("drawer-close");
      const overlay  = document.getElementById("drawer-overlay");
      const drawer   = document.getElementById("nav-drawer");

      if (!openBtn || !closeBtn || !overlay || !drawer) return;

      function openDrawer() {
        drawer.classList.remove("-translate-x-full");
        overlay.classList.remove("opacity-0", "pointer-events-none");
        overlay.classList.add("opacity-100");
        document.body.style.overflow = "hidden";
        drawer.setAttribute("aria-hidden", "false");
        openBtn.setAttribute("aria-expanded", "true");
      }

      function closeDrawer() {
        drawer.classList.add("-translate-x-full");
        overlay.classList.add("opacity-0", "pointer-events-none");
        overlay.classList.remove("opacity-100");
        document.body.style.overflow = "";
        drawer.setAttribute("aria-hidden", "true");
        openBtn.setAttribute("aria-expanded", "false");
        openBtn.focus();
      }

      openBtn.addEventListener("click", function (e) {
        e.preventDefault();
        openDrawer();
      });

      closeBtn.addEventListener("click", closeDrawer);
      overlay.addEventListener("click", closeDrawer);

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeDrawer();
      });
    })();

    /* -----------------------------
       Wordmark docking on scroll
       - Centered over hero
       - Docks to #wordmark-target when hero is out of view
    ------------------------------ */
    (function () {
      const wordmark = document.getElementById("brand-wordmark");
      const hero = document.querySelector("[data-hero]");
      const target = document.getElementById("wordmark-target");
      const nav = document.querySelector("nav");

      if (!wordmark) return;

      let docked = false;

      function setCentered() {
        docked = false;
        wordmark.classList.remove("is-docked");
        wordmark.style.left = "50%";

        const navH = nav ? nav.getBoundingClientRect().height : 80;
        // place just below nav (tweak-friendly)
        wordmark.style.top = Math.round(navH + 56) + "px";

        wordmark.style.transform = "translateX(-50%)";
      }

      function setDocked() {
        docked = true;
        wordmark.classList.add("is-docked");

        if (!target) {
          // fallback: top-left-ish
          wordmark.style.left = "5.5rem";
          wordmark.style.top = "1.05rem";
          wordmark.style.transform = "translate(0,0)";
          return;
        }

        const r = target.getBoundingClientRect();
        // Slight Y tweak so the text sits nicer next to icon
        const yTweak = -6;

        wordmark.style.left = Math.round(r.left) + "px";
        wordmark.style.top  = Math.round(r.top + yTweak) + "px";
        wordmark.style.transform = "translate(0,0)";
      }

      function updateDockPosition() {
        if (docked) setDocked();
        else setCentered();
      }

      // If there is no hero on this page -> start docked (keeps layout clean)
      if (!hero) {
        setDocked();
        window.addEventListener("resize", function () {
          window.requestAnimationFrame(updateDockPosition);
        });
        return;
      }

      // Preferred: IntersectionObserver
      if ("IntersectionObserver" in window) {
        const io = new IntersectionObserver(
          function ([entry]) {
            if (entry.isIntersecting) setCentered();
            else setDocked();
          },
          { threshold: 0.25 }
        );
        io.observe(hero);
      } else {
        // Fallback: scroll threshold
        const threshold = 220;
        function onScroll() {
          const scrolled = window.pageYOffset || document.documentElement.scrollTop;
          if (scrolled > threshold) setDocked();
          else setCentered();
        }
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
      }

      // Keep position correct on resize
      window.addEventListener("resize", function () {
        window.requestAnimationFrame(updateDockPosition);
      });

      // Initial placement
      setCentered();
    })();

    /* -----------------------------
       Scroll-to-top behavior
    ------------------------------ */
    (function () {
      const scrollBtn = document.getElementById("scroll-to-top");
      if (!scrollBtn) return;

      function updateScrollButton() {
        const scrolled = window.pageYOffset || document.documentElement.scrollTop;

        if (scrolled > 300) {
          scrollBtn.classList.remove("opacity-0", "invisible", "translate-y-2");
          scrollBtn.classList.add("opacity-100", "visible", "translate-y-0");
        } else {
          scrollBtn.classList.remove("opacity-100", "visible", "translate-y-0");
          scrollBtn.classList.add("opacity-0", "invisible", "translate-y-2");
        }
      }

      scrollBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });

      let ticking = false;
      window.addEventListener(
        "scroll",
        function () {
          if (!ticking) {
            window.requestAnimationFrame(function () {
              updateScrollButton();
              ticking = false;
            });
            ticking = true;
          }
        },
        { passive: true }
      );

      updateScrollButton();
    })();

    /* -----------------------------
       Callback sidebar (your existing behavior)
    ------------------------------ */
    (function () {
      const trigger  = document.getElementById("callback-trigger");
      const sidebar  = document.getElementById("callback-sidebar");
      const content  = document.getElementById("callback-modal-content");
      const btnClose = document.getElementById("callback-close");
      const firstInp = document.getElementById("modal-callback-name");

      if (!trigger || !sidebar || !content || !btnClose) return;

      function openSidebar() {
        sidebar.classList.remove("translate-x-full");
        content.classList.remove("opacity-0", "scale-95");
        content.classList.add("opacity-100", "scale-100");
        document.body.style.overflow = "hidden";
        sidebar.setAttribute("aria-hidden", "false");
        trigger.setAttribute("aria-expanded", "true");
        setTimeout(() => firstInp?.focus({ preventScroll: true }), 200);
      }

      function closeSidebar() {
        content.classList.add("opacity-0", "scale-95");
        content.classList.remove("opacity-100", "scale-100");
        sidebar.classList.add("translate-x-full");
        document.body.style.overflow = "";
        sidebar.setAttribute("aria-hidden", "true");
        trigger.setAttribute("aria-expanded", "false");
        trigger.focus();
      }

      trigger.addEventListener("click", function (e) {
        e.preventDefault();
        openSidebar();
      });

      btnClose.addEventListener("click", closeSidebar);

      sidebar.addEventListener("click", function (e) {
        if (e.target === sidebar) closeSidebar();
      });

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeSidebar();
      });
    })();
  });
})();

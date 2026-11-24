/**
 * ==========================================================================
 * Fahad Usman Portfolio - Main Interaction Scripts
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {

  // =======================================================
  // 1. LENIS SMOOTH SCROLL & GSAP SCROLLTRIGGER SYNC
  // =======================================================
  const lenis = new Lenis({
    duration: 1.25,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    wheelMultiplier: 1.05,
    touchMultiplier: 1.5,
  });

  // Sinkronisasi update posisi ScrollTrigger dengan Lenis scroll loop
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });
  gsap.ticker.lagSmoothing(0);

  // Smooth scroll untuk semua anchor links (#)
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetEl = document.querySelector(targetId);
        if (targetEl) {
          e.preventDefault();
          lenis.scrollTo(targetEl, { offset: -85, duration: 1.2 });
        }
      }
    });
  });

  // =======================================================
  // 2. GSAP + SCROLLTRIGGER: JUDUL MUNCUL PER KATA (WORD REVEAL)
  // =======================================================
  gsap.registerPlugin(ScrollTrigger);

  function initWordRevealAnimation() {
    const headingTargets = document.querySelectorAll(
      '#tentang h1, section h2, #karya h3'
    );

    headingTargets.forEach((heading) => {
      if (heading.dataset.splitDone) return;
      heading.dataset.splitDone = "true";

      const rawText = heading.innerText.trim();
      if (!rawText) return;

      const words = rawText.split(/\s+/);
      heading.innerHTML = words
        .map(
          (w) =>
            `<span class="word-wrapper"><span class="word-reveal">${w}</span></span>`
        )
        .join('');

      const wordSpans = heading.querySelectorAll('.word-reveal');

      gsap.to(wordSpans, {
        y: '0%',
        opacity: 1,
        rotateZ: 0,
        duration: 0.8,
        stagger: 0.04,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: heading,
          start: 'top 88%',
          toggleActions: 'play none none none',
        },
      });
    });

    // Animasi halus untuk pill / badge judul section saat di-scroll
    document.querySelectorAll('section .inline-flex.items-center.gap-2').forEach((badge) => {
      gsap.from(badge, {
        opacity: 0,
        y: 16,
        scale: 0.94,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: badge,
          start: 'top 90%',
          toggleActions: 'play none none none',
        },
      });
    });
  }

  initWordRevealAnimation();

  // =======================================================
  // 3. MOTION: ANIMASI MASUK CARD (INVIEW) & HOVER EFFECTS
  // =======================================================
  function initMotionCardAnimations() {
    if (typeof Motion === 'undefined') return;

    const cards = document.querySelectorAll('.bento-card');

    cards.forEach((card, index) => {
      // Set initial entrance state
      card.style.opacity = '0';
      card.style.transform = 'translateY(36px) scale(0.97)';

      // Animasi masuk card menggunakan Motion inView
      Motion.inView(
        card,
        () => {
          Motion.animate(
            card,
            {
              opacity: [0, 1],
              transform: ['translateY(36px) scale(0.97)', 'translateY(0px) scale(1)'],
            },
            {
              duration: 0.7,
              delay: (index % 3) * 0.1,
              easing: [0.16, 1, 0.3, 1], // Apple-style spring/ease-out
            }
          );
        },
        { amount: 0.12 }
      );

      // Efek interaktif hover card menggunakan Motion
      card.addEventListener('mouseenter', () => {
        Motion.animate(
          card,
          {
            transform: 'translateY(-7px) scale(1.012)',
            boxShadow: '0 24px 40px -12px rgba(15, 23, 42, 0.12), 0 0 0 1.5px rgba(99, 102, 241, 0.28)',
          },
          {
            duration: 0.32,
            easing: [0.16, 1, 0.3, 1],
          }
        );
      });

      card.addEventListener('mouseleave', () => {
        Motion.animate(
          card,
          {
            transform: 'translateY(0px) scale(1)',
            boxShadow: '0 2px 8px -2px rgba(15, 23, 42, 0.04), 0 12px 24px -4px rgba(15, 23, 42, 0.04)',
          },
          {
            duration: 0.45,
            easing: [0.16, 1, 0.3, 1],
          }
        );
      });
    });

    // Animasi masuk untuk Polaroid Card di Hero
    const polaroidHero = document.querySelector('.shadow-polaroid');
    if (polaroidHero) {
      Motion.animate(
        polaroidHero,
        {
          opacity: [0, 1],
          transform: ['rotate(-5deg) scale(0.92)', 'rotate(-2deg) scale(1)'],
        },
        {
          duration: 1,
          delay: 0.2,
          easing: [0.16, 1, 0.3, 1],
        }
      );
    }
  }

  initMotionCardAnimations();

  // =======================================================
  // 4. Update Tahun Copyright Otomatis
  // =======================================================
  const yearEl = document.getElementById('current-year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // =======================================================
  // 5. Salin Email ke Clipboard
  // =======================================================
  const copyEmailBtn = document.getElementById('copy-email-btn');
  const copyTextStatus = document.getElementById('copy-text-status');
  const emailAddressText = document.getElementById('email-address-text');

  if (copyEmailBtn && emailAddressText && copyTextStatus) {
    copyEmailBtn.addEventListener('click', async () => {
      const email = emailAddressText.textContent.trim();
      try {
        await navigator.clipboard.writeText(email);
        copyTextStatus.textContent = 'Alamat Tersalin! ✓';
        copyTextStatus.classList.add('text-emerald-600');
        setTimeout(() => {
          copyTextStatus.textContent = 'Salin Alamat Email';
          copyTextStatus.classList.remove('text-emerald-600');
        }, 3000);
      } catch (err) {
        const tempInput = document.createElement('input');
        tempInput.value = email;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        copyTextStatus.textContent = 'Alamat Tersalin! ✓';
        setTimeout(() => {
          copyTextStatus.textContent = 'Salin Alamat Email';
        }, 3000);
      }
    });
  }

  // =======================================================
  // 6. Submit Formulir Kontak Terhubung ke WhatsApp
  // =======================================================
  const collabForm = document.getElementById('collab-form');
  const formFeedback = document.getElementById('form-feedback');
  const submitBtn = document.getElementById('submit-collab-btn');

  if (collabForm && formFeedback && submitBtn) {
    collabForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('contact-name').value;
      const email = document.getElementById('contact-email').value;
      const topic = document.getElementById('project-topic').value;
      const message = document.getElementById('contact-message').value;
      const phoneWA = "6281317768135";

      // Animasi tombol loading
      const originalBtnContent = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        Mengarahkan ke WhatsApp...
      `;

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;

        // Format WhatsApp Link
        const waEncoded = encodeURIComponent(`Halo Fahad Usman,\n\nPerkenalkan saya ${name} (${email}).\nSaya ingin berdiskusi mengenai: ${topic}.\n\nCatatan:\n${message}`);
        const waUrl = `https://wa.me/${phoneWA}?text=${waEncoded}`;

        // Tampilkan Feedback Sukses
        formFeedback.classList.remove('hidden');
        formFeedback.classList.add('flex');

        document.getElementById('form-feedback-text').innerHTML = `
          Terima kasih <strong>${name}</strong>! Jika WhatsApp tidak terbuka otomatis, silakan 
          <a href="${waUrl}" target="_blank" class="underline font-bold text-emerald-800 hover:text-emerald-950">klik di sini untuk membuka WhatsApp ↗</a>.
        `;

        // Buka tab WhatsApp
        window.open(waUrl, "_blank", "noopener,noreferrer");

        // Reset form
        collabForm.reset();
      }, 600);
    });
  }

  // =======================================================
  // 7. Active Link Spy Saat Scroll (Desktop & Mobile Tabs)
  // =======================================================
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  const bottomTabLinks = document.querySelectorAll('.bottom-tab-link');

  window.addEventListener('scroll', () => {
    let current = '';
    const scrollPosition = window.scrollY + 130;

    sections.forEach((section) => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    // Update active state pada desktop nav links
    navLinks.forEach((link) => {
      link.classList.remove('text-brand-600', 'bg-white', 'shadow-sm');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('text-brand-600', 'bg-white', 'shadow-sm');
      }
    });

    // Update active state pada mobile bottom tab bar
    bottomTabLinks.forEach((tab) => {
      if (tab.getAttribute('href') === `#${current}`) {
        tab.classList.remove('text-slate-500');
        tab.classList.add('text-brand-600', 'bg-brand-50/90', 'font-bold');
      } else {
        tab.classList.remove('text-brand-600', 'bg-brand-50/90', 'font-bold');
        tab.classList.add('text-slate-500');
      }
    });

  });

  // =======================================================
  // 8. DESKTOP FLOATING PILL: AUTO COLLAPSE ON SCROLL & CLICK TO EXPAND
  // =======================================================
  const pillContainer = document.getElementById('desktop-pill-container');
  const desktopBrandBtn = document.getElementById('desktop-brand-btn');
  const desktopCloseBtn = document.getElementById('desktop-pill-close-btn');
  const desktopNavLinks = document.querySelectorAll('#desktop-nav-menu .nav-link');
  const desktopCtaLink = document.querySelector('#desktop-right-group a');

  let isDesktopScrolled = false;
  let isPillExpandedManually = false;

  function updateDesktopPillState() {
    const isDesktop = window.innerWidth >= 768;
    if (!isDesktop || !pillContainer) return;

    const currentScrollY = window.scrollY;

    // Posisi di paling atas (scrollY <= 80): Navbar Terbuka Normal
    if (currentScrollY <= 80) {
      isDesktopScrolled = false;
      isPillExpandedManually = false;

      pillContainer.classList.remove('is-collapsed');
      pillContainer.classList.add('is-expanded');

      if (desktopCloseBtn) {
        desktopCloseBtn.classList.add('hidden');
        desktopCloseBtn.classList.remove('inline-flex');
      }
    } 
    // Posisi di-scroll ke bawah (scrollY > 80)
    else {
      isDesktopScrolled = true;

      // Jika user klik brand / pill untuk membuka navigasi saat posisi scroll
      if (isPillExpandedManually) {
        pillContainer.classList.remove('is-collapsed');
        pillContainer.classList.add('is-expanded');

        if (desktopCloseBtn) {
          desktopCloseBtn.classList.remove('hidden');
          desktopCloseBtn.classList.add('inline-flex');
        }
      } 
      // Default saat scroll: TERTUTUP (HANYA tulisan "Fahad. Web Dev")
      else {
        pillContainer.classList.remove('is-expanded');
        pillContainer.classList.add('is-collapsed');

        if (desktopCloseBtn) {
          desktopCloseBtn.classList.add('hidden');
          desktopCloseBtn.classList.remove('inline-flex');
        }
      }
    }
  }

  // Klik tombol Brand "Fahad. Web Dev"
  if (desktopBrandBtn) {
    desktopBrandBtn.addEventListener('click', (e) => {
      if (window.innerWidth < 768) return;
      if (isDesktopScrolled) {
        e.stopPropagation();
        isPillExpandedManually = !isPillExpandedManually;
        updateDesktopPillState();
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  // Klik sembarang area pill saat tertutup untuk membuka
  if (pillContainer) {
    pillContainer.addEventListener('click', (e) => {
      if (window.innerWidth < 768) return;
      if (isDesktopScrolled && !isPillExpandedManually) {
        e.stopPropagation();
        isPillExpandedManually = true;
        updateDesktopPillState();
      }
    });
  }

  // Tombol Tutup (✕) saat navbar dibuka di posisi scroll
  if (desktopCloseBtn) {
    desktopCloseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      isPillExpandedManually = false;
      updateDesktopPillState();
    });
  }

  // Saat tautan navbar diklik di posisi scroll, tutup kembali ke tulisan ringkas
  desktopNavLinks.forEach((link) => {
    link.addEventListener('click', () => {
      if (isDesktopScrolled) {
        isPillExpandedManually = false;
        updateDesktopPillState();
      }
    });
  });

  if (desktopCtaLink) {
    desktopCtaLink.addEventListener('click', () => {
      if (isDesktopScrolled) {
        isPillExpandedManually = false;
        updateDesktopPillState();
      }
    });
  }

  // Klik di luar navbar untuk menutup kembali jika sedang terbuka di posisi scroll
  document.addEventListener('click', (e) => {
    if (window.innerWidth >= 768 && isDesktopScrolled && isPillExpandedManually) {
      if (pillContainer && !pillContainer.contains(e.target)) {
        isPillExpandedManually = false;
        updateDesktopPillState();
      }
    }
  });

  // Dengarkan event resize dan scroll
  window.addEventListener('resize', updateDesktopPillState);
  window.addEventListener('scroll', updateDesktopPillState, { passive: true });
  updateDesktopPillState();

});

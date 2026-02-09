      // Update Tahun Footer
      document.getElementById('year').textContent = new Date().getFullYear();

      // Mobile Menu Logic
      const btn = document.getElementById('mobile-menu-btn');
      const menu = document.getElementById('mobile-menu');

      btn.addEventListener('click', () => {
        menu.classList.toggle('hidden');
        menu.classList.toggle('flex');
      });

      // Menutup menu saat link diklik
      document.querySelectorAll('#mobile-menu a').forEach(link => {
        link.addEventListener('click', () => {
          menu.classList.add('hidden');
          menu.classList.remove('flex');
        });
      });
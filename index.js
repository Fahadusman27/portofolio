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
      
function kirimWA() {
  const nama = document.getElementById("nama").value;
  const pesan = document.getElementById("pesan").value;
  const email = document.getElementById("email").value;
  const nomor = "6281317768135";

  const textWA = `Halo Fahad, perkenalkan nama saya ${nama} (${email}).%0A%0A${pesan}`;
  
  const url = `https://wa.me/${nomor}?text=${textWA}`;
  
  window.open(url, "_blank");
}

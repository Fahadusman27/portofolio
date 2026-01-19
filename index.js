const menuToggle = document.getElementById("mobile-menu");
const navList = document.getElementById("nav-list");

// Buka/Tutup menu saat tombol hamburger diklik
menuToggle.addEventListener("click", (e) => {
  menuToggle.classList.toggle("active");
  navList.classList.toggle("active");
});

// Fungsi untuk menutup menu (dipakai saat link diklik atau klik di luar menu)
function closeMenu() {
  menuToggle.classList.remove("active");
  navList.classList.remove("active");
}

// Tambahan: Menutup menu jika user mengklik area di luar menu dropdown
window.addEventListener("click", (e) => {
  if (!menuToggle.contains(e.target) && !navList.contains(e.target)) {
    closeMenu();
  }
});

document.getElementById("year").textContent = new Date().getFullYear();
function kirimWA() {
  const nama = document.getElementById("Fahad Usman").value;
  const pesan = document.getElementById("Ada yang bisa di ba").value;
  const nomor = "6281317768135";

  const url = `https://wa.me/${nomor}?text=Halo Fahad, nama saya ${nama}. %0A%0A${pesan}`;
  window.open(url, "_blank");
}

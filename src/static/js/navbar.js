const htmlElement = document.documentElement;

// 1. FUNCIÓN PARA ACTUALIZAR LOS ICONOS (SOL/LUNA)
function updateThemeIcons() {
    const isDark = htmlElement.classList.contains('dark');
    const darkIcons = document.querySelectorAll('#theme-toggle-dark-icon, .dark-icon-m');
    const lightIcons = document.querySelectorAll('#theme-toggle-light-icon, .light-icon-m');

    darkIcons.forEach(i => isDark ? i.classList.add('hidden') : i.classList.remove('hidden'));
    lightIcons.forEach(i => isDark ? i.classList.remove('hidden') : i.classList.add('hidden'));
}

// 2. LÓGICA DE CLIC EN LOS BOTONES
document.querySelectorAll('#theme-toggle, #theme-toggle-mobile').forEach(btn => {
    btn.addEventListener('click', () => {
        if (htmlElement.classList.contains('dark')) {
            htmlElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        } else {
            htmlElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        }
        updateThemeIcons();
    });
});

// 3. EJECUCIÓN INICIAL (IMPORTANTE: Esto es lo que te faltaba)
// Al cargar cualquier página, comprobamos qué hay guardado
const savedTheme = localStorage.getItem('color-theme');
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    htmlElement.classList.add('dark');
} else {
    htmlElement.classList.remove('dark');
}

// Lanzamos una vez al cargar para que los iconos coincidan con el tema aplicado
updateThemeIcons();

// 4. CONTROL MENÚ MÓVIL (Hamburguesa)
const mobileBtn = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}
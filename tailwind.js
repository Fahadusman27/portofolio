tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'monospace'],
            },
            colors: {
                brand: {
                    50: '#EEF2FF',
                    100: '#E0E7FF',
                    200: '#C7D2FE',
                    300: '#A5B4FC',
                    400: '#818CF8',
                    500: '#6366F1',
                    600: '#4F46E5', // Primary Royal Indigo
                    700: '#4338CA',
                    800: '#3730A3',
                    900: '#312E81',
                },
                surface: {
                    50: '#F8FAFC', // Slate 50 Off-white
                    100: '#F1F5F9',
                    200: '#E2E8F0',
                },
                pastel: {
                    emerald: '#ECFDF5',
                    'emerald-text': '#047857',
                    'emerald-border': '#A7F3D0',
                    blue: '#EFF6FF',
                    'blue-text': '#1D4ED8',
                    'blue-border': '#BFDBFE',
                    purple: '#FAF5FF',
                    'purple-text': '#6D28D9',
                    'purple-border': '#E9D5FF',
                    amber: '#FFFBEB',
                    'amber-text': '#B45309',
                    'amber-border': '#FDE68A',
                }
            },
            boxShadow: {
                'bento': '0 2px 8px -2px rgba(15, 23, 42, 0.04), 0 12px 24px -4px rgba(15, 23, 42, 0.04)',
                'bento-hover': '0 12px 32px -4px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(79, 70, 229, 0.05)',
                'polaroid': '0 20px 35px -10px rgba(15, 23, 42, 0.12), 0 8px 16px -6px rgba(15, 23, 42, 0.06)',
            }
        }
    }
};
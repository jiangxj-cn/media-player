export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#7c3aed',
        bg: {
          primary: '#0f0f0f',
          secondary: '#1a1a1a',
          card: '#1f1f1f',
        }
      }
    }
  }
}

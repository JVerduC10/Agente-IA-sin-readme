# Jarvis Analyst - React Frontend

🚀 **Conversational Analytics, Zero Friction** - A modern React frontend for the Jarvis Analyst AI-powered data analytics platform.

## ✨ Features

- **🎨 Modern UI/UX**: FlowautoMate-inspired design with Trust Blue & Teal gradients
- **🌙 Dark/Light Mode**: Automatic theme detection with manual toggle
- **💬 AI Chat Interface**: Natural language queries with instant responses
- **📱 Responsive Design**: Mobile-first approach with Tailwind CSS
- **⚡ Performance Optimized**: Vite build system with code splitting
- **🎭 Micro-interactions**: Framer Motion animations and transitions
- **♿ Accessibility**: WCAG 2.1 AA compliant with keyboard navigation

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Backend**: FastAPI (existing)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.10+ (for backend)
- Groq API key

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the backend** (in separate terminal):
   ```bash
   # Install Python dependencies if not done
   pip install -r requirements.txt
   
   # Start FastAPI server
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start the React development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # shadcn/ui base components
│   ├── Header.tsx      # Navigation header
│   ├── Hero.tsx        # Landing hero section
│   ├── Features.tsx    # Features grid
│   ├── FeatureCard.tsx # Individual feature cards
│   ├── VideoSection.tsx# Demo video section
│   ├── ChatSection.tsx # Chat interface section
│   ├── ChatWidget.tsx  # Main chat component
│   └── Footer.tsx      # Site footer
├── hooks/              # Custom React hooks
│   └── useDarkMode.ts  # Dark mode management
├── lib/                # Utilities
│   └── utils.ts        # Class name utilities
├── App.tsx             # Main app component
├── main.tsx           # React entry point
└── index.css          # Global styles
```

## 🎨 Design System

### Color Palette

```css
/* Brand Colors */
--brand-blue: #1565C0    /* Headers, links */
--brand-teal: #1DBFAC    /* Gradients, badges */
--cta-orange: #FF8F00    /* CTA buttons */
--surface-light: #F6F8FC /* Light backgrounds */
--surface-dark: #0F172A  /* Dark backgrounds */
--text-primary: #1E293B  /* Primary text */
```

### Typography

- **Font**: Inter (preloaded)
- **Headings**: 700 weight, brand gradient
- **Body**: 400 weight, readable line height
- **UI**: 500-600 weight for buttons/labels

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint

# Backend (Python)
python -m uvicorn app.main:app --reload  # Start API server
python -m pytest -v                      # Run tests
```

## 🌐 Environment Variables

```bash
# Required
VITE_API_URL=http://localhost:8000  # Backend API URL
GROQ_API_KEY=your_groq_api_key      # Groq API key (backend)

# Optional
VITE_DEV_MODE=true                  # Enable dev features
VITE_ENABLE_CHAT=true              # Enable chat widget
VITE_ANALYTICS_ID=                  # Analytics tracking ID
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px (1 column)
- **Tablet**: 640px - 1024px (2 columns)
- **Desktop**: > 1024px (3 columns)
- **Large**: > 1280px (optimized layout)

## ♿ Accessibility Features

- **Keyboard Navigation**: Full tab support
- **Screen Readers**: ARIA labels and descriptions
- **Color Contrast**: WCAG AA compliant (4.5:1+)
- **Reduced Motion**: Respects `prefers-reduced-motion`
- **Focus Indicators**: Visible focus states

## 🚀 Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Font Preloading**: Inter font preloaded
- **Image Optimization**: SVG icons, optimized assets
- **Bundle Analysis**: Vite bundle analyzer
- **Tree Shaking**: Unused code elimination

## 🧪 Testing

```bash
# Backend tests
python -m pytest -v

# Frontend tests (when implemented)
npm run test
```

## 📦 Deployment

### Frontend (Vercel/Netlify)

```bash
npm run build
# Deploy dist/ folder
```

### Backend (Railway/Heroku)

```bash
# Use existing FastAPI deployment
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@jarvisanalyst.com

---

**Made with ❤️ for data teams** | © 2024 Jarvis Analyst
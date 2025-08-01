import { useState, useEffect } from 'react'
import { Header, Footer, Hero, Features, VideoSection, ChatSection } from './components'
import { useTheme } from './context'

function App() {
  const { isDark, toggleDark } = useTheme()
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-teal"></div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
      <Header isDark={isDark} toggleDark={toggleDark} />
      <main>
        <Hero />
        <Features />
        <VideoSection />
        <ChatSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
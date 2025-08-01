import { motion } from 'framer-motion'
import { Play, Volume2 } from 'lucide-react'
import { useState } from 'react'

export default function VideoSection() {
  const [isPlaying, setIsPlaying] = useState(false)

  return (
    <section id="video" className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            See{' '}
            <span className="bg-gradient-to-r from-brand-blue to-brand-teal bg-clip-text text-transparent">
              Jarvis Analyst
            </span>
            {' '}in Action
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Watch how easy it is to get insights from your data with natural language queries. 
            No SQL, no complex dashboards – just ask and get answers.
          </p>
        </motion.div>

        {/* Video Container */}
        <motion.div
          className="max-w-5xl mx-auto"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="relative aspect-video rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-brand-blue/10 to-brand-teal/10">
            {!isPlaying ? (
              // Video Thumbnail
              <div className="absolute inset-0 bg-gradient-to-br from-brand-blue to-brand-teal flex items-center justify-center">
                <div className="text-center">
                  <motion.button
                    className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mb-6 mx-auto hover:bg-white/30 transition-colors duration-300"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsPlaying(true)}
                  >
                    <Play className="h-10 w-10 text-white ml-1" fill="currentColor" />
                  </motion.button>
                  <h3 className="text-2xl font-semibold text-white mb-2">
                    Product Demo
                  </h3>
                  <p className="text-white/80 text-lg">
                    3 minutes • See how it works
                  </p>
                </div>
                
                {/* Floating Elements */}
                <motion.div
                  className="absolute top-8 left-8 bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2 text-white text-sm"
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <Volume2 className="h-4 w-4 inline mr-2" />
                  Audio included
                </motion.div>
                
                <motion.div
                  className="absolute bottom-8 right-8 bg-cta-orange/90 backdrop-blur-sm rounded-lg px-4 py-2 text-white text-sm font-medium"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  ✨ New features
                </motion.div>
              </div>
            ) : (
              // Actual Video (placeholder for now)
              <div className="absolute inset-0 bg-black flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="w-16 h-16 border-4 border-brand-teal border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p>Loading video...</p>
                  <p className="text-sm text-white/60 mt-2">
                    In a real implementation, this would be a YouTube embed or video player
                  </p>
                </div>
              </div>
            )}
            
            {/* Video Overlay Effects */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent pointer-events-none" />
          </div>

          {/* Video Stats */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <div className="text-center p-6 bg-card border border-border rounded-xl">
              <div className="text-3xl font-bold text-brand-blue mb-2">2M+</div>
              <div className="text-muted-foreground">Queries Processed</div>
            </div>
            <div className="text-center p-6 bg-card border border-border rounded-xl">
              <div className="text-3xl font-bold text-brand-teal mb-2">500+</div>
              <div className="text-muted-foreground">Enterprise Clients</div>
            </div>
            <div className="text-center p-6 bg-card border border-border rounded-xl">
              <div className="text-3xl font-bold text-cta-orange mb-2">99.9%</div>
              <div className="text-muted-foreground">Uptime Guarantee</div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
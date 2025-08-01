import { motion } from 'framer-motion'
import { MessageSquare, BarChart3, Zap, Shield, Brain, Sparkles } from 'lucide-react'
import { FeatureCard } from '../common'

const features = [
  {
    icon: MessageSquare,
    title: 'Natural Language Queries',
    description: 'Ask questions in plain English and get instant insights from your data without complex SQL or formulas.'
  },
  {
    icon: BarChart3,
    title: 'Real-time Analytics',
    description: 'Monitor your KPIs and metrics in real-time with dynamic dashboards that update automatically.'
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Get answers in seconds, not hours. Our AI processes complex queries instantly across massive datasets.'
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-level encryption and compliance with SOC 2, GDPR, and HIPAA standards for complete data protection.'
  },
  {
    icon: Brain,
    title: 'Smart Insights',
    description: 'AI automatically discovers patterns, anomalies, and trends in your data that you might have missed.'
  },
  {
    icon: Sparkles,
    title: 'Predictive Analytics',
    description: 'Forecast future trends and outcomes with advanced machine learning models built into every analysis.'
  }
]

export default function Features() {
  return (
    <section id="features" className="py-24 bg-surface-light dark:bg-surface-dark">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-text-primary dark:text-text-inverse mb-6">
            Why Choose{' '}
            <span className="bg-gradient-to-r from-brand-blue to-brand-teal bg-clip-text text-transparent">
              Jarvis Analyst
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Powerful features designed to transform how you interact with data. 
            No technical expertise required – just ask and get answers.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <FeatureCard {...feature} />
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          className="text-center mt-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <p className="text-lg text-muted-foreground mb-6">
            Ready to experience the future of data analytics?
          </p>
          <button className="bg-cta-orange hover:bg-cta-orange/90 text-white font-semibold px-8 py-4 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-xl">
            Start Your Free Trial
          </button>
        </motion.div>
      </div>
    </section>
  )
}
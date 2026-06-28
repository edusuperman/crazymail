import { createFileRoute } from "@tanstack/react-router";
import { Check, X, Zap, Shield, Clock, Globe, Mail, Users, Code, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const PRICING_TIERS = [
  {
    name: "Free",
    nameEn: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for quick, one-time use",
    descriptionEn: "Perfect for quick, one-time use",
    icon: <Mail className="w-6 h-6" />,
    features: [
      { text: "Instant temp email address", included: true },
      { text: "Receive emails in real-time", included: true },
      { text: "Multiple domain options", included: true },
      { text: "Email auto-deletes in hours", included: true },
      { text: "Basic support", included: true },
      { text: "Custom username", included: false },
      { text: "Extended retention (24h)", included: false },
      { text: "API access", included: false },
      { text: "Priority support", included: false },
    ],
    cta: "Get Started Free",
    ctaEn: "Get Started Free",
    popular: false,
    color: "from-blue-500 to-cyan-500",
  },
  {
    name: "Premium",
    nameEn: "Premium",
    price: "$4.99",
    period: "/month",
    description: "For power users who need more control",
    descriptionEn: "For power users who need more control",
    icon: <Zap className="w-6 h-6" />,
    features: [
      { text: "Everything in Free", included: true },
      { text: "Custom username selection", included: true },
      { text: "Extended 24-hour retention", included: true },
      { text: "Ad-free experience", included: true },
      { text: "Save up to 50 emails", included: true },
      { text: "Custom domain support", included: true },
      { text: "API access (100 req/day)", included: true },
      { text: "Priority email support", included: true },
      { text: "No rate limits", included: true },
    ],
    cta: "Upgrade to Premium",
    ctaEn: "Upgrade to Premium",
    popular: true,
    color: "from-purple-500 to-pink-500",
  },
  {
    name: "Enterprise",
    nameEn: "Enterprise",
    price: "$29.99",
    period: "/month",
    description: "For teams and businesses at scale",
    descriptionEn: "For teams and businesses at scale",
    icon: <Shield className="w-6 h-6" />,
    features: [
      { text: "Everything in Premium", included: true },
      { text: "Unlimited API access", included: true },
      { text: "Custom domain branding", included: true },
      { text: "Team management (10 seats)", included: true },
      { text: "Webhook integrations", included: true },
      { text: "90-day email retention", included: true },
      { text: "Dedicated account manager", included: true },
      { text: "SLA guarantee (99.9%)", included: true },
      { text: "White-label solution", included: true },
    ],
    cta: "Contact Sales",
    ctaEn: "Contact Sales",
    popular: false,
    color: "from-amber-500 to-orange-500",
  },
];

const FAQ_ITEMS = [
  {
    q: "Can I cancel my subscription anytime?",
    a: "Yes! You can cancel your Premium or Enterprise subscription at any time. Your access will continue until the end of your current billing period. No questions asked.",
  },
  {
    q: "What payment methods do you accept?",
    a: "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and cryptocurrency (Bitcoin, Ethereum) for maximum privacy.",
  },
  {
    q: "Is there a free trial for Premium?",
    a: "Yes! We offer a 7-day free trial for Premium. No credit card required to start. You can upgrade or downgrade at any time.",
  },
  {
    q: "What happens to my emails after retention period?",
    a: "All emails are permanently deleted after the retention period (hours for Free, 24h for Premium, 90 days for Enterprise). We never store your data beyond this period.",
  },
  {
    q: "Can I use my own domain?",
    a: "Premium users can use custom subdomains, while Enterprise users get full custom domain branding with DNS configuration support.",
  },
  {
    q: "Is there an API rate limit?",
    a: "Free: 10 requests/day. Premium: 100 requests/day. Enterprise: Unlimited. Rate limits reset at midnight UTC.",
  },
  {
    q: "Do you offer refunds?",
    a: "We offer a 30-day money-back guarantee for all paid plans. If you're not satisfied, contact our support team for a full refund.",
  },
  {
    q: "Can I upgrade from Premium to Enterprise?",
    a: "Absolutely! You can upgrade at any time. We'll prorate the difference and apply it to your next billing cycle.",
  },
];

const FEATURES_COMPARISON = [
  { feature: "Temp email address", free: true, premium: true, enterprise: true },
  { feature: "Real-time inbox", free: true, premium: true, enterprise: true },
  { feature: "Multiple domains", free: true, premium: true, enterprise: true },
  { feature: "Custom username", free: false, premium: true, enterprise: true },
  { feature: "Email retention", free: "Hours", premium: "24 hours", enterprise: "90 days" },
  { feature: "Saved emails", free: "0", premium: "50", enterprise: "Unlimited" },
  { feature: "API access", free: false, premium: "100/day", enterprise: "Unlimited" },
  { feature: "Custom domains", free: false, premium: "Subdomain", enterprise: "Full domain" },
  { feature: "Team seats", free: "1", premium: "1", enterprise: "10" },
  { feature: "Webhooks", free: false, premium: false, enterprise: true },
  { feature: "Ad-free", free: false, premium: true, enterprise: true },
  { feature: "Priority support", free: false, premium: true, enterprise: true },
  { feature: "SLA guarantee", free: false, premium: false, enterprise: "99.9%" },
  { feature: "White-label", free: false, premium: false, enterprise: true },
];

export const Route = createFileRoute("/pricing")({
  head: () => ({
    meta: [
      { title: "Pricing - TempMail Pro | Free & Premium Temporary Email" },
      { name: "description", content: "Choose the perfect plan for your temporary email needs. Free forever plan available. Premium features starting at $4.99/month." },
      { name: "keywords", content: "temp email pricing, disposable email plans, premium temporary email, burner mail subscription" },
      { property: "og:title", content: "Pricing - TempMail Pro" },
      { property: "og:description", content: "Choose the perfect plan for your temporary email needs. Free forever plan available." },
      { property: "og:type", content: "website" },
    ],
  }),
  component: PricingPage,
});

function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300 border-purple-500/30">
            <Star className="w-3 h-3 mr-1" />
            Simple, Transparent Pricing
          </Badge>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
            Choose Your{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Protection Level
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Start free, upgrade when you need more power. All plans include instant temp email generation and real-time inbox.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-20 px-4">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
          {PRICING_TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`relative rounded-2xl border ${
                tier.popular
                  ? "border-purple-500/50 shadow-lg shadow-purple-500/20"
                  : "border-gray-700/50"
              } bg-gray-800/50 backdrop-blur-sm overflow-hidden transition-all hover:scale-105`}
            >
              {tier.popular && (
                <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-4 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              
              <div className="p-8">
                {/* Icon & Name */}
                <div className="flex items-center gap-3 mb-4">
                  <div className={`p-2 rounded-lg bg-gradient-to-r ${tier.color} text-white`}>
                    {tier.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{tier.nameEn}</h3>
                    <p className="text-sm text-gray-400">{tier.descriptionEn}</p>
                  </div>
                </div>

                {/* Price */}
                <div className="mb-6">
                  <span className="text-4xl font-bold text-white">{tier.price}</span>
                  <span className="text-gray-400">{tier.period}</span>
                </div>

                {/* CTA */}
                <Button
                  className={`w-full mb-6 ${
                    tier.popular
                      ? "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                      : "bg-gray-700 hover:bg-gray-600"
                  }`}
                >
                  {tier.ctaEn}
                </Button>

                {/* Features */}
                <ul className="space-y-3">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      {feature.included ? (
                        <Check className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
                      ) : (
                        <X className="w-5 h-5 text-gray-600 shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? "text-gray-300" : "text-gray-600"}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="py-20 px-4 bg-gray-800/30">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Detailed Feature Comparison
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Feature</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Free</th>
                  <th className="text-center py-4 px-6 text-purple-400 font-medium">Premium</th>
                  <th className="text-center py-4 px-6 text-amber-400 font-medium">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {FEATURES_COMPARISON.map((item, i) => (
                  <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="py-4 px-6 text-gray-300">{item.feature}</td>
                    <td className="py-4 px-6 text-center">
                      {typeof item.free === "boolean" ? (
                        item.free ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <X className="w-5 h-5 text-gray-600 mx-auto" />
                        )
                      ) : (
                        <span className="text-gray-400">{item.free}</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-center">
                      {typeof item.premium === "boolean" ? (
                        item.premium ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <X className="w-5 h-5 text-gray-600 mx-auto" />
                        )
                      ) : (
                        <span className="text-purple-400 font-medium">{item.premium}</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-center">
                      {typeof item.enterprise === "boolean" ? (
                        item.enterprise ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <X className="w-5 h-5 text-gray-600 mx-auto" />
                        )
                      ) : (
                        <span className="text-amber-400 font-medium">{item.enterprise}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { icon: <Shield className="w-8 h-8 mx-auto mb-2 text-green-400" />, title: "Secure", desc: "End-to-end encryption" },
              { icon: <Clock className="w-8 h-8 mx-auto mb-2 text-blue-400" />, title: "Instant", desc: "5-second delivery" },
              { icon: <Globe className="w-8 h-8 mx-auto mb-2 text-purple-400" />, title: "Global", desc: "10+ domains available" },
              { icon: <Users className="w-8 h-8 mx-auto mb-2 text-amber-400" />, title: "Trusted", desc: "1M+ users worldwide" },
            ].map((badge, i) => (
              <div key={i}>
                {badge.icon}
                <h4 className="text-white font-semibold">{badge.title}</h4>
                <p className="text-sm text-gray-400">{badge.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4 bg-gray-800/30">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Frequently Asked Questions
          </h2>
          
          <Accordion type="single" collapsible className="w-full">
            {FAQ_ITEMS.map((item, i) => (
              <AccordionItem key={i} value={`item-${i}`} className="border-gray-700">
                <AccordionTrigger className="text-left text-white hover:text-purple-400">
                  {item.q}
                </AccordionTrigger>
                <AccordionContent className="text-gray-400">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Protect Your Privacy?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join over 1 million users who trust TempMail Pro for their temporary email needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              <Zap className="w-5 h-5 mr-2" />
              Start Free Trial
            </Button>
            <Button size="lg" variant="outline" className="border-gray-600 text-white hover:bg-gray-800">
              <Code className="w-5 h-5 mr-2" />
              View API Docs
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

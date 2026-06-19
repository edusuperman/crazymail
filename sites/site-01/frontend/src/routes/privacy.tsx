import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/privacy")({
  head: () => ({
    meta: [
      { title: "Privacy Policy - TempMails.top" },
      { name: "description", content: "Privacy Policy for TempMails.top temporary email service." },
      { name: "robots", content: "index, follow" },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/privacy" },
    ],
  }),
  component: PrivacyPage,
});

function PrivacyPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
      <p className="mt-2 text-sm text-muted-foreground">Last updated: June 19, 2026</p>

      <div className="prose prose-gray mt-8 space-y-6">
        <section>
          <h2 className="text-2xl font-semibold">1. Introduction</h2>
          <p>
            Welcome to TempMails.top ("we," "our," or "us"). We are committed to protecting your privacy.
            This Privacy Policy explains how we collect, use, and safeguard information when you use our
            temporary email service.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">2. Information We Collect</h2>
          <h3 className="text-xl font-medium mt-4">2.1 Information You Provide</h3>
          <p>
            We do not require registration or personal information to use our service. You may optionally
            provide a username for your temporary email address.
          </p>
          <h3 className="text-xl font-medium mt-4">2.2 Automatically Collected Information</h3>
          <p>
            We may automatically collect certain information when you visit our website, including:
          </p>
          <ul className="list-disc pl-6 mt-2">
            <li>IP address (for abuse prevention)</li>
            <li>Browser type and version</li>
            <li>Operating system</li>
            <li>Referring website</li>
            <li>Pages visited and time spent</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">3. How We Use Your Information</h2>
          <p>We use the collected information to:</p>
          <ul className="list-disc pl-6 mt-2">
            <li>Provide and maintain our temporary email service</li>
            <li>Prevent abuse and ensure service security</li>
            <li>Improve user experience</li>
            <li>Analyze usage patterns</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">4. Email Data</h2>
          <p>
            Temporary email addresses and their contents are automatically deleted after a short period
            (typically 10 minutes). We do not permanently store email content. However, we may temporarily
            process emails to deliver them to your browser.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">5. Cookies</h2>
          <p>
            We use essential cookies to maintain your session and preferences. We do not use tracking
            cookies or third-party advertising cookies.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">6. Third-Party Services</h2>
          <p>
            We may use third-party services for analytics and infrastructure. These services have their
            own privacy policies, and we encourage you to review them.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">7. Data Security</h2>
          <p>
            We implement reasonable security measures to protect your information. However, no method of
            transmission over the Internet is 100% secure.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">8. Children's Privacy</h2>
          <p>
            Our service is not intended for children under 13. We do not knowingly collect personal
            information from children.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">9. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of any changes by
            posting the new policy on this page.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">10. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy, please contact us at{" "}
            <a href="mailto:privacy@tempmails.top" className="text-primary underline">
              privacy@tempmails.top
            </a>
            .
          </p>
        </section>
      </div>
    </div>
  );
}

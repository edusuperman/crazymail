import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/terms")({
  head: () => ({
    meta: [
      { title: "Terms of Service - TempMails.top" },
      { name: "description", content: "Terms of Service for TempMails.top temporary email service." },
      { name: "robots", content: "index, follow" },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/terms" },
    ],
  }),
  component: TermsPage,
});

function TermsPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
      <p className="mt-2 text-sm text-muted-foreground">Last updated: June 19, 2026</p>

      <div className="prose prose-gray mt-8 space-y-6">
        <section>
          <h2 className="text-2xl font-semibold">1. Acceptance of Terms</h2>
          <p>
            By accessing or using TempMails.top ("the Service"), you agree to be bound by these Terms of
            Service. If you do not agree to these terms, please do not use the Service.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">2. Description of Service</h2>
          <p>
            TempMails.top provides temporary, disposable email addresses for privacy protection. The Service
            allows users to receive emails without revealing their real email addresses.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">3. User Responsibilities</h2>
          <p>You agree to:</p>
          <ul className="list-disc pl-6 mt-2">
            <li>Use the Service only for lawful purposes</li>
            <li>Not use the Service for spam, fraud, or abuse</li>
            <li>Not attempt to disrupt or overload the Service</li>
            <li>Not use the Service to violate any laws or regulations</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">4. Service Limitations</h2>
          <p>
            The Service is provided "as is" without warranties of any kind. We do not guarantee:
          </p>
          <ul className="list-disc pl-6 mt-2">
            <li>Uninterrupted or error-free service</li>
            <li>Delivery of all emails</li>
            <li>Permanent storage of emails</li>
            <li>Compatibility with all websites or services</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">5. Email Retention</h2>
          <p>
            Temporary emails are automatically deleted after a short period (typically 10 minutes).
            We are not responsible for any loss of data or missed communications.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">6. Intellectual Property</h2>
          <p>
            The Service and its original content, features, and functionality are owned by TempMails.top
            and are protected by international copyright, trademark, and other intellectual property laws.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">7. Limitation of Liability</h2>
          <p>
            In no event shall TempMails.top be liable for any indirect, incidental, special,
            consequential, or punitive damages arising out of or related to your use of the Service.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">8. Indemnification</h2>
          <p>
            You agree to indemnify and hold harmless TempMails.top and its officers, directors,
            employees, and agents from any claims, damages, or expenses arising from your use of the Service.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">9. Termination</h2>
          <p>
            We may terminate or suspend your access to the Service immediately, without prior notice,
            for any reason, including breach of these Terms.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">10. Changes to Terms</h2>
          <p>
            We reserve the right to modify these Terms at any time. We will notify users of any material
            changes by posting the new Terms on this page.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold">11. Contact Us</h2>
          <p>
            If you have questions about these Terms, please contact us at{" "}
            <a href="mailto:terms@tempmails.top" className="text-primary underline">
              terms@tempmails.top
            </a>
            .
          </p>
        </section>
      </div>
    </div>
  );
}

import type { Metadata } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://tempmailpro.com";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "Learn how TempMail Pro protects your privacy. We do not collect personal information. Temporary emails are stored briefly and auto-deleted.",
  alternates: {
    canonical: `${siteUrl}/privacy`,
  },
  openGraph: {
    title: "Privacy Policy | TempMail Pro",
    description:
      "Learn how TempMail Pro protects your privacy. We do not collect personal information.",
    type: "website",
    url: `${siteUrl}/privacy`,
  },
};

export default function PrivacyPolicy() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: "Privacy Policy",
    description:
      "Privacy policy for TempMail Pro temporary email service.",
    url: `${siteUrl}/privacy`,
    datePublished: "2026-06-12",
    dateModified: "2026-06-12",
    publisher: {
      "@type": "Organization",
      name: "TempMail Pro",
      url: siteUrl,
    },
    mainEntity: {
      "@type": "WebApplication",
      name: "TempMail Pro",
      url: siteUrl,
      applicationCategory: "UtilitiesApplication",
      operatingSystem: "Web",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main className="max-w-3xl mx-auto px-4 py-16 text-slate-300">
        <h1 className="text-3xl font-bold text-white mb-8">Privacy Policy</h1>
        <p className="text-sm text-slate-500 mb-8">
          Last updated: June 12, 2026
        </p>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            1. Data Collection
          </h2>
          <p className="mb-4">
            TempMail Pro is designed with privacy at its core. We do{" "}
            <strong className="text-white">not</strong> collect any personal
            information such as names, real email addresses, phone numbers, or
            IP addresses for tracking purposes.
          </p>
          <p>
            The only data we process is the temporary email address you
            generate, which is stored temporarily to deliver your messages.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            2. Email Storage & Retention
          </h2>
          <p className="mb-4">
            Emails received by your temporary address are stored on our servers
            for a limited period (typically 10 minutes). After this period, both
            the email address and all associated messages are automatically and
            permanently deleted.
          </p>
          <p>
            You may manually delete individual messages at any time before the
            automatic expiration.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            3. Cookies
          </h2>
          <p className="mb-4">
            TempMail Pro uses only essential cookies required for the
            application to function correctly (e.g., session management). We do
            not use advertising or tracking cookies.
          </p>
          <p>
            No third-party analytics scripts (such as Google Analytics) are
            loaded on our pages.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            4. Third-Party Services
          </h2>
          <p className="mb-4">
            We use third-party email providers to generate and receive
            temporary emails. These providers have their own privacy policies,
            and we encourage you to review them.
          </p>
          <p>
            We do not share any user data with advertisers, data brokers, or
            other third parties for marketing purposes.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            5. Security
          </h2>
          <p>
            All data is transmitted over HTTPS. We implement industry-standard
            security measures to protect the temporary data stored on our
            servers during its brief retention period.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            6. Children&apos;s Privacy
          </h2>
          <p>
            TempMail Pro is not directed at children under 13. We do not
            knowingly collect information from children.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            7. Changes to This Policy
          </h2>
          <p>
            We may update this privacy policy from time to time. Changes will
            be posted on this page with an updated revision date.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-white mb-4">
            8. Contact Us
          </h2>
          <p>
            If you have questions about this privacy policy, please contact us
            at{" "}
            <a
              href="mailto:privacy@tempmailpro.com"
              className="text-cyan-400 hover:text-cyan-300 underline"
            >
              privacy@tempmailpro.com
            </a>
            .
          </p>
        </section>

        <footer className="mt-12 pt-8 border-t border-slate-700 text-sm text-slate-500">
          <p>
            Published by TempMail Pro Team. This policy is effective as of June
            12, 2026.
          </p>
        </footer>
      </main>
    </>
  );
}

import { createFileRoute } from "@tanstack/react-router";
import { Code, Copy, Check, Lock, Zap, Globe, BookOpen, Terminal, Key, Server } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState, useCallback } from "react";

const ENDPOINTS = [
  { method: "POST", path: "/v1/mailbox", desc: "Create a new temporary mailbox" },
  { method: "GET", path: "/v1/mailbox/{id}/messages", desc: "Get all messages" },
  { method: "GET", path: "/v1/domains", desc: "List available domains" },
  { method: "DELETE", path: "/v1/mailbox/{id}", desc: "Delete a mailbox" },
];

export const Route = createFileRoute("/api-docs")({
  head: () => ({
    meta: [
      { title: "API Documentation - TempMail Pro" },
      { name: "description", content: "RESTful API for temporary email services." },
    ],
  }),
  component: ApiDocsPage,
});

function ApiDocsPage() {
  const [copied, setCopied] = useState(false);
  const sampleCode = "# Create a mailbox\ncurl -X POST https://api.tempmails.top/v1/mailbox";

  const copy = useCallback(() => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(sampleCode);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [sampleCode]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      <section className="pt-20 pb-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <Badge className="mb-4 bg-blue-500/20 text-blue-300 border-blue-500/30">
            <Code className="w-3 h-3 mr-1" /> RESTful API
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            API <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Documentation</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
            Integrate temporary email into your apps. Create mailboxes, retrieve messages, manage emails programmatically.
          </p>
          <Button size="lg" className="bg-gradient-to-r from-blue-500 to-cyan-500">
            <Key className="w-5 h-5 mr-2" /> Get API Key
          </Button>
        </div>
      </section>

      <section className="pb-16 px-4">
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-6">
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
            <Server className="w-6 h-6 text-blue-400 mb-2" />
            <h3 className="text-white font-semibold">Base URL</h3>
            <p className="text-gray-400 font-mono text-sm mt-1">https://api.tempmails.top/v1</p>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
            <Lock className="w-6 h-6 text-green-400 mb-2" />
            <h3 className="text-white font-semibold">Authentication</h3>
            <p className="text-gray-400 font-mono text-sm mt-1">Bearer Token</p>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
            <Zap className="w-6 h-6 text-amber-400 mb-2" />
            <h3 className="text-white font-semibold">Rate Limit</h3>
            <p className="text-gray-400 font-mono text-sm mt-1">100 req/day</p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-gray-800/30">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-8">Quick Start</h2>
          <div className="relative">
            <pre className="bg-gray-900 rounded-xl p-6 overflow-x-auto border border-gray-700">
              <code className="text-sm text-gray-300 font-mono whitespace-pre">{sampleCode}</code>
            </pre>
            <Button size="sm" variant="ghost" className="absolute top-4 right-4" onClick={copy}>
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Endpoints</h2>
          <div className="space-y-4">
            {ENDPOINTS.map((ep, i) => (
              <div key={i} className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                <div className="flex items-center gap-3">
                  <Badge className="font-mono bg-blue-500/20 text-blue-400">{ep.method}</Badge>
                  <code className="text-white font-mono">{ep.path}</code>
                  <span className="text-gray-400">{ep.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-gray-800/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to Build?</h2>
          <p className="text-xl text-gray-400 mb-8">Get your API key and start integrating today.</p>
          <Button size="lg" className="bg-gradient-to-r from-blue-500 to-cyan-500">
            <Key className="w-5 h-5 mr-2" /> Generate API Key
          </Button>
        </div>
      </section>
    </div>
  );
}

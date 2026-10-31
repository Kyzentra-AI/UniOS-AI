
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FaLinkedinIn,
  FaInstagram,
} from "react-icons/fa";
import {
  Globe,
  Mail,
  ArrowUpRight,
} from "lucide-react";
import Image from "next/image";
import { useTheme } from '@/components/providers/ThemeProvider';

const productLinks = [
  { label: "AI Roadmaps", href: "/roadmap" },
  { label: "Internship Hub", href: "/internships" },
  { label: "Lab Workspace", href: "/build" },
];

const companyLinks = [
  { label: "About Us", href: "/about" },
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Service", href: "/terms" },
];

const socialLinks = [
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/company/kyzentra-ai/",
    icon: FaLinkedinIn,
  },
  {
    label: "Instagram",
    href: "https://www.instagram.com/kyzentra_ai?dlrf=eHZvcjJ4Zzd5bHhy",
    icon: FaInstagram,
  },
  {
    label: "Company Website",
    href: "https://kyzentra.in",
    icon: Globe,
  },
];


export default function Footer() {
  const pathname = usePathname();
  const { theme } = useTheme();

  // Hide footer on onboarding pages
  if (pathname?.startsWith("/onboarding")) {
    return null;
  }

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--background)] text-[var(--foreground)]">
      <div className="mx-auto max-w-7xl px-6 py-14 lg:px-10">

        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">

          {/* Brand Section */}
          <div className="lg:col-span-2">

            <Link href="/" className="inline-flex items-center">
              <Image
                src={theme === "dark" ? "/logo1.png" : "/logo.png"}
                alt="UniOS.AI"
                width={120}
                height={150}
                priority
                className="h-16 w-auto"
              />
            </Link>

            <p className="mt-5 max-w-md text-sm leading-7 text-[var(--text-secondary)]">
              An intelligent learning ecosystem designed to help students
              learn better, build real-world skills, compete with confidence,
              and launch their careers.
            </p>

            <p className="mt-3 text-sm font-semibold text-[var(--text-primary)]">
              Your Learning. Your Growth. Your Future.
            </p>

            {/* Social Media Icons */}
            <div className="mt-7 flex items-center gap-3">
              {socialLinks.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  title={label}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)] transition-all duration-200 hover:-translate-y-1 hover:border-[var(--feature-orange)] hover:bg-[var(--primary)] hover:text-white"
                >
                  <Icon size={18} />
                </a>
              ))}
            </div>

            {/* Contact */}
            <a
              href="mailto:support@kyzentra.in"
              className="mt-5 inline-flex items-center gap-2 text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--feature-orange)]"
            >
              <Mail size={15} />
              support@kyzentra.in
            </a>
          </div>

          {/* Platform Links */}
          <div>
            <h3 className="mb-5 text-sm font-bold uppercase tracking-[0.15em] text-[var(--primary)]">
              Platform
            </h3>

            <ul className="space-y-4">
              {productLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--feature-orange)]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="mb-5 text-sm font-bold uppercase tracking-[0.15em] text-[var(--primary)]">
              Company
            </h3>

            <ul className="space-y-4">
              {companyLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--feature-orange)]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 flex flex-col gap-4 border-t border-[var(--border)] pt-6 text-xs text-[var(--text-muted)] sm:flex-row sm:items-center sm:justify-between">

          <p>
            © {new Date().getFullYear()} Kyzentra.AI Private Limited.
            All rights reserved.
          </p>

          <a
            href="https://kyzentra.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 transition-colors hover:text-[var(--feature-orange)]"
          >
            Developed by Kyzentra.AI
            <ArrowUpRight size={13} />
          </a>

        </div>
      </div>
    </footer>
  );
}
